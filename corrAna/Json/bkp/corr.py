import os
import json

# # 创建 Corr 文件夹
# corr_folder = "Corr"
# if not os.path.exists(corr_folder):
#     os.makedirs(corr_folder)

# 文件路径
bkp_folder = "/Users/ky230/Desktop/sensor/AHT20/corrAna/Json/bkp"
moudle_names = ["Moudle_0", "Moudle_1", "Moudle_2", "Moudle_3", "Moudle_5", "Moudle_6", "Moudle_7"]

# 加载 JSON 修正文件
def load_json_corrections(moudle_name):
    with open(os.path.join(bkp_folder, f"{moudle_name}.json"), 'r') as f:
        return json.load(f)

# 修正数据的函数
def process_and_correct_moudle_data(moudle_name, corrections, moudle_4_data):
    input_file_path = os.path.join(bkp_folder, f"{moudle_name}_corr.txt")
    output_file_path = os.path.join(bkp_folder, f"{moudle_name}_corrected.txt")

    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        lines = infile.readlines()

        # 写入表头
        outfile.write(lines[0])

        # 从第二行开始处理
        for i, line in enumerate(lines[1:], start=1):
            if i >= len(moudle_4_data):  # 确保不超出 Moudle_4 的行数
                break
            
            parts = line.strip().split()
            m4_temp_str = moudle_4_data[i].strip().split()[2]
            m4_temp = round(float(m4_temp_str), 1)  # 只取一位小数
            
            # 查找对应的修正值
            correction = corrections.get(str(m4_temp), 0)
            
            # 修正温度
            current_temp_str = parts[2]
            corrected_temp = float(current_temp_str) - correction
            parts[2] = f"{corrected_temp:.2f}"  # 保留两位小数

            # 写入修正后的数据
            outfile.write(" ".join(parts) + "\n")

# 读取 Moudle_4 的数据
with open(os.path.join(bkp_folder, "Moudle_4_corr.txt"), 'r') as m4_file:
    m4_data = m4_file.readlines()

# 处理其他 Moudle 文件
for moudle_name in moudle_names:
    if moudle_name != "Moudle_4":
        # 加载对应的 JSON 修正文件
        corrections = load_json_corrections(moudle_name)
        # 修正温度数据
        process_and_correct_moudle_data(moudle_name, corrections, m4_data)


# sensor_mapping = {
#     '0': '6',
#     '1': '4',
#     '2': '2',
#     '3': '0',
#     '4': '7',
#     '5': '5',
#     '6': '3',
#     '7': '1'
# }