import sys
import matplotlib.pyplot as plt
import numpy as np

def plot_data(filenames):
    plt.figure(figsize=(10, 6))

    for filename in filenames:
        with open(filename, 'r') as f:
            lines = f.readlines()[1:]  # 跳过表头
            rows = [line.strip().split() for line in lines]
            row_numbers = list(range(len(rows)))
            temperatures = [float(row[2]) for row in rows]
            humidities = [float(row[3]) for row in rows]

            # 画温度数据
            plt.subplot(2, 1, 1)
            plt.plot(row_numbers, temperatures, label=filename.split('.')[0])
            plt.title('Temperature over Row Numbers')
            plt.xlabel('Row Number')
            plt.ylabel('Temperature (°C)')
            plt.legend()
            
            # 设置温度图的网格，纵坐标间距为0.3
            plt.grid(True)
            plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.3))  # 设置纵轴间隔为0.3
            
            # 画湿度数据
            plt.subplot(2, 1, 2)
            plt.plot(row_numbers, humidities, label=filename.split('.')[0])
            plt.title('Humidity over Row Numbers')
            plt.xlabel('Row Number')
            plt.ylabel('Humidity (%)')
            plt.legend()

            # 设置湿度图的网格，但不要求特定纵轴间距
            plt.grid(True)

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python plot.py <file1.txt> [<file2.txt> ...]")
    else:
        plot_data(sys.argv[1:])
