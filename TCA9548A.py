import serial
import time
import os

# 设置串口参数
serial_port = '/dev/cu.usbmodem1201'  # 根据你的实际串口端口修改
baud_rate = 115200
current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
base_path = '/Users/ky230/Desktop/sensor/AHT20'

# 创建存储路径
if not os.path.exists(base_path):
    os.makedirs(base_path)

# 打开串口
ser = serial.Serial(serial_port, baud_rate, timeout=1)
time.sleep(2)  # 给Arduino一些时间来复位

# 创建一个字典来存储每个传感器对应的文件
sensor_files = {}
initialization_done = False

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data:
                print(data)
                
                # 检查是否所有传感器都初始化完成
                if "initialized." in data:
                    initialization_done = True
                
                # 只有在初始化完成后才开始记录数据
                if initialization_done:
                    # 分割数据并处理每个传感器的数据
                    parts = data.split("   ")
                    for part in parts:
                        if part:
                            # 提取传感器编号和数据
                            try:
                                sensor_id, sensor_data = part.split(":", 1)
                                sensor_id = sensor_id.strip()
                                sensor_data = sensor_data.strip()
                                
                                # 创建对应传感器的文件路径
                                file_path = f'{base_path}/{sensor_id}_THdata_{current_time}.txt'
                                
                                # 如果文件还没有被创建，则创建一个新的文件并写入标题
                                if sensor_id not in sensor_files:
                                    sensor_files[sensor_id] = open(file_path, 'a')
                                    sensor_files[sensor_id].write("Timestamp Temperature(°C) Humidity(%)\n")
                                
                                # 解析温度和湿度
                                data_parts = sensor_data.split(", ")
                                if len(data_parts) == 2:
                                    temperature = data_parts[0].split(": ")[1]
                                    humidity = data_parts[1].split(": ")[1]
                                    
                                    # 获取当前时间戳
                                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                    
                                    # 写入文件
                                    sensor_files[sensor_id].write(f"{timestamp} {temperature} {humidity}\n")
                                    sensor_files[sensor_id].flush()  # 确保数据立即写入文件
                                else:
                                    print(f"Unexpected data format: {data_parts}")
                            except ValueError as e:
                                print(f"Error processing part: {part}")
                                print(f"Exception: {e}")

except KeyboardInterrupt:
    # 关闭所有打开的文件
    for file in sensor_files.values():
        file.close()
    print("Program terminated.")
