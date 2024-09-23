import sys
import matplotlib.pyplot as plt
from datetime import datetime

def plot_data(filenames, origin_file):
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

    # 读取 Moudle_4_Origin.txt 中的温度数据
    with open(origin_file, 'r') as f:
        origin_lines = f.readlines()[1:]  # 跳过表头
        origin_rows = [line.strip().split() for line in origin_lines]
        origin_temperatures = [float(row[2]) for row in origin_rows]

    # 画所有文件的温度数据
    for filename in filenames:
        with open(filename, 'r') as f:
            lines = f.readlines()[1:]  # 跳过表头
            rows = [line.strip().split() for line in lines]
            temperatures = [float(row[2]) for row in rows]
            
            now = datetime.now()
            AAA = now.strftime('%Y-%m-%d')

            # 画温度数据
            ax1 = plt.subplot(2, 1, 1)
            plt.plot(row_numbers, temperatures, label=filename.split('.')[0])
            plt.title(f'Temperature Vs Time({AAA})')
            plt.ylabel('Temperature (°C)')
            plt.grid(True)
            ax1.yaxis.set_major_locator(plt.MultipleLocator(0.5))  # 设置纵轴间隔为0.5

            # 画温度差值
            ax2 = plt.subplot(2, 1, 2)
            temp_diff = [t - o for t, o in zip(temperatures, origin_temperatures)]
            plt.plot(row_numbers, temp_diff, label=f'{filename.split(".")[0]} - Origin')
            plt.ylabel('Temperature Difference (°C)')
            plt.grid(True)

            # 设置纵坐标范围为 [-0.3, 0.3]，并设置网格间隔为 0.1
            ax2.set_ylim([-0.5, 0.5])
            ax2.yaxis.set_major_locator(plt.MultipleLocator(0.1))
            plt.title(f'Temperature Difference ({AAA})')

    # 设置图例在图的外面右侧
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # 设置图例在温度图的外部
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))  # 设置图例在温度差图的外部

    # 获取当前的 x 轴刻度，并替换为对应的时间戳
    for ax in [ax1, ax2]:
        current_xticks = [1,700,1400,2100,2800,3500]
        new_xticks = [timestamps[i] if i < len(timestamps) else "" for i in current_xticks]  # 替换为对应的时间戳
        ax.set_xticks(current_xticks)
        ax.set_xticklabels(new_xticks, rotation=45, ha='right')  # 应用新的 x 轴刻度标签

    # 缩小第二个子图的高度
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.6, right=0.8)  # 调整子图间距和右侧图例位置
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python plot.py <file1.txt> [<file2.txt> ...] <origin_file.txt>")
    else:
        origin_file = sys.argv[-1]
        plot_data(sys.argv[1:-1], origin_file)