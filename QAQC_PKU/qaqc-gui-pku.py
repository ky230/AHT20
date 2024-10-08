#!/usr/bin/env python3
"""
GUI for controlling the Caltech BTL QA/QC jig.

Author: Anthony LaTorre
Last Updated: Jan 24, 2023
"""
USE_TTi = False
USE_CHILLER = False

import glob
from btl import Client
import tkinter as tk
from tkinter import ttk
import random
from os.path import join, expanduser, exists, splitext
import os
import json
from subprocess import Popen, PIPE
import subprocess
import os
import h5py
import sys
import time
import signal


# 用于存储AHT20.py进程的全局变量
aht20_process = None



if USE_TTi:
   sys.path.append('/home/pkumtd/TXP3510P')
   from TXP3510PWrapper import TXP3510P
   
WAVEDUMP_PROGRAM = 'wavedump'
INTEGRATE_WAVEFORMS_PROGRAM = 'integrate-waveforms'
ANALYZE_WAVEFORMS_PROGRAM = 'analyze-waveforms'

# Debug mode. Right now this just controls whether we draw random numbers for
# polling.
DEBUG = False

# Assembly centers. This should be synchronized with the SQL file at
# ../website/btl_qa.sql.
ASSEMBLY_CENTERS = [
    "Caltech",
    "UVA",
    "Milano",
    "CERN",
    "Peking"
]

NUMBER_OF_BOARDS = [str(i) for i in range(1,5)]

BOARD_ADDRESSES = {
    0: [0,1],
    1: [2,3],
    2: [4,5],
    3: [6,7],
}

RELAYS = [0,1,2,3,4,5]

# Stepper motor
dLcm_perstep = 0.005 # distance per step, configurable in gui pannel (stepper_dLperstep)
dLcm_intermodule = 5.34 # distance between two modules on the same module board
dLcm_interboard = 7.76 # distance between two modules from two neighbouring module boards

step_lastposition = 0
out = Popen(['cat','/home/pkumtd/qaqc_jig/.step_lastposition'],stdout=subprocess.PIPE)
step_lastposition = int(out.stdout.read().decode().rstrip())

def filename_template(data_path='./', barcode=None, label=None):
    if not exists(data_path) and data_path != '':
        os.makedirs(data_path)
    if label != None and label != '':
       label = '_'+label
    else:
       label = ''
    return join(data_path, 'module_%i%s' % (int(barcode), str(label) ))

def print_warning(msg):
    start = entry.index(tk.INSERT)
    if not msg.endswith('\n'):
        msg += '\n'
    entry.insert(tk.END,msg)
    entry.yview(tk.END)
    entry.update()
    stop = entry.index(tk.INSERT)
    entry.tag_add("error",start,stop)

def run_command(cmd, progress_bar=None):
    global stop
    stop = False
    stop_button['state'] = tk.NORMAL
    stop_button.update()
    entry.insert(tk.END, " ".join(map(str,cmd)) + '\n')
    p = Popen(['stdbuf','-o0'] + list(map(str,cmd)), stdout=PIPE, stderr=PIPE)
    for line in iter(p.stdout.readline, b''):
        print(line.decode().rstrip('\n'))
        if progress_bar is not None:
            try:
                i, length = map(float,line.decode().split("/"))
                progress_bars[progress_bar]['value'] = i*100/length
            except Exception as e:
                pass
        entry.insert(tk.END,line)
        entry.yview(tk.END)
        entry.update()

        if stop:
            p.terminate()
            stop = False
    p.wait()
    if p.returncode != 0:
        print_warning(p.stderr.read().decode())
    stop_button['state'] = tk.DISABLED
    stop_button.update()
    return p.returncode

def save(filename=None):
    """
    Save the GUI state from the json file specified by `filename`.
    """
    if filename is None:
        filename = join(expanduser("~"),".qaqc_gui.settings")
    data = {}
    data['assembly_center'] = assembly_center.get()
    data['n_boards'] = int(n_boards_var.get())
    data['barcodes'] = [barcode.get() for barcode in barcodes]
    data['module_available'] = [available.get() for available in module_available]
    data['ov'] = ov.get()
    data['trigger'] = trigger.get()
    data['vbds'] = [vbd.get() for vbd in vbds]
    data['data_path'] = data_path.get()
    data['label'] = label.get()
    data['ip_address'] = ip_address.get()
    data['stepper_enable'] = stepper_enable.get()
    data['stepper_dLperstep'] = stepper_dLperstep.get()
    data['n_spe_events'] = n_spe_events.get()
    data['n_source_events'] = n_source_events.get()
    print("Saving GUI state into '%s'" % filename)
    with open(filename,'w') as f:
        json.dump(data,f)

def load(filename=None):
    """
    Load the GUI state from the json file specified by `filename`.
    """
    if filename is None:
        filename = join(expanduser("~"),".qaqc_gui.settings")
    print("Loading GUI state from '%s'" % filename)
    if exists(filename):
        with open(filename,'r') as f:
            data = json.load(f)
        if 'assembly_center' in data:
            assembly_center.set(data['assembly_center'])
        if 'n_boards' in data:
            n_boards_var.set(str(data['n_boards']))
        if 'barcodes' in data:
            for i, barcode in enumerate(data['barcodes']):
                barcodes[i].set(barcode)
        if 'module_available' in data:
            for i, available in enumerate(data['module_available']):
                module_available[i].set(available)
        if 'ov' in data:
            ov.set(data['ov'])
        if 'trigger' in data:
            trigger.set(data['trigger'])
        if 'vbds' in data:
            for i, vbd in enumerate(data['vbds']):
                vbds[i].set(vbd)
        if 'data_path' in data:
            data_path.set(data['data_path'])            
        if 'label' in data:
            label.set(data['label'])            
        if 'ip_address' in data:
            ip_address.set(data['ip_address'])
        if 'stepper_enable' in data:
            stepper_enable.set(data['stepper_enable'])
        if 'stepper_dLperstep' in data:
            stepper_dLperstep.set(data['stepper_dLperstep'])
        if 'n_spe_events' in data:
            n_spe_events.set(data['n_spe_events'])
        if 'n_source_events' in data:
            n_source_events.set(data['n_source_events'])
        n_boards_changed()

