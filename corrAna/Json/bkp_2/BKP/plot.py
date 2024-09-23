import sys
import matplotlib.pyplot as plt
from datetime import datetime

def plot_data(filenames):
    plt.figure(figsize=(10, 6))

    # 只使用第一个文件的时间戳作为 x 轴标签
    filename = filenames[0]
    
    with open(filename, 'r') as f:
        lines = f.readlines()[1:]  # 跳过表头
        rows = [line.strip().split() for line in lines]
        
        # 提取时间戳，组合第一列的日期和第二列的时间（这里只使用时间）
        timestamps = [f" {row[1]}" for row in rows]  # 组合日期和时间
        
        # 使用行号作为 x 轴数据
        row_numbers = list(range(len(rows)))

    # 画所有文件的温度数据和湿度数据
    for filename in filenames:
        with open(filename, 'r') as f:
            lines = f.readlines()[1:]  # 跳过表头
            rows = [line.strip().split() for line in lines]
            temperatures = [float(row[2]) for row in rows]
            humidities = [float(row[3]) for row in rows]
            
            now = datetime.now()
            AAA = now.strftime('%Y-%m-%d')

            # 画温度数据
            ax1 = plt.subplot(2, 1, 1)
            plt.plot(row_numbers, temperatures, label=filename.split('.')[0])
            plt.title(f'Temperature Vs Time({AAA})')
            plt.ylabel('Temperature (°C)')
            plt.grid(True)
            ax1.yaxis.set_major_locator(plt.MultipleLocator(0.5))  # 设置纵轴间隔为0.3

            # 画湿度数据
            ax2 = plt.subplot(2, 1, 2)
            plt.plot(row_numbers, humidities, label=filename.split('.')[0])
            plt.title(f'Humidity Vs Time({AAA})')

            plt.ylabel('Humidity (%)')
            plt.grid(True)

    # 设置图例在图的外面右侧
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # 设置图例在温度图的外部
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # 设置图例在湿度图的外部

    # 获取当前的 x 轴刻度，并替换为对应的时间戳
    for ax in [ax1, ax2]:
        current_xticks = [1,7000,14000 ,21000, 28000 ,35000 ,42000 ,49000, 56000 ]   # 获取当前的 x 轴刻度，并确保是整数
        print(f'{current_xticks}')
        new_xticks = [timestamps[i] if i < len(timestamps) else "" for i in current_xticks]  # 替换为对应的时间戳
        ax.set_xticks(current_xticks)
        ax.set_xticklabels(new_xticks, rotation=45, ha='right')  # 应用新的 x 轴刻度标签
        #ax.xaxis.set_major_locator(plt.MaxNLocator(7))  # 限制 x 轴最多显示 7 个刻度

    plt.tight_layout()
    plt.subplots_adjust(right=0.8)  # 调整整体布局，确保图不会被图例挤压
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python plot.py <file1.txt> [<file2.txt> ...]")
    else:
        plot_data(sys.argv[1:])
