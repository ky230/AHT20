import os
import subprocess
import glob
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
from datetime import datetime
import numpy as np



# 传感器ID映射关系
sensor_mapping = {
    '0': '6',
    '1': '4',
    '2': '2',
    '3': '0',
    '4': '7',
    '5': '5',
    '6': '3',
    '7': '1'
}

def map_sensor_id(sensor_id):
    """根据传感器ID进行映射"""
    return sensor_mapping.get(sensor_id, sensor_id)

def find_latest_folder(folders):
    """查找最新的文件夹"""
    if not folders:
        return None
    latest_folder = max(folders, key=os.path.getmtime)
    return latest_folder

def find_files_in_folder(folder, pattern):
    """在指定文件夹中查找符合模式的文件"""
    return glob.glob(os.path.join(folder, pattern))

def read_data(file_path):
    """读取数据文件"""
    print(f"Reading data from {file_path}")
    try:
        data = pd.read_csv(file_path, sep='\s+', header=0, parse_dates=['Timestamp'])
        data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')
        if data.empty:
            print(f"No data found in {file_path}")
        else:
            print(f"Data read from {file_path}:")
            print(data.head())  # 打印前几行数据进行检查
        return data
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def plot_data(sensor_list, save_path=None):
    folders = glob.glob('/home/pkumtd/Desktop/AHT20/QAQC_PKU_*')
    latest_folder = find_latest_folder(folders)
    if not latest_folder:
        print("No folders found.")
        return None
    
    print(f"Latest folder: {latest_folder}")

    # 创建图形和轴，2行1列布局
    fig, axs = plt.subplots(2, 1, figsize=(12, 10))

    def update(frame):
        # 清空图表
        for ax in axs:
            ax.clear()

        # 遍历传感器列表，绘制相应数据
        for sensor in sensor_list:
            if sensor.lower() == 'average':
                average_files = find_files_in_folder(latest_folder, 'average_*.txt')
                print(f"Average files found: {average_files}")
                
                if average_files:
                    avg_data = read_data(average_files[0])
                    
                    if not avg_data.empty:
                        avg_data = avg_data.reset_index(drop=True)  
                        
                        
                        corrected_temperature = []
                        corrected_humidity = []
                        
                        # 设置初始值
                        prev_temperature = avg_data['Temperature(°C)'].iloc[0]
                        prev_humidity = avg_data['Humidity(%)'].iloc[0]

                        # 修正温度和湿度数据
                        for i in range(len(avg_data)):
                            curr_temperature = avg_data['Temperature(°C)'].iloc[i]
                            curr_humidity = avg_data['Humidity(%)'].iloc[i]
                            
                            # 检查温度变化是否大于0.1%
                            if abs(curr_temperature - prev_temperature) > 0.001 * prev_temperature:
                                curr_temperature = prev_temperature  
                            
                            # # 检查湿度变化是否大于0.1%
                            # if abs(curr_humidity - prev_humidity) > 0.001 * prev_humidity:
                            #     curr_humidity = prev_humidity  
                            
                            
                            corrected_temperature.append(curr_temperature)
                            corrected_humidity.append(curr_humidity)
                            
                            
                            prev_temperature = curr_temperature
                            prev_humidity = curr_humidity
                        
                     
                        axs[0].plot(avg_data.index, corrected_temperature, linestyle='-', marker=None, label='Average Temperature', linewidth=1)
                        axs[1].plot(avg_data.index, corrected_humidity, linestyle='-', marker=None, label='Average Humidity ', linewidth=1)

                        xticks = axs[0].get_xticks().astype(int)  
                        valid_xticks = xticks[(xticks >= 0) & (xticks < len(avg_data))]  

                        time_labels = avg_data['Timestamp'].iloc[valid_xticks].dt.strftime('%H:%M:%S')

                        axs[0].set_xticks(valid_xticks)  
                        axs[0].set_xticklabels(time_labels, rotation=45, ha='right')
                        axs[0].xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
    

                        axs[1].set_xticks(valid_xticks) 
                        axs[1].set_xticklabels(time_labels, rotation=45, ha='right')
                        axs[1].legend(loc='upper left', bbox_to_anchor=(1.1, 1.0), fontsize='small')
                        axs[1].xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
            else:
                sensor_files = find_files_in_folder(latest_folder, f'{sensor}_*.txt')
                if sensor_files:
                    sensor_data = read_data(sensor_files[0])
                    if not sensor_data.empty:
                        sensor_data = sensor_data.reset_index(drop=True)

                        sensor_id = sensor.split('_')[1]
                        module_id = map_sensor_id(sensor_id)

                        axs[0].plot(sensor_data.index, sensor_data['Temperature(°C)'], linestyle='-', marker=None, label=f'MOD_board_{module_id}', linewidth=1)
                        axs[1].plot(sensor_data.index, sensor_data['Humidity(%)'], linestyle='-', marker=None, label=f'MOD_board_{module_id}', linewidth=1)

                        xticks = axs[0].get_xticks().astype(int)  
                        valid_xticks = xticks[(xticks >= 0) & (xticks < len(sensor_data))]  

                        time_labels = sensor_data['Timestamp'].iloc[valid_xticks].dt.strftime('%H:%M:%S')

                        axs[0].set_xticks(valid_xticks)  
                        axs[0].set_xticklabels(time_labels, rotation=45, ha='right')
                        axs[0].xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
    

                        axs[1].set_xticks(valid_xticks) 
                        axs[1].set_xticklabels(time_labels, rotation=45, ha='right')
                        axs[1].legend(loc='upper left', bbox_to_anchor=(1.1, 1.0), fontsize='small')
                        axs[1].xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))

        # 获取当前时间用于标题
        now = datetime.now()
        AAA = now.strftime('%Y-%m-%d')

        # 设置温度图的属性
        axs[0].grid(True)
        axs[0].set_ylabel('Temperature (°C)')
        axs[0].set_title(f'Temperature vs Time ({AAA})')
        #axs[0].set_xlabel('Row Number')
        axs[0].legend(loc='upper left', bbox_to_anchor=(1.1, 1.0), fontsize='small')
        axs[0].xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
        axs[0].tick_params(axis='x', rotation=45)
        axs[0].yaxis.set_major_locator(ticker.MultipleLocator(0.3))
        axs[0].set_ylim(22, 24)


        # 设置湿度图的属性
        axs[1].grid(True)
        axs[1].set_ylabel('Humidity (%)')
        axs[1].set_title(f'Humidity vs Time ({AAA})')
        #axs[1].set_xlabel('Row Number')
        axs[1].legend(loc='upper left', bbox_to_anchor=(1.1, 1.0), fontsize='small')
        axs[1].tick_params(axis='x', rotation=45)

        axs[1].xaxis.set_major_locator(ticker.MaxNLocator(nbins=7)) 
        axs[1].yaxis.set_major_locator(ticker.MultipleLocator(1))

        plt.tight_layout()

    # 使用 FuncAnimation 实现实时更新
    ani = FuncAnimation(fig, update, interval=1000)  # 每秒更新一次

    # 显示图形
    plt.show()

    # 保存图形
    if save_path:
        try:
            save_path = save_path.strip('()')  # 去掉路径中的括号
            fig.savefig(save_path)
            print(f"Figure saved to {save_path}")
        except Exception as e:
            print(f"Error saving figure: {e}")

if __name__ == '__main__':
    # 获取命令行参数
    if len(sys.argv) > 1:
        # 从命令行参数中提取传感器列表和保存路径
        sensor_list = []
        save_path = None

        # 检查是否包含括号包裹的保存路径
        if '(' in sys.argv[-1] and ')' in sys.argv[-1]:
            save_path = sys.argv[-1]
            # 去掉括号
            save_path = save_path.strip('()')
            sensor_list = sys.argv[1:-1]
        else:
            sensor_list = sys.argv[1:]
        
        # 打印参数以调试
        print(f"Sensor list: {sensor_list}")
        print(f"Save path: {save_path}")
        
        plot_data(sensor_list, save_path)
    else:
        print("No command line arguments provided.")
