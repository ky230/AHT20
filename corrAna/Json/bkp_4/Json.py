import json

# 文件路径
json_file_path = '/Users/ky230/Desktop/sensor/AHT20/corrAna/Json/bkp_4/bkp/Moudle_1.json'

# 读取 JSON 文件
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

# 将每个值乘以 -2
updated_data = {key: round(value * 1 + 0.07 , 2) for key, value in data.items()}

# 将更新后的数据写回 JSON 文件
with open(json_file_path, 'w') as json_file:
    json.dump(updated_data, json_file, indent=4)

print(f"Updated values in {json_file_path}")
