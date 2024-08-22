import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

# 设置目录路径
directory_path = '/Users/ky230/Desktop/sensor/AHT20'

def find_latest_file(directory):
    # 查找目录下最新的txt文件
    txt_files = [f for f in os.listdir(directory) if f.endswith('.txt')]
    if not txt_files:
        return None
    latest_file = max(txt_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
    return os.path.join(directory, latest_file)

def read_data(file_path):
    # 读取数据
    data = pd.read_csv(file_path, delim_whitespace=True, header=0, parse_dates=['Timestamp'])
    # 确保 'Timestamp' 列为 datetime 类型
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')
    return data

def plot_data():
    # 查找最新的文件
    latest_file = find_latest_file(directory_path)
    if latest_file:
        data = read_data(latest_file)
    else:
        print("No .txt files found.")
        return None

    # 创建图形和轴
    fig, axs = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    def update(frame):
        # 读取最新数据
        latest_file = find_latest_file(directory_path)
        if latest_file:
            data = read_data(latest_file)
        else:
            return

        # 清空图表
        for ax in axs:
            ax.clear()

        # 上面一幅图：时间戳 vs Temperature
        axs[0].plot(data['Timestamp'], data['Temperature(°C)'], marker='o', linestyle='-', color='r')
        axs[0].set_ylabel('Temperature (°C)')
        axs[0].set_title('Temperature vs Time')
        axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        axs[0].xaxis.set_major_locator(mdates.HourLocator(interval=1))
        axs[0].tick_params(axis='x', rotation=45)

        # 下面一幅图：时间戳 vs Humidity
        axs[1].plot(data['Timestamp'], data['Humidity(%)'], marker='o', linestyle='-', color='b')
        axs[1].set_xlabel('Time')
        axs[1].set_ylabel('Humidity (%)')
        axs[1].set_title('Humidity vs Time')
        axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        axs[1].xaxis.set_major_locator(mdates.HourLocator(interval=1))
        axs[1].tick_params(axis='x', rotation=45)

        plt.tight_layout()

    # 使用 FuncAnimation 实现实时更新
    ani = FuncAnimation(fig, update, interval=1000)  # 每秒更新一次

    plt.show()

if __name__ == '__main__':
    plot_data()
