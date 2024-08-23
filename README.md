# Installing
```bash
conda create -n AHT20 python=3.11
conda install numpy scipy matplotlib pandas h5py matplotlib pyserial 
conda config --add channels conda-forge
conda install -c conda-forge root
```
## check
```bash
python -c "import h5py; import pandas as pd; import matplotlib.pyplot as plt; import matplotlib.dates as mdates; from matplotlib.animation import FuncAnimation; import serial; import time; from btl import Client; import tkinter as tk; from tkinter import ttk; import random; from os.path import join, expanduser, exists, splitext; import json;import ROOT as R;import argparse;  from subprocess import Popen, PIPE; import subprocess; import sys; print('All packages imported successfully')"
```
# Run take data

```
source evi.sh
```

# Run plotting
```
source plot.sh`

```


# Details of qaqc-gui-pku.py update

## Add  head file "signal"   and  global variable ：“aht20_process”
Line 25
```python
import signal
```
Line 29
```python
aht20_process = None
```

##  Comment function read_dht22   and define our functions
Line 698 ~ Line 704:  Comment read_dht22
```python
# def read_dht22():
#     out = Popen(['ssh', 'cmsdaq@raspcmsroma01', 'tail', '-n 1', '/home/cmsdaq/SHT40/temp.txt'],stdout=PIPE)
#     vals = (out.stdout.read().decode('utf-8')).split(',')
#     for i in range(1):
#         dht22_text[(i,'temp')].config(text="%.1f"%float(vals[0+0+2*i]))
#         dht22_text[(i,'hum')].config(text="%.1f"%float(vals[0+1+2*i]))
#     root.after(3000,read_dht22)
```


Line 710 ~ Line 782 :  Define our functions
```python
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
```

##  update in main function
Line 894 :   Add AHT20.py termination button
```python
root.protocol("WM_DELETE_WINDOW", on_closing_AHT20)
```
Line 916 :  change qaqc-gui Line 811 into:
```python
frame_temps.pack(expand=1,fill='both',side=tk.BOTTOM)
```
