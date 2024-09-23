import os
import shutil

# 创建 bkp 文件夹
bkp_folder = "bkp"
if not os.path.exists(bkp_folder):
    os.makedirs(bkp_folder)

# 遍历当前目录中的所有 Moudle_*_origin.txt 文件
for filename in os.listdir('.'):
    if filename.startswith('Moudle_') and filename.endswith('_origin.txt'):
        new_filename = filename.replace('_origin.txt', '_corr.txt')

        with open(filename, 'r') as infile, open(os.path.join(bkp_folder, new_filename), 'w') as outfile:
            lines = infile.readlines()

            # 写入表头
            outfile.write(lines[0])

            # 从第 8588 行开始复制数据
            for line in lines[8588:]:
                outfile.write(line)

print("文件已成功复制到 bkp 文件夹。")
