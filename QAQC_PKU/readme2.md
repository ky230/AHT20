# TCA9548A & Arduino Uno
![Tem&Hum Monitoring GUI](TCA9548A.png)
| AHT20 引脚 | Arduino Uno 引脚 |
|------------|------------------|
| SCL        | A5               |
| SDA        | A4               |
| VCC        | 5V               |
| GND        | GND              |
| SD*        | SDA              |
| SC*        | SCL              |


# AHT20 & Arduino Uno
![Tem&Hum Monitoring GUI](AHT20.jpg)
| AHT20 引脚 | Arduino Uno 引脚 |
|------------|------------------|
| SCL        | A5               |
| SDA        | A4               |
| VCC        | 5V               |
| GND        | GND              |


# TCA9548A & AHT20 
![Tem&Hum Monitoring GUI](Muti.jpg)


# Details
![Tem&Hum Monitoring GUI](ACM.jpg)
See https://github.com/ky230/AHT20/blob/02bac9d1c16a3ce11920e34191d235469bc5c8cb/QAQC_PKU/TCA9548A.py#L30


If left: 
‘’‘python
serial_port = '/dev/ttyACM1'
’‘’

If right:
‘’‘python
serial_port = '/dev/ttyACM0'
’‘’


# New button : Test Tem&Hum Monitoring
![Tem&Hum Monitoring GUI](qaqc-TCA9548A.jpg)

## update Plotting button

![Tem&Hum Monitoring GUI](Plotting.jpg)

# test.py (independent code)
![Tem&Hum Monitoring GUI](test.jpg)




# qaqc-pku-gui-TCA9548A.py

## Add new head file
https://github.com/ky230/AHT20/blob/02bac9d1c16a3ce11920e34191d235469bc5c8cb/QAQC_PKU/qaqc-gui-pku-TCA9548A.py#L27 ~  https://github.com/ky230/AHT20/blob/02bac9d1c16a3ce11920e34191d235469bc5c8cb/QAQC_PKU/qaqc-gui-pku-TCA9548A.py#L29

‘’‘python
import threading ##%
import re
import sys
’‘’

## Add new global variable

https://github.com/ky230/AHT20/blob/02bac9d1c16a3ce11920e34191d235469bc5c8cb/QAQC_PKU/qaqc-gui-pku-TCA9548A.py#L33

‘’‘python
timestamp = None ##%
’‘’