def on_closing():
    """
    Function to run before the window is closed. Right now we just save the GUI
    state and then quit the program.
   """  #关闭GUI并终止AHT20.py进程
    save()
    root.destroy()




def query(client, cmd, timeout=10):
    entry.insert(tk.END, "%s\n" % cmd)
    entry.yview(tk.END)
    entry.update()
    if not DEBUG:
        return client.query(cmd, timeout)

def hv_off(client):
    n_boards = int(n_boards_var.get())

    try:
        query(client, "disable_hv")
    except Exception as e:
        print_warning(str(e))

    # First, make sure all the HV relays are off
    for i in range(n_boards):
        for bus in BOARD_ADDRESSES[i]:
            for k in RELAYS:
                try:
                    query(client, "hv_write %i %i off" % (bus, k))
                except Exception as e:
                    print_warning(str(e))

STOP = False

def stop():
    global stop
    stop = True

def reanalyze_data():
    # Make sure they entered the barcodes first.
    for i in range(12):
        if not module_available[i].get():
            continue

        barcode = barcodes[i].get()
        if barcode == '':
            print_warning('Need to enter a barcode for module %i\n' % i)
            return

        progress_bars[i]['value'] = 0

    # Now, we analyze all the data
    for i in range(12):
        if not module_available[i].get():
            entry.insert(tk.END, "Skipping module %i\n" % i)
            continue

        barcode = barcodes[i].get()
        if barcode == '':
            print_warning('Need to enter a barcode for module %i\n' % i)
            return

        try:
            filename = filename_template(data_path=data_path.get(), barcode=barcode, label=label.get())+'.hdf5'
        except:
            print_warning("Not a valid data path: %s\n" % data_path.get())
            return

        entry.insert(tk.END, "Integrating data for module %i\n" % int(barcode))
        entry.yview(tk.END)
        entry.update()

        root, ext = splitext(filename)
        out_filename = "%s_integrals.hdf5" % root
        cmd = [INTEGRATE_WAVEFORMS_PROGRAM,filename,'-o', out_filename]
        
        if run_command(cmd,progress_bar=i):
            module_status[i].config(text="Failed integration")
            continue

        module_status[i].config(text="Integration successful!")

def power_on():
    """
    Function to power on the board power supply
    """
    
    mytti1 = TXP3510P('/dev/TTi-1')
    mytti1.setCurrent(2.)
    mytti1.setVoltage(5.3)
    mytti1.powerOn()
    mytti2 = TXP3510P('/dev/TTi-2')
    mytti2.setCurrent(1.,1)
    mytti2.setVoltage(12.,1)
    mytti2.powerOn(1)
    mytti2.setCurrent(1.,2)
    mytti2.setVoltage(12.,2)
    mytti2.powerOn(2)
    
    power_on_button['state'] = tk.DISABLED
    power_off_button['state'] = tk.NORMAL

def power_off():
    """
    Function to power off the board power supply
    """
    
    mytti1 = TXP3510P('/dev/TTi-1')
    mytti1.powerOff()
    mytti2 = TXP3510P('/dev/TTi-2')
    mytti2.powerOff(1)
    mytti2.powerOff(2)
    
    power_on_button['state'] = tk.NORMAL
    power_off_button['state'] = tk.DISABLED

def chiller_on():
    """
    Function to turn on the chiller
    """
    
    proc = Popen(['python3','/home/pkumtd/qaqc_jig/python/utilities/setBoxTemp_PID.py','--target','%f'%(float(chiller_temp_entry.get()))])
    chiller_pid = proc.pid
    os.system('echo %d >> /home/cmsdaq/.setBoxTemp_PID.pid'%chiller_pid)
    chiller_on_button.config(text='Chiller is on (PID: %d)'%chiller_pid)
    
    chiller_on_button['state'] = tk.DISABLED
    chiller_off_button['state'] = tk.NORMAL

def chiller_off():
    """
    Function to turn off the chiller
    """
    
    out = Popen(['cat','/home/cmsdaq/.setBoxTemp_PID.pid'],stdout=subprocess.PIPE)
    chiller_pid = int(out.stdout.read().decode().rstrip())
    os.system('kill -9 %d'%chiller_pid)
    os.system('rm /home/cmsdaq/.setBoxTemp_PID.pid')
    out = Popen(['/home/pkumtd/LAUDAChiller/driveChiller.py', '--power-off'],stdout=subprocess.PIPE)
    
    chiller_on_button.config(text='Chiller on')
    chiller_on_button['state'] = tk.NORMAL
    chiller_off_button['state'] = tk.DISABLED

# Setup module positions for stepper motor
dLcm_perstep= 0.005 # default=0.005
nstep_intermodule = dLcm_intermodule/dLcm_perstep
nstep_interboard = dLcm_interboard/dLcm_perstep
list_nstep= [ 0,                 # board 0, module 0
              nstep_intermodule, # board 0, module 1
              nstep_intermodule, # board 0, module 2
              nstep_interboard,  # board 1, module 0
              nstep_intermodule, # board 1, module 1
              nstep_intermodule, # board 1, module 2
              nstep_interboard,  # board 2, module 0
              nstep_intermodule, # board 2, module 1
              nstep_intermodule, # board 2, module 2
              nstep_interboard,  # board 3, module 0
              nstep_intermodule, # board 3, module 1
              nstep_intermodule, # board 3, module 2
]

