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

## Add  head file "signal"   and  global variable aht20_process
Line 25

```python
import signal
