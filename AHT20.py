#ls /dev/tty.*
import serial
import time

# 设置串口参数
serial_port = '/dev/cu.usbmodem1101'  # 根据你的实际串口端口修改
baud_rate = 115200
current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
file_path = f'/Users/ky230/Desktop/sensor/AHT20/THdata_{current_time}.txt'


# 打开串口
ser = serial.Serial(serial_port, baud_rate, timeout=1)
time.sleep(2)  # 给Arduino一些时间来复位

with open(file_path, 'w') as file:
    file.write("Timestamp Temperature(°C) Humidity(%)\n")  # 写入文件头
    
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data:
                print(data)
                # 获取当前时间戳
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                
                # 分割数据并获取温度和湿度
                parts = data.split()
                if len(parts) == 2:
                    temperature = parts[0]
                    humidity = parts[1]
                    
                    # 写入文件
                    file.write(f"{timestamp} {temperature} {humidity}\n")
                    file.flush()  # 确保数据立即写入文件
