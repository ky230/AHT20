#!/usr/bin/env python3
"""
GUI for controlling the Caltech BTL QA/QC jig.

Author: Anthony LaTorre
Last Updated: Jan 24, 2023
"""
USE_TTi = True
USE_CHILLER = True
 
from btl import Client     ###
import tkinter as tk       
from tkinter import ttk    ###
import random
from os.path import join, expanduser, exists, splitext
import os
import json
from subprocess import Popen, PIPE
import subprocess
import os
import h5py               ####
import sys
import time

if USE_TTi:
   sys.path.append('/home/cmsdaq/DAQ/TXP3510P')
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
out = Popen(['cat','/home/cmsdaq/DAQ/qaqc_jig/.step_lastposition'],stdout=subprocess.PIPE)
step_lastposition = int(out.stdout.read().decode().rstrip())



#######

def read_dht22():
    out = Popen(['ssh', 'cmsdaq@raspcmsroma01', 'tail', '-n 1', '/home/cmsdaq/SHT40/temp.txt'],stdout=PIPE)
    vals = (out.stdout.read().decode('utf-8')).split(',')
    for i in range(1):
        dht22_text[(i,'temp')].config(text="%.1f"%float(vals[0+0+2*i]))
        dht22_text[(i,'hum')].config(text="%.1f"%float(vals[0+1+2*i]))
    root.after(3000,read_dht22)

#######


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

    frame_temps.pack(expand=1,fill='x',side=tk.BOTTOM)
    
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
    
    #stepper_enable = tk.IntVar(frame_settings, value=0)
    #stepper_enable_checkbox = tk.Checkbutton(frame_settings, text='Enable Stepper', variable=stepper_enable, onvalue=1, offvalue=0)
    #stepper_enable_checkbox.pack()
    
    if USE_TTi:
        mytti3 = TXP3510P('/dev/TTi-1')
        state = mytti3.getState()
        
        power_on_button = tk.Button(master=frame_buttons2,text="Power on", width=25, height=5, command=power_on)
        if state == '0':
            power_on_button['state'] = tk.NORMAL
        else:
            power_on_button['state'] = tk.DISABLED        
        power_on_button.pack()
        
        power_off_button = tk.Button(master=frame_buttons2,text="Power off", width=25, height=5, command=power_off)
        if state == '0':
            power_off_button['state'] = tk.DISABLED
        else:
            power_off_button['state'] = tk.NORMAL
        power_off_button.pack()
    
    if USE_CHILLER:
        out = Popen(['/home/cmsdaq/DAQ/LAUDAChiller/driveChiller.py', '--check-state'],stdout=subprocess.PIPE)
        state = int(out.stdout.read().decode().rstrip())
        
        chiller_pid = -1
        if os.path.isfile('/home/cmsdaq/.setBoxTemp_PID.pid'):
            out = Popen(['cat','/home/cmsdaq/.setBoxTemp_PID.pid'],stdout=subprocess.PIPE)
            chiller_pid = int(out.stdout.read().decode().rstrip())
    
        if chiller_pid == -1:
            chiller_on_button = tk.Button(master=frame_buttons2,text="Chiller on", width=25, height=5, command=chiller_on)
            chiller_on_button['state'] = tk.NORMAL
        else:
            chiller_on_button = tk.Button(master=frame_buttons2,text="Chiller is on (PID: %d)"%chiller_pid, width=25, height=5, command=chiller_on)
            chiller_on_button['state'] = tk.DISABLED
        chiller_on_button.pack()
        
        chiller_off_button = tk.Button(master=frame_buttons2,text="Chiller off", width=25, height=5, command=chiller_off)
        if state == 1:
            chiller_off_button['state'] = tk.DISABLED
        else:
            chiller_off_button['state'] = tk.NORMAL
        chiller_off_button.pack()
    
        chiller_temp_label = tk.Label(frame_chiller, text="chiller target temp. (° C): ")
        chiller_temp_label.grid(row=0,column=0)
        chiller_temp = tk.StringVar(frame_temps, value="23.0")
        chiller_temp_entry = tk.Entry(frame_chiller, textvariable=chiller_temp)
        chiller_temp_entry.grid(row=1,column = 0)
        
        tk.Label(frame_temps,text="#1").grid(row=2,column=1)
        tk.Label(frame_temps,text="temp. (° C)").grid(row=3,column=0)
        tk.Label(frame_temps,text=" hum. (%)").grid(row=4,column=0)    
        
        dht22_text = {}
        for i in range(1):
            dht22_text[(i,'temp')] = tk.Label(frame_temps,text="n/a")
            dht22_text[(i,'temp')].grid(row=3,column=1+i)
            dht22_text[(i,'hum')] = tk.Label(frame_temps,text="n/a")
            dht22_text[(i,'hum')].grid(row=4,column=1+i)
        read_dht22()
        
        module_step_label = tk.Label(frame_stepper, text="module to go: ")
        module_step_label.grid(row=0,column=0)
        module_step = tk.StringVar(frame_temps, value="0")
        module_step_entry = tk.Entry(frame_stepper, textvariable=module_step)
        module_step_entry.grid(row=1,column = 0)

    #frame_settings.grid(row=0,column=1)
    frame_buttons.grid(row=0,column=1)
    frame_buttons2.grid(row=0,column=2)
    frame_chiller.grid(row=1,column=2)
    frame_stepper.grid(row=2,column=2)
    #frame_temps.grid(row=1,column=2)
    
    load()

    root.mainloop()