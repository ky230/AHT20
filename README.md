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


# Details of qaqc-gui-pku.py

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
Comment read_dht22
```python
# def read_dht22():
#     out = Popen(['ssh', 'cmsdaq@raspcmsroma01', 'tail', '-n 1', '/home/cmsdaq/SHT40/temp.txt'],stdout=PIPE)
#     vals = (out.stdout.read().decode('utf-8')).split(',')
#     for i in range(1):
#         dht22_text[(i,'temp')].config(text="%.1f"%float(vals[0+0+2*i]))
#         dht22_text[(i,'hum')].config(text="%.1f"%float(vals[0+1+2*i]))
#     root.after(3000,read_dht22)
```



```