def take_data():
   """
   Function to take single PE and 511 keV data for all the modules marked
   present in the GUI. First, we move the stepper motor, then take single PE
   data, then 511 data, and finally analyze it
   """
   
   # Clear error messages
   entry.delete(1.0,tk.END)
   
   dLcm_perstep= float(stepper_dLperstep.get()) # default=0.005
   
   n_boards = int(n_boards_var.get())
   
   
   # Make sure they entered the barcodes first.
   for i in range(12):
      if not module_available[i].get():
         continue

      barcode = barcodes[i].get()
      if barcode == '':
         print_warning('Need to enter a barcode for module %i\n' % i)
         return

      progress_bars[i]['value'] = 0
      module_status[i].config(text="-")

   client = Client(ip_address.get())
    
   # Increment the run number
   run = -1
   with open('/home/pkumtd/qaqc_jig/.last_run') as f:
      runs = [int(x) for x in next(f).split()]
      run = str(runs[0]+1)
      os.remove('/home/pkumtd/qaqc_jig/.last_run')
      with open('/home/pkumtd/qaqc_jig/.last_run','w+') as f:
         f.write(run)
   run_path = data_path.get() + '/run%04d'%int(run)
   if not exists(run_path) and run_path != '':
      os.makedirs(run_path)
   
   # Store the GUI config
   try:
      save(run_path+'/qaqc_gui.settings')
   except:
      print_warning("Not a valid data path: %s\n" % run_path)
      return
   
   # First, we try to get the stepper to the home position
   #
   # Techicalities: Command 'step_home' may take second or up to minutes for moving to home depending on its last position.
   #                Teensy can sucessfully send back a return packet to PC for the completion of this operation.
   #                But due to the long waiting time, the actual udp packet are often missed in the udp recvform() buffer of the PC.
   # Workaround: Ignore the timeout and the return packet of 'step_home'.
   #             Start a loop to read the value of stp_home pin on teensy.
   #             If stp_home is LOW, then the home position is reached.
   #             One more thing, we need to clear up the udp recvfrom() buffer at PC,
   #             since the above operations have overlooked at least one packet,
   #             and this leftover misaligns later communication.
   if stepper_enable.get():
      out = Popen(['cat','/home/pkumtd/qaqc_jig/.step_lastposition'],stdout=subprocess.PIPE)
      step_lastposition = int(out.stdout.read().decode().rstrip())
      os.system('echo %d > /home/pkumtd/qaqc_jig/.step_lastposition'%step_lastposition)
      
   # Next, we take the single PE data
   try:
      query(client, "set_attenuation off")
   except Exception as e:
      print_warning(str(e))
      return
   
   # First, make sure all the HV relays are off
   hv_off(client)
   
   # Now, we turn them on one by one and take data
   for i in range(12):
      
      if not module_available[i].get():
         entry.insert(tk.END, "Skipping module %i\n" % i)
         continue
        
      barcode = barcodes[i].get()
      if barcode == '':
         print_warning('Need to enter a barcode for module %i\n' % i)
         return
        
      vbd = vbds[i].get()
      if vbd == '':
         print_warning('Need to enter a Vbd for module %i\n' % i)
         return
      
      hv = float(vbd)+float(ov.get())
      print('Setting absolute bias voltage %.2f for module %i\n' %(hv,i) )
      
      try:
         filename = filename_template(data_path=run_path, barcode=barcode, label=label.get())+'.hdf5'
      except:
         print_warning("Not a valid data path: %s\n" % run_path)
         return
      
      if exists(filename):
         print("deleting %s" % filename)
         os.unlink(filename)
      
      # Move the stepper motor to the position of the module
      if stepper_enable.get():
         step_module(i)
         
      # Loop over first 8 channels and second eight channels
      for j in range(2):
         # Diagram to help figure out what's going on. It's drawn as if you
         # are looking top down at the modules plugged in:
         #
         #     Bus HV1 HV2 Module Bus HV1 HV2
         #     --- --- --- ------ --- --- ---
         #      2   0   1     5    3   4   5
         #      2   2   3     4    3   2   3
         #      2   4   5     3    3   0   1
         #
         #      0   0   1     2    1   4   5
         #      0   2   3     1    1   2   3
         #      0   4   5     0    1   0   1
         
         # Loop over left and right sides
         for k in range(2):
            bus = (i//3)*2 + k
            relay = (i % 3)*2 + j
            
            if k == 0:
               # Ordering for the board on left side is backwards from the
               # board on the right side
               relay = 5 - relay
                  
            try:
               query(client, "hv_write %i %i on" % (bus, relay))
            except Exception as e:
               print_warning(str(e))
               return
            
         try:
            query(client, "set_hv %.2f" % hv )
         except Exception as e:
            print_warning(str(e))
            return
            
         # Turn the attenuation off to take SPE data
         try:
            query(client, "set_attenuation off")
         except Exception as e:
            print_warning(str(e))
            return
         
         entry.insert(tk.END, 'Taking spe events for module %d (%d/2)\n'%(i,j+1))
         entry.yview(tk.END)
         entry.update()
         module_status[i].config(text="Taking spe data (%d/2)"%(j+1))
         if run_command([WAVEDUMP_PROGRAM,'-t','software','-l','spe','--channel-map',j % 2,'-n',n_spe_events.get(),'-o',filename], progress_bar=i):
         #if run_command([WAVEDUMP_PROGRAM,'-t','external','-l','spe','--channel-map',j % 2,'-n',n_spe_events.get(),'-o',filename], progress_bar=i):
         #if run_command([WAVEDUMP_PROGRAM,'-t','self','-l','spe','--channel-map',j % 2,'-n',n_spe_events.get(),'-o',filename,'--threshold',-0.05], progress_bar=i):
            hv_off(client)
            return
         
         # Turn the attenuation on to take source data
         try:
            query(client, "set_attenuation on")
         except Exception as e:
            print_warning(str(e))
            return
         
         try:
            voltage = query(client, "extmon_vread")
         except Exception as e:
            print_warning(str(e))
            return
         
         entry.insert(tk.END, 'Taking lyso events for module %d (%d/2)\n'%(i,j+1))
         entry.yview(tk.END)
         entry.update()
         module_status[i].config(text="Taking lyso data (%d/2)"%(j+1))
         cmd = [WAVEDUMP_PROGRAM,'-t','self','-l','lyso','--channel-map',j % 2,'-n',n_source_events.get(),'-o',filename,'--threshold',trigger.get()]
         print_warning(" ".join(str(c) for c in cmd))
         if run_command(cmd, progress_bar=i):
            hv_off(client)
            return
         
         try:
            query(client, "disable_hv")
         except Exception as e:
            print_warning(str(e))
            return
         
         # Loop over left and right sides
         for k in range(2):
            bus = (i//3)*2 + k
            relay = (i % 3)*2 + j
            
            if k == 0:
               # Ordering for the board on left side is backwards from the
               # board on the right side
               relay = 5 - relay
               
            try:
               query(client, "hv_write %i %i off" % (bus, relay))
            except Exception as e:
               print_warning(str(e))
               return
         
      info = poll_single_module(client,i)
      
      with h5py.File(filename,"a") as f:
         for key, value in info.items():
            f.attrs[key] = value
         f.attrs['barcode'] = barcode
         f.attrs['voltage'] = voltage
         f.attrs['institution'] = assembly_center.get()
      
      module_status[i].config(text="Data taking done")
      
      # Analyze data now
      filename = filename_template(data_path=run_path, barcode=barcode, label=label.get())+'.hdf5'
      
      entry.insert(tk.END, "Integrating data for module %i\n" % int(barcode))
      entry.yview(tk.END)
      entry.update()
      
      root, ext = splitext(filename)
      out_filename = "%s_integrals.hdf5" % root
      cmd = [INTEGRATE_WAVEFORMS_PROGRAM,filename,'-o', out_filename]
        
      if run_command(cmd,progress_bar=i):
         module_status[i].config(text="Failed integration")
         continue
      
      module_status[i].config(text="Integration successful!")
      
      filename = filename_template(data_path=run_path, barcode=barcode, label=label.get())+'_integrals.hdf5'
      
      entry.insert(tk.END, "Analyzing data for module %i\n" % int(barcode))
      entry.yview(tk.END)
      entry.update()
      
      out_filename = "%s_analysis.root" % root
      cmd = [ANALYZE_WAVEFORMS_PROGRAM,'-o',out_filename,'--slot',i,'--sourceType','cesium','--print-pdfs','/var/www/html/',filename]
      
      if run_command(cmd,progress_bar=i):
         module_status[i].config(text="Failed analysis")
         continue
      
      module_status[i].config(text="Analysis successful!")

   # Send the stepper back to the home position that takes a while
   # See above explaination of this operation




def poll_single_module(client, module):
    values = {}
    # Loop over left and right sides
    for k in range(2):
        # Diagram to help figure out what's going on. It's drawn as if you
        # are looking top down at the modules plugged in:
        #
        #     Bus Thermistor Module Bus Thermistor
        #     --- ---------- ------ --- ----------
        #      2      0         5    3      2
        #      2      1         4    3      1
        #      2      2         3    3      0
        #
        #      0      0         2    1      2
        #      0      1         1    1      1
        #      0      2         0    1      0
        bus = (module//3)*2 + k
        thermistor = module % 3

        if k == 0:
            # Ordering for the board on left side is backwards from the
            # board on the right side
            thermistor = 2 - thermistor

        key = '_a' if k == 0 else '_b'

        try:
            thermistor_value = query(client, "thermistor_read %i %i" % (bus, thermistor))
            if DEBUG:
                thermistor_value = random.uniform(20,30)
        except Exception as e:
            print_warning(str(e))
            return

        try:
            # TECs are numbered backwards from thermistors
            tec_value = query(client, "tec_check %i %i" % (bus, 2-thermistor))
            if DEBUG:
                tec_value = random.uniform(7,10)
        except Exception as e:
            print_warning(str(e))
            return

        values['temp%s' % key] = thermistor_value
        values['tec%s' % key] = tec_value

    return values

def poll():
    """
    Read all the thermistor temperatures and the TEC resistance.
    """
    # Clear error messages
    entry.delete(1.0,tk.END)

    client = Client(ip_address.get())

    for i in range(12):
        if not module_available[i].get():
            print("Skipping module %i" % i)
            for k in range(2):
                bus = (i//3)*2 + k
                thermistor = i % 3
                if k % 2 == 0:
                    thermistor_text[(i,'temp_a')].config(text="")
                    thermistor_text[(i,'tec_a')].config(text="")
                else:
                    thermistor_text[(i,'temp_b')].config(text="")
                    thermistor_text[(i,'tec_b')].config(text="")
            continue

        values = poll_single_module(client, i)

        if values is None:
            return

        for key, value in values.items():
            print("i, key = ", i, key)
            print("value = ", value)
            thermistor_text[(i,key)].config(text="%.2f" % value)





# def read_dht22():
#     out = Popen(['ssh', 'cmsdaq@raspcmsroma01', 'tail', '-n 1', '/home/cmsdaq/SHT40/temp.txt'],stdout=PIPE)
#     vals = (out.stdout.read().decode('utf-8')).split(',')
#     for i in range(1):
#         dht22_text[(i,'temp')].config(text="%.1f"%float(vals[0+0+2*i]))
#         dht22_text[(i,'hum')].config(text="%.1f"%float(vals[0+1+2*i]))
#     root.after(3000,read_dht22)



########

def read_AHT20():
    """读取最新的 AHT20 数据并更新GUI"""
    # 获取最新的 .txt 文件
    file_path = max(glob.glob('/home/pkumtd/Desktop/AHT20/QAQC_PKU/*.txt'), key=os.path.getmtime)
   
    # 读取最新的文件内容
    with open(file_path, 'r') as file:
        vals = file.readlines()[-1].strip().split()  # 获取最后一行内容并分割

    # 确保数据长度正确
    if len(vals) == 4:
        timestamp = f"{vals[0]} {vals[1]}"
        temperature = f"{vals[2]}°C"
        humidity = f"{vals[3]}%"

        # 更新 GUI 显示
        AHT20_text['Time'].config(text=f"Timestamp: {timestamp}")
        AHT20_text['Temp'].config(text=f"Temperature: {temperature}")
        AHT20_text['Hum'].config(text=f"Humidity: {humidity}")
    else:
        # 处理数据格式错误
        AHT20_text['Time'].config(text="Timestamp: --")
        AHT20_text['Temp'].config(text="Temperature: --")
        AHT20_text['Hum'].config(text="Humidity: --")
   
    # 5000 毫秒后再次调用 read_AHT20
    root.after(2000, read_AHT20)

def start_AHT20_monitoring():
    """启动 AHT20.sh 并开始监控数据"""
    global aht20_process

    # 检查之前是否有正在运行的 AHT20 进程
    if aht20_process is not None:
        os.killpg(os.getpgid(aht20_process.pid), signal.SIGINT)  # 终止旧进程
        aht20_process.wait()  # 等待进程完全终止

    # 运行 AHT20.sh 脚本
    aht20_process = subprocess.Popen(
        ["/home/pkumtd/Desktop/AHT20/AHT20.sh"],
        shell=True,
        preexec_fn=os.setsid  # 设置进程组ID，使得可以向该组发送信号
    )
    # 调用 read_AHT20 函数开始读取数据
    read_AHT20()

def on_closing_AHT20():
    """关闭GUI并终止AHT20.sh进程"""
    global aht20_process
    if aht20_process is not None:
        # 发送 SIGINT 信号，相当于按下 Ctrl+C
        os.killpg(os.getpgid(aht20_process.pid), signal.SIGINT)
        aht20_process.wait()  # 等待进程结束
    root.destroy()  # 关闭 GUI 窗口    \

def draw_AHT20_monitoring():
       # 运行 AHT20.sh 脚本
     subprocess.Popen(
        ["/home/pkumtd/Desktop/AHT20/plot.sh"],
        shell=True,
        preexec_fn=os.setsid  # 设置进程组ID，使得可以向该组发送信号
    )
    

def stop_AHT20_monitoring():
    """停止 AHT20.sh 进程"""
    global aht20_process

    # 检查之前是否有正在运行的 AHT20 进程
    if aht20_process is not None:
        os.killpg(os.getpgid(aht20_process.pid), signal.SIGINT)  # 终止旧进程
        aht20_process.wait()  # 等待进程完全终止
        aht20_process = None  # 重置进程变量    



##########











def step_home():
    # Clear error messages
    entry.delete(1.0,tk.END)

    client = Client(ip_address.get())
    # See above explaination of this operation
    try:
        query(client, "step_home")
    except Exception as e:
        print_warning(str(e)+' due to step_home. Ignore!')
        # Read Pin 17 of teensy (stp_home)
        pin17 = 1
        while(1):
            try:
                pin17 = query(client, "read_pin 17")
            except Exception as e:
                print_warning(str(e)+" waiting for read_pin 17. Retry!")
            # Pin stp_home LOW means home position
            if pin17 == 0:
                print("step_home done")
                step_lastposition = 0
                os.system('echo %d > /home/pkumtd/qaqc_jig/.step_lastposition'%step_lastposition)
                break
            time.sleep(10)
        # clearup recvfrom buffer
        _oldtimeout = client.sock.gettimeout()
        for _i in range(5):
            try:
                client.sock.settimeout(1)
                client.recv()
            except Exception as e:
                pass
        client.sock.settimeout(_oldtimeout)

def step_module(module_i):
   
   out = Popen(['cat','/home/pkumtd/qaqc_jig/.step_lastposition'],stdout=subprocess.PIPE)
   step_lastposition = int(out.stdout.read().decode().rstrip())

   ##module_i = int(module_step_entry.get())
   print("going to module %d from module %d"%(module_i,step_lastposition))
   
   client = Client(ip_address.get())
   #Move the stepper motor to the position of the i-th module
   if stepper_enable.get():
      try:
         if module_i>step_lastposition:
            for j in range(step_lastposition +1, module_i+1):
               query(client, "step %i" % list_nstep[j], 600)
            print("step %i done" % module_i)
         elif module_i<step_lastposition:
            for j in range(module_i +1, step_lastposition+1):
               query(client, "step %i" % -list_nstep[j], 600)
            print("step %i done" % module_i)
         else:
            pass
      except Exception as e:
         print_warning(str(e)+" step")
         return

      step_lastposition = module_i
      os.system('echo %d > /home/pkumtd/qaqc_jig/.step_lastposition'%step_lastposition)

def n_boards_changed(*args):
    for i in range(4):
        if i + 1 <= int(n_boards_var.get()):
            module_checkbox[i*3].configure(state=tk.NORMAL)
            module_checkbox[i*3+1].configure(state=tk.NORMAL)
            module_checkbox[i*3+2].configure(state=tk.NORMAL)
        else:
            module_checkbox[i*3].configure(state=tk.DISABLED)
            module_checkbox[i*3+1].configure(state=tk.DISABLED)
            module_checkbox[i*3+2].configure(state=tk.DISABLED)
            module_available[i*3].set(0)
            module_available[i*3+1].set(0)
            module_available[i*3+2].set(0)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser("BTL QA/QC GUI")
    parser.add_argument("--debug", action='store_true', help='debug')
    args = parser.parse_args()

    if args.debug:
        DEBUG = True
        WAVEDUMP_PROGRAM = './wavedump-test'
        INTEGRATE_WAVEFORMS_PROGRAM = './wavedump-test'

    # Create the root window
    root = tk.Tk()

    root.title("BTL QA/QC GUI")

    # Make sure to save before quitting
    root.protocol("WM_DELETE_WINDOW", on_closing_AHT20)
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Right now there are three main frames in the window: the main frame with
    # buttons for taking data and showing results, a second frame for settings
    # like which modules are present, and a third frame for error messages.
    frame_top = tk.Frame(root)
    frame_bottom = tk.Frame(root)

    frame_main = tk.LabelFrame(frame_top,text="Main")
    frame_config = tk.LabelFrame(frame_top,text="Settings")
    frame_log = tk.LabelFrame(frame_bottom,text="Messages")

    frame_temps = tk.LabelFrame(frame_config,text="Temperatures")
    
    frame_top.pack(expand=1,fill='both',side=tk.TOP)
    frame_bottom.pack(expand=1,fill='both',side=tk.BOTTOM)

    frame_main.pack(expand=1,fill='both',side=tk.LEFT)
    frame_config.pack(expand=1,fill='both',side=tk.RIGHT)
    frame_log.pack(expand=1,fill='both')


    frame_temps.pack(expand=1,fill='both',side=tk.BOTTOM)
    #frame_temps.pack(expand=1,fill='x',side=tk.BOTTOM)
    
    # The main frame has tabs for switching between taking data and polling
    # thermistor temperatures and TEC resistances.
    tab = ttk.Notebook(frame_main)
    tab1 = ttk.Frame(tab)
    tab2 = ttk.Frame(tab)
    tab.add(tab1,text="Data")
    tab.add(tab2,text="Polling")
    tab.pack(expand=1,fill='both')

    # The following are frames in the config frame
    frame_menu = tk.Frame(frame_config)
    frame_barcodes = tk.Frame(frame_config)

    # The following are frames in the main frame
    frame_settings = tk.Frame(tab1)
    frame_buttons = tk.Frame(tab1)
    frame_buttons2 = tk.Frame(tab1)
    frame_chiller = tk.Frame(tab1)
    frame_stepper = tk.Frame(tab1)
    frame_thermistor = tk.Frame(tab2)
    frame_adv_buttons = tk.Frame(tab2)

    # Settings Frame
    assembly_center = tk.StringVar(frame_menu)
    assembly_center.set(ASSEMBLY_CENTERS[0])
    
    barcode_labels = []
    barcodes = []
    barcode_entries = []
    vbd_labels = []
    vbds = []
    vbd_entries = []
    progress_bars = []
    module_available = []
    module_checkbox = []
    module_status = []
    for i in range(12):
        barcode_labels.append(tk.Label(frame_barcodes,text="Barcode %i: " % i))
        barcode_labels[-1].grid(row=i,column=0)
        barcodes.append(tk.StringVar(frame_menu))
        barcode_entries.append(tk.Entry(frame_barcodes,textvariable=barcodes[-1]))
        barcode_entries[-1].grid(row=i,column=1)
        vbd_labels.append(tk.Label(frame_barcodes,text="Vbd %i (V): " % i))
        vbd_labels[-1].grid(row=i,column=2)
        vbds.append(tk.StringVar(frame_menu))
        vbd_entries.append(tk.Entry(frame_barcodes,textvariable=vbds[-1]))
        vbd_entries[-1].grid(row=i,column=3)
        module_available.append(tk.IntVar(frame_barcodes, value=1))
        checkbox = tk.Checkbutton(frame_barcodes, text='Present', variable=module_available[-1], onvalue=1, offvalue=0)
        module_checkbox.append(checkbox)
        checkbox.grid(row=i,column=4)
        progress_bar = ttk.Progressbar(frame_barcodes, orient='horizontal', mode='determinate', length=100)
        progress_bars.append(progress_bar)
        progress_bar.grid(row=i,column=5)
        module_status.append(tk.Label(frame_barcodes,text="-"))
        module_status[-1].grid(row=i,column=6)

    for i in range(11):
        barcode_entries[i].bind('<Return>', lambda x, i=i: barcode_entries[i+1].focus())

    assembly_center_label = tk.Label(frame_menu,text="Assembly Center: ")
    assembly_center_label.grid(row=0,column=0)

    assembly_center_menu = tk.OptionMenu(frame_menu, assembly_center, *ASSEMBLY_CENTERS)
    assembly_center_menu.grid(row=0,column=1)
    
    n_boards_label = tk.Label(frame_menu,text="Number of Boards: ")
    n_boards_label.grid(row=2,column=0)

    n_boards_var = tk.StringVar(frame_menu)
    n_boards_var.set(NUMBER_OF_BOARDS[3])

    n_boards_menu = tk.OptionMenu(frame_menu, n_boards_var, *NUMBER_OF_BOARDS, command=n_boards_changed)
    n_boards_menu.grid(row=2,column=1)

    n_boards_changed()

    ov_menu_label = tk.Label(frame_menu, text="OV (V): ")
    ov_menu_label.grid(row=3,column=0)
    ov = tk.StringVar(frame_menu)
    ov_menu_entry = tk.Entry(frame_menu, textvariable=ov)
    ov_menu_entry.grid(row=3,column=1)
    
    trigger_menu_label = tk.Label(frame_menu, text="Trigger Threshold (V): ")
    trigger_menu_label.grid(row=4,column=0)
    trigger = tk.StringVar(frame_menu)
    trigger_menu_entry = tk.Entry(frame_menu, textvariable=trigger)
    trigger_menu_entry.grid(row=4,column=1)

    ip_address_menu_label = tk.Label(frame_menu, text="IP Address: ")
    ip_address_menu_label.grid(row=5,column=0)
    ip_address = tk.StringVar(frame_menu)
    ip_address.set('192.168.1.177')
    ip_address_menu_entry = tk.Entry(frame_menu, textvariable=ip_address)
    ip_address_menu_entry.grid(row=5,column=1)

    data_path_menu_label = tk.Label(frame_menu, text="Data path: ")
    data_path_menu_label.grid(row=6,column=0)
    data_path = tk.StringVar(frame_menu)
    data_path.set('')
    data_path_menu_entry = tk.Entry(frame_menu, textvariable=data_path)
    data_path_menu_entry.grid(row=6,column=1)

    label_menu_label = tk.Label(frame_menu, text="Extra label: ")
    label_menu_label.grid(row=7,column=0)
    label = tk.StringVar(frame_menu)
    label.set('')
    label_menu_entry = tk.Entry(frame_menu, textvariable=label)
    label_menu_entry.grid(row=7,column=1)
    
    n_spe_events_menu_label = tk.Label(frame_menu, text="Number of SPE Events: ")
    n_spe_events_menu_label.grid(row=8,column=0)
    n_spe_events = tk.IntVar(frame_menu)
    n_spe_events.set(100000)
    n_spe_events_menu_entry = tk.Entry(frame_menu, textvariable=n_spe_events)
    n_spe_events_menu_entry.grid(row=8,column=1)

    n_source_events_menu_label = tk.Label(frame_menu, text="Number of Source Events: ")
    n_source_events_menu_label.grid(row=9,column=0)
    n_source_events = tk.IntVar(frame_menu)
    n_source_events.set(100000)
    n_source_events_menu_entry = tk.Entry(frame_menu, textvariable=n_source_events)
    n_source_events_menu_entry.grid(row=9,column=1)
    
    stepper_enable_label = tk.Label(frame_menu, text="Enable stepper motor: ")
    stepper_enable_label.grid(row=10,column=0)
    stepper_enable = tk.IntVar(frame_settings, value=0)
    stepper_enable_checkbox = tk.Checkbutton(frame_menu, text=None, variable=stepper_enable, onvalue=1, offvalue=0)
    stepper_enable_checkbox.grid(row=10,column=1)

    stepper_dLperstep_menu_label = tk.Label(frame_menu, text="Distance per step (cm): ")
    stepper_dLperstep_menu_label.grid(row=11,column=0)
    stepper_dLperstep = tk.StringVar(frame_menu)
    stepper_dLperstep.set(str(dLcm_perstep))
    stepper_dLperstep_menu_entry = tk.Entry(frame_menu, textvariable=stepper_dLperstep)
    stepper_dLperstep_menu_entry.grid(row=11,column=1)

    frame_menu.pack()
    frame_barcodes.pack()

    # Main Frame - Polling
    tk.Label(frame_thermistor,text="Thermistor A (C)").grid(row=0,column=1)
    tk.Label(frame_thermistor,text="Thermistor B (C)").grid(row=0,column=2)
    tk.Label(frame_thermistor,text="TEC A (Ohms)").grid(row=0,column=3)
    tk.Label(frame_thermistor,text="TEC B (Ohms)").grid(row=0,column=4)
    thermistor_labels = {}
    thermistor_text = {}
    for i in range(12):
        thermistor_labels[i] = tk.Label(frame_thermistor,text="Barcode %i: " % i)
        thermistor_labels[i].grid(row=i+1,column=0)
        thermistor_text[(i,'temp_a')] = tk.Label(frame_thermistor,text="")
        thermistor_text[(i,'temp_a')].grid(row=i+1,column=1)
        thermistor_text[(i,'temp_b')] = tk.Label(frame_thermistor,text="")
        thermistor_text[(i,'temp_b')].grid(row=i+1,column=2)
        thermistor_text[(i,'tec_a')] = tk.Label(frame_thermistor,text="")
        thermistor_text[(i,'tec_a')].grid(row=i+1,column=3)
        thermistor_text[(i,'tec_b')] = tk.Label(frame_thermistor,text="")
        thermistor_text[(i,'tec_b')].grid(row=i+1,column=4)

    button_poll = tk.Button(master=frame_adv_buttons,text="Poll", width=25, height=5, command=poll)
    button_poll.pack()

    frame_thermistor.grid(row=0,column=0)
    frame_adv_buttons.grid(row=1,column=0)





    # Main Frame - Take Data
    entry = tk.Text(master=frame_log)
    entry.pack(expand=1,fill='both')

    entry.tag_config("error",foreground='red')
    
    button = tk.Button(master=frame_buttons,text="Take Data", width=25, height=5, command=take_data)
    button.pack()

    stop_button = tk.Button(master=frame_buttons,text="Stop", width=25, height=5, command=stop)
    stop_button['state'] = tk.DISABLED
    stop_button.pack()

    reanalyze_button = tk.Button(master=frame_buttons,text="Reanalyze Data", width=25, height=5, command=reanalyze_data)
    reanalyze_button.pack()

    button_home = tk.Button(master=frame_buttons,text="Stepper Home", width=25, height=5, command=step_home)
    button_home.pack()
    
    button_module = tk.Button(master=frame_buttons,text="Stepper To Module", width=25, height=5, command = lambda: step_module(int(module_step_entry.get())))
    button_module.pack()

    


    ###########
    # 在 frame_temps 中添加3个标签
    AHT20_text = {}
    AHT20_text['Time'] = tk.Label(frame_temps, text="Timestamp: --", width=50)
    AHT20_text['Temp'] = tk.Label(frame_temps, text="Temperature (°C): --", width=50)
    AHT20_text['Hum'] = tk.Label(frame_temps, text="Humidity (%): --", width=50)

    AHT20_text['Time'].pack()
    AHT20_text['Temp'].pack()
    AHT20_text['Hum'].pack()


    # 创建按钮
    button_module = tk.Button(master=frame_buttons, text="Tem&Hum Monitoring", width=25, height=5, command=start_AHT20_monitoring)
    button_module.pack()

    # 创建绘图按钮
    button_plot = tk.Button(master=frame_buttons, text="Plotting Tem&Hum Monitoring", width=25, height=5, command=draw_AHT20_monitoring)
    button_plot.pack()  # 设置按钮位置

    # 创建停止按钮
    button_stop = tk.Button(master=frame_buttons, text="Stop Tem&Hum Monitoring", width=25, height=5, command=stop_AHT20_monitoring)
    button_stop.pack()  # 设置按钮位置

    ###############
    
    #stepper_enable = tk.IntVar(frame_settings, value=0)
    #stepper_enable_checkbox = tk.Checkbutton(frame_settings, text='Enable Stepper', variable=stepper_enable, onvalue=1, offvalue=0)
    #stepper_enable_checkbox.pack()
    
    # if USE_TTi:
    #     mytti3 = TXP3510P('/dev/TTi-1')
    #     state = mytti3.getState()
        
    #     power_on_button = tk.Button(master=frame_buttons2,text="Power on", width=25, height=5, command=power_on)
    #     if state == '0':
    #         power_on_button['state'] = tk.NORMAL
    #     else:
    #         power_on_button['state'] = tk.DISABLED        
    #     power_on_button.pack()
        
    #     power_off_button = tk.Button(master=frame_buttons2,text="Power off", width=25, height=5, command=power_off)
    #     if state == '0':
    #         power_off_button['state'] = tk.DISABLED
    #     else:
    #         power_off_button['state'] = tk.NORMAL
    #     power_off_button.pack()
    
    # if USE_CHILLER:
    #     out = Popen(['/home/pkumtd/LAUDAChiller/driveChiller.py', '--check-state'],stdout=subprocess.PIPE)
    #     state = int(out.stdout.read().decode().rstrip())
        
    #     chiller_pid = -1
    #     if os.path.isfile('/home/cmsdaq/.setBoxTemp_PID.pid'):
    #         out = Popen(['cat','/home/cmsdaq/.setBoxTemp_PID.pid'],stdout=subprocess.PIPE)
    #         chiller_pid = int(out.stdout.read().decode().rstrip())
    
    #     if chiller_pid == -1:
    #         chiller_on_button = tk.Button(master=frame_buttons2,text="Chiller on", width=25, height=5, command=chiller_on)
    #         chiller_on_button['state'] = tk.NORMAL
    #     else:
    #         chiller_on_button = tk.Button(master=frame_buttons2,text="Chiller is on (PID: %d)"%chiller_pid, width=25, height=5, command=chiller_on)
    #         chiller_on_button['state'] = tk.DISABLED
    #     chiller_on_button.pack()
        
    #     chiller_off_button = tk.Button(master=frame_buttons2,text="Chiller off", width=25, height=5, command=chiller_off)
    #     if state == 1:
    #         chiller_off_button['state'] = tk.DISABLED
    #     else:
    #         chiller_off_button['state'] = tk.NORMAL
    #     chiller_off_button.pack()
    
    #     chiller_temp_label = tk.Label(frame_chiller, text="chiller target temp. (° C): ")
    #     chiller_temp_label.grid(row=0,column=0)
    #     chiller_temp = tk.StringVar(frame_temps, value="23.0")
    #     chiller_temp_entry = tk.Entry(frame_chiller, textvariable=chiller_temp)
    #     chiller_temp_entry.grid(row=1,column = 0)
        
    #     tk.Label(frame_temps,text="#1").grid(row=2,column=1)
    #     tk.Label(frame_temps,text="temp. (° C)").grid(row=3,column=0)
    #     tk.Label(frame_temps,text=" hum. (%)").grid(row=4,column=0)    
        
    #     dht22_text = {}
    #     for i in range(1):
    #         dht22_text[(i,'temp')] = tk.Label(frame_temps,text="n/a")
    #         dht22_text[(i,'temp')].grid(row=3,column=1+i)
    #         dht22_text[(i,'hum')] = tk.Label(frame_temps,text="n/a")
    #         dht22_text[(i,'hum')].grid(row=4,column=1+i)
    #     read_dht22()
        
    #     module_step_label = tk.Label(frame_stepper, text="module to go: ")
    #     module_step_label.grid(row=0,column=0)
    #     module_step = tk.StringVar(frame_temps, value="0")
    #     module_step_entry = tk.Entry(frame_stepper, textvariable=module_step)
    #     module_step_entry.grid(row=1,column = 0)

    #frame_settings.grid(row=0,column=1)
    frame_buttons.grid(row=0,column=1)
    frame_buttons2.grid(row=0,column=2)
    frame_chiller.grid(row=1,column=2)
    frame_stepper.grid(row=2,column=2)
    #frame_temps.grid(row=1,column=2)
    
    load()

    root.mainloop()
