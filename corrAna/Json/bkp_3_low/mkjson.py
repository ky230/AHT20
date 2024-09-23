import os
import json

# 用于生成浮点数的函数
def frange(start, stop, step):
    while start < stop:
        yield round(start, 1)
        start += step

# 定义文件路径
base_path = "/Users/ky230/Desktop/sensor/AHT20/corrAna/Json/bkp_2/BKP"
moudle_files = [f"Moudle_{i}_origin.txt" for i in [0, 1, 2, 3, 5, 6, 7]]
temperature_range = list(frange(20.90, 27.20, 0.1))  # 生成温度范围

# 提取温度对应的修正值
def find_first_temperature_value(file_path, target_temp):
    with open(file_path, 'r') as file:
        next(file)  # 跳过表头
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 3:  # 确保有足够的列
                temperature = float(parts[2])  # 第三列为温度
                if round(temperature, 1) == target_temp:
                    return temperature
    return None

# 生成修正 JSON 文件
def generate_correction_json():
    corrections = {}
    for target_temp in reversed(temperature_range):  # 降序
        for moudle_file in moudle_files:
            file_path = os.path.join(base_path, moudle_file)
            first_temp = find_first_temperature_value(os.path.join(base_path, "Moudle_4_origin.txt"), target_temp)
            if first_temp is not None:
                current_temp = find_first_temperature_value(file_path, first_temp)
                if current_temp is not None:
                    correction_value = round(current_temp - target_temp, 2)
                    corrections[str(target_temp)] = correction_value
                    break  # 找到一个对应值后就跳出
    return corrections

# 保存 JSON 文件
for i in range(8):
    corrections = generate_correction_json()
    with open(os.path.join(base_path, f"Moudle_{i}.json"), 'w') as json_file:
        json.dump(corrections, json_file, indent=4)

print("温度修正 JSON 文件已生成。")
