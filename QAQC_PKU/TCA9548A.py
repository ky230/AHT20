import sys
import serial
import time
import os
import shutil
import glob

def delete_test_folders(base_path_pattern):
    """删除所有符合 base_path_pattern 的文件夹"""
    for folder in glob.glob(base_path_pattern):
        if os.path.isdir(folder):
            shutil.rmtree(folder)
            print(f"Deleted folder: {folder}")

# 删除所有符合 QAQC_PKU_*_test 模式的文件夹
base_path_pattern = '/home/pkumtd/Desktop/AHT20/QAQC_PKU_*_test'
delete_test_folders(base_path_pattern)

# 获取命令行参数
if len(sys.argv) != 3:
    print("Usage: python TCA9548A.py <timestamp> <0 or 1>")
    sys.exit(1)

timestamp = sys.argv[1]  # 例如 "20240902035955"
cleanup_on_exit = sys.argv[2] == '0'
base_path = f'/home/pkumtd/Desktop/AHT20/QAQC_PKU_{timestamp}'
base_path_test = f'{base_path}_test'

# 设置串口参数
serial_port = '/dev/ttyACM2'
baud_rate = 115200

# 创建存储路径
if not os.path.exists(base_path):
    os.makedirs(base_path)

# 打开串口
ser = serial.Serial(serial_port, baud_rate, timeout=1)
time.sleep(2)

# 创建一个字典来存储每个传感器对应的文件
sensor_files = {}
sensor_data = {}

initialization_done = False

def write_averages():
    """写入平均值到 average_{timestamp}.txt"""
    average_file_path = f'{base_path}/average_{timestamp}.txt'
    
    # 确保有数据存在
    if not sensor_data:
        return
    
    sensor_ids = list(sensor_data.keys())
    if not sensor_ids:
        return

    with open(average_file_path, 'w') as avg_file:
        # 写入表头
        avg_file.write("Timestamp Temperature(°C) Humidity(%)\n")
        
        # 获取所有文件的时间戳
        timestamps = list(sensor_data[sensor_ids[0]].keys())
        for t in timestamps:
            temp_values = []
            hum_values = []
            for sensor_id in sensor_ids:
                temp_values.append(sensor_data[sensor_id].get(t, [None, None])[0])
                hum_values.append(sensor_data[sensor_id].get(t, [None, None])[1])
            
            # 计算平均值
            avg_temp = sum(v for v in temp_values if v is not None) / len(temp_values)
            avg_hum = sum(v for v in hum_values if v is not None) / len(hum_values)
            
            # 写入到文件
            avg_file.write(f"{t} {avg_temp:.2f} {avg_hum:.2f}\n")

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            if data:
                print(data)
                
                if "initialized." in data:
                    initialization_done = True
                
                if initialization_done:
                    parts = data.split("   ")
                    for part in parts:
                        if part:
                            try:
                                sensor_id, sensor_data_str = part.split(":", 1)
                                sensor_id = sensor_id.strip()
                                sensor_data_str = sensor_data_str.strip()
                                
                                # 使用传递的时间戳来生成文件名
                                file_path = f'{base_path}/{sensor_id}_{timestamp}.txt'
                                
                                if sensor_id not in sensor_files:
                                    sensor_files[sensor_id] = open(file_path, 'a')
                                    sensor_data[sensor_id] = {}
                                    # 写入表头
                                    sensor_files[sensor_id].write("Timestamp Temperature(°C) Humidity(%)\n")
                                
                                data_parts = sensor_data_str.split(", ")
                                if len(data_parts) == 2:
                                    temperature = data_parts[0].split(": ")[1]
                                    humidity = data_parts[1].split(": ")[1]
                                    
                                    # 使用相同的时间戳格式
                                    current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                    
                                    # 写入数据，不包含符号
                                    temperature_value = float(temperature.replace('°C', '').strip())
                                    humidity_value = float(humidity.replace('%', '').strip())
                                    
                                    sensor_files[sensor_id].write(f"{current_timestamp} {temperature_value:.2f} {humidity_value:.2f}\n")
                                    sensor_files[sensor_id].flush()
                                    
                                    # 更新传感器数据字典
                                    if current_timestamp not in sensor_data[sensor_id]:
                                        sensor_data[sensor_id][current_timestamp] = [temperature_value, humidity_value]
                                    else:
                                        sensor_data[sensor_id][current_timestamp] = [temperature_value, humidity_value]
                                
                                # 计算并写入平均值
                                write_averages()
                                
                            except ValueError as e:
                                print(f"Error processing part: {part}")
                                print(f"Exception: {e}")

except KeyboardInterrupt:
    for file in sensor_files.values():
        file.close()
    
    # 处理清理
    if cleanup_on_exit:
        # 如果 cleanup_on_exit 为 True，重命名文件夹
        if os.path.exists(base_path):
            if os.path.exists(base_path_test):
                shutil.rmtree(base_path_test)  # 删除旧的 base_path_test 文件夹
            shutil.move(base_path, base_path_test)  # 重命名文件夹
        else:
            print(f"Base path does not exist: {base_path}")
    
    print("Program terminated.")

