import os
import json

# 创建 Corr 文件夹
corr_folder = "Corr"
if not os.path.exists(corr_folder):
    os.makedirs(corr_folder)

# 原始文件和 JSON 修正文件的映射
moudle_files = {
    "Moudle_0": "Moudle_0_origin.txt",
    # "Moudle_1": "Moudle_1_origin.txt",
    # "Moudle_2": "Moudle_2_origin.txt",
    # "Moudle_3": "Moudle_3_origin.txt",
    # "Moudle_5": "Moudle_5_origin.txt",
    # "Moudle_6": "Moudle_6_origin.txt",
    # "Moudle_7": "Moudle_7_origin.txt",
    "Moudle_4": "Moudle_4_origin.txt"  # Moudle_4 也需要复制
}

# 加载 JSON 修正文件
def load_json_corrections(moudle_name):
    with open(f"{moudle_name}.json", 'r') as f:
        return json.load(f)

# 修正并处理数据的函数
def process_and_correct_moudle_data(moudle_name, moudle_file, corrections):
    with open(moudle_file, 'r') as infile, open(f"{corr_folder}/{moudle_name}_Corr.txt", 'w') as outfile:
        lines = infile.readlines()

        # 写入表头
        outfile.write(lines[0])

        # 跳到第 8508 行开始处理
        for i, line in enumerate(lines[8508:], start=8508):
            parts = line.strip().split()

            # 确保数据格式正确
            if len(parts) == 4:
                timestamp, temp_str, humidity_str = parts[0] + " " + parts[1], parts[2], parts[3]
                current_temp = float(temp_str)

             
                if moudle_name != "Moudle_4":
                    with open(f"{corr_folder}/Moudle_4_Corr.txt", 'r') as m4_file:
                        m4_lines = m4_file.readlines()

                        # 查找对应的行
                        if i < len(m4_lines):  # 确保索引有效
                            m4_temp_str = m4_lines[i].strip().split()[2]
                            m4_temp = float(m4_temp_str)

                            # 在修正字典中查找对应的温度
                            correction = corrections.get(str(m4_temp), 0)

                            # 修正温度
                            corrected_temp = round(current_temp - correction, 2)
                            parts[2] = f"{corrected_temp:.2f}"

                # 写入修正后的数据
                outfile.write(" ".join(parts) + "\n")

# 首先生成 Moudle_4_Corr.txt
with open(moudle_files["Moudle_4"], 'r') as infile, open(f"{corr_folder}/Moudle_4_Corr.txt", 'w') as outfile:
    lines = infile.readlines()

    # 写入表头
    outfile.write(lines[0])

    # 从第 8508 行开始复制数据
    for line in lines[8508:]:
        outfile.write(line)

# 处理其他 Moudle 文件
for moudle_name, moudle_file in moudle_files.items():
    if moudle_name != "Moudle_4":

        corrections = load_json_corrections(moudle_name)

        process_and_correct_moudle_data(moudle_name, moudle_file, corrections)
