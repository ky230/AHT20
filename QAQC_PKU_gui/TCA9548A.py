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

def check_and_delete_folders(base_path_pattern, required_file_count):
    """检查文件夹中的 .txt 文件数量，如果不符合要求则删除文件夹"""
    for folder in glob.glob(base_path_pattern):
        if os.path.isdir(folder):
            txt_files = glob.glob(os.path.join(folder, '*.txt'))
            if len(txt_files) != required_file_count:
                shutil.rmtree(folder)
                print(f"Deleted folder due to file count mismatch: {folder}")

# 检查并删除文件夹，如果里面的 .txt 文件数量不为 9
check_and_delete_folders('/home/pkumtd/Desktop/AHT20/QAQC_PKU_*', 9)

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
serial_port = '/dev/ttyACM0'
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
start_time = time.time()  # 记录程序开始时间

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
                # 只考虑那些在此时间点有数据的传感器
                if t in sensor_data[sensor_id]:
                    temp_values.append(sensor_data[sensor_id][t][0])
                    hum_values.append(sensor_data[sensor_id][t][1])
            
            # 计算平均值，仅当有数据的传感器数量大于0时进行计算
            if temp_values:
                avg_temp = sum(temp_values) / len(temp_values)
            else:
                avg_temp = None  # 没有数据时设为 None 或 其他合适的值
            
            if hum_values:
                avg_hum = sum(hum_values) / len(hum_values)
            else:
                avg_hum = None  # 没有数据时设为 None 或 其他合适的值
            
            # 写入到文件，如果有平均值计算结果
            if avg_temp is not None and avg_hum is not None:
                avg_file.write(f"{t} {avg_temp:.2f} {avg_hum:.2f}\n")
            else:
                # 如果没有数据，按需处理，比如跳过这一行或写入其他标识
                avg_file.write(f"{t} No data\n")


def rename_files(base_path, timestamp):
    """重命名生成的文件，按指定映射关系更换 AHT20_X 为 Module_Y"""
    
    # 映射关系字典
    sensor_mapping = {
        '0': '6',
        '1': '4',
        '2': '2',
        '3': '0',
        '4': '7',
        '5': '5',
        '6': '3',
        '7': '1'
    }

    # 查找所有符合 AHT20_X_* 的文件
    for file_path in glob.glob(f'{base_path}/AHT20_*_{timestamp}.txt'):
        # 提取传感器 ID 和时间戳
        file_name = os.path.basename(file_path)
        sensor_id = file_name.split('_')[1]
        
        # 根据映射关系生成新的文件名
        if sensor_id in sensor_mapping:
            new_sensor_id = sensor_mapping[sensor_id]
            new_file_name = file_name.replace(f'AHT20_{sensor_id}', f'Module_{new_sensor_id}')
            new_file_path = os.path.join(base_path, new_file_name)
            
            # 重命名文件
            os.rename(file_path, new_file_path)
            print(f"Renamed {file_name} to {new_file_name}")
        else:
            print(f"Sensor ID {sensor_id} not found in mapping, skipping file {file_name}.")

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
    
    # 文件重命名
    rename_files(base_path, timestamp)
    
    # 如果运行时间小于60秒，则重命名文件夹加上后缀_test
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    if elapsed_time < 60 and not cleanup_on_exit:
        if os.path.exists(base_path):
            if not os.path.exists(base_path_test):
                shutil.move(base_path, base_path_test)
                print(f"Renamed {base_path} to {base_path_test} due to short execution time.")
            else:
                print(f"Folder with suffix '_test' already exists: {base_path_test}")
    
    print("Program terminated.")
