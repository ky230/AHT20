import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def plot_data(file_paths):
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"文件 {file_path} 不存在.")
            continue

        # 读取数据，跳过表头（1行）
        sensor_data = pd.read_csv(file_path, sep='\s+', header=0, skiprows=1)

        # 画温度（第三列）
        axs[0].plot(sensor_data.index, sensor_data.iloc[:, 1], linestyle='-', marker=None, 
                    label=os.path.basename(file_path).replace('_Corr.txt', ''), linewidth=1)

        # 画湿度（第四列）
        axs[1].plot(sensor_data.index, sensor_data.iloc[:, 2], linestyle='-', marker=None, 
                    label=os.path.basename(file_path).replace('_Corr.txt', ''), linewidth=1)

    # 设置 X 轴刻度
    for ax in axs:
        ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=7))

    axs[0].set_title('Temperature over Time')
    axs[0].set_ylabel('Temperature (°C)')
    axs[1].set_title('Humidity over Time')
    axs[1].set_ylabel('Humidity (%)')

    # 添加图例
    axs[0].legend()
    axs[1].legend()

    plt.tight_layout()

    # 保存图形
    plt.savefig('sensor_data_plot.png', dpi=300)  # 保存为 PNG 文件，分辨率为 300 dpi
    # plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("请提供至少一个数据文件的路径.")
        sys.exit(1)

    file_paths = sys.argv[1:]
    plot_data(file_paths)
