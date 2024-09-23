#!/bin/bash

# 遍历当前目录下所有*_corr.txt文件
for file in *_corr.txt; do
    # 检查文件是否存在
    if [[ -e "$file" ]]; then
        # 使用参数替换来修改文件名
        mv "$file" "${file/_corr/_Origin}"
        echo "Renamed: $file to ${file/_corr/_Origin}"
    fi
done


# python3 plot.py Moudle_0_Origin.txt Moudle_1_Origin.txt Moudle_2_Origin.txt Moudle_3_Origin.txt Moudle_4_Origin.txt Moudle_5_Origin.txt Moudle_6_Origin.txt Moudle_7_Origin.txt 

