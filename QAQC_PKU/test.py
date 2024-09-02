import tkinter as tk
import subprocess
import os
import signal
import threading
import glob
import re
import sys

# 创建主窗口
root = tk.Tk()
root.title("AHT20 Monitoring")

# 定义全局变量
aht20_process = None
timestamp = None

# 创建主框架
frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.TOP, padx=10, pady=10)

frame_temps = tk.Frame(root)
frame_temps.pack(side=tk.TOP, padx=10, pady=10)

# 函数：读取最新的 AHT20 数据并更新 GUI
def read_AHT20():
    base_path_pattern = '/home/pkumtd/Desktop/AHT20/QAQC_PKU_*'
    folders = glob.glob(base_path_pattern)
    
    if not folders:
        print("No data folders found.")
        return

    latest_folder = max(folders, key=os.path.getmtime)
    print(f"Using latest folder: {latest_folder}")

    file_paths = glob.glob(f'{latest_folder}/AHT20_*_*.txt')
    average_files = glob.glob(f'{latest_folder}/average_*.txt')

    latest_data = {i: {"timestamp": None, "temperature": None, "humidity": None} for i in range(8)}

    for file_path in file_paths:
        print(f"Processing file: {file_path}")
        
        match = re.search(r'AHT20_(\d+)_\d+\.txt$', file_path)
        if match:
            sensor_id = int(match.group(1))
        else:
            print(f"Error extracting sensor ID from file path {file_path}")
            continue

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()
                if lines:
                    lines = lines[1:]  # Skip header

                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        timestamp = f"{parts[0]} {parts[1]}"
                        temperature = parts[2]
                        humidity = parts[3]
                        
                        temperature_value = float(temperature.replace('°C', ''))
                        humidity_value = float(humidity.replace('%', ''))
                        
                        latest_data[sensor_id]["timestamp"] = timestamp
                        latest_data[sensor_id]["temperature"] = temperature
                        latest_data[sensor_id]["humidity"] = humidity
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    for i, data in latest_data.items():
        if i in AHT20_text:
            text_widget = AHT20_text[i]
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"AHT20_{i}:\n", 'bold')
            text_widget.insert(tk.END, f"Timestamp: {data['timestamp'] if data['timestamp'] else '--'}\n")
            text_widget.insert(tk.END, f"Temperature (°C): {data['temperature'] if data['temperature'] else '--'}\n")
            text_widget.insert(tk.END, f"Humidity (%): {data['humidity'] if data['humidity'] else '--'}\n")
            text_widget.config(state=tk.DISABLED)

    avg_timestamp = '--'
    avg_temp = '--'
    avg_humidity = '--'

    for average_file in average_files:
        try:
            with open(average_file, 'r') as file:
                lines = file.readlines()
                print(f"Open Average file successfully: {average_file}")

                if lines:
                    lines = lines[1:]  # Skip header
                    
                    if lines:
                        last_line = lines[-1].strip()
                        parts = last_line.split()
                        if len(parts) >= 3:
                            avg_timestamp = f"{parts[0]} {parts[1]}"
                            avg_temp = parts[2]
                            avg_humidity = parts[3]
        except Exception as e:
            print(f"Error opening average file {average_file}: {e}")

    print(f"AHT20_text keys: {AHT20_text.keys()}")
    if 8 in AHT20_text:
        average_widget = AHT20_text[8]
        average_widget.config(state=tk.NORMAL)
        average_widget.delete(1.0, tk.END)
        average_widget.insert(tk.END, "Average:\n", 'bold')
        average_widget.insert(tk.END, f"Timestamp: {avg_timestamp}\n")
        average_widget.insert(tk.END, f"Temperature (°C): {avg_temp}\n")
        average_widget.insert(tk.END, f"Humidity (%): {avg_humidity}\n")
        average_widget.config(state=tk.DISABLED)
    else:
        print("Error: Average widget (index 8) not found.")

    root.after(2000, read_AHT20)  # 每2秒更新一次

def start_AHT20_monitoring():
    global aht20_process

    if aht20_process is not None:
        os.killpg(os.getpgid(aht20_process.pid), signal.SIGINT)
        aht20_process.wait()

    def run_script():
        global aht20_process

        try:
            current_time = subprocess.check_output("date +\"%Y%m%d%H%M%S\"", shell=True).decode().strip()
            print(f"Current timestamp: {current_time}")

            aht20_process = subprocess.Popen(
                ["python3", "/home/pkumtd/Desktop/AHT20/TCA9548A.py", current_time, '1'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )

            stdout, stderr = aht20_process.communicate()
            timestamp = stdout.decode().strip()
            print(f"Timestamp from script: {timestamp}")
            print(f"stderr from script: {stderr.decode()}")

            if timestamp:
                read_AHT20()
            else:
                print("Failed to get timestamp from script.")
        except Exception as e:
            print(f"Error starting TCA9548A.py: {e}")

    threading.Thread(target=run_script).start()

def Test_AHT20_monitoring():
    global aht20_process

    if aht20_process is not None:
        os.killpg(os.getpgid(aht20_process.pid), signal.SIGINT)
        aht20_process.wait()

    def run_script():
        global aht20_process

        try:
            current_time = subprocess.check_output("date +\"%Y%m%d%H%M%S\"", shell=True).decode().strip()
            print(f"Current timestamp: {current_time}")

            aht20_process = subprocess.Popen(
                ["python3", "/home/pkumtd/Desktop/AHT20/TCA9548A.py", current_time, '0'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )

            stdout, stderr = aht20_process.communicate()
            timestamp = stdout.decode().strip()
            print(f"Timestamp from script: {timestamp}")
            print(f"stderr from script: {stderr.decode()}")

            if timestamp:
                read_AHT20()
            else:
                print("Failed to get timestamp from script.")
        except Exception as e:
            print(f"Error starting TCA9548A.py: {e}")

    threading.Thread(target=run_script).start()

def stop_AHT20_monitoring():
    global aht20_process

    if aht20_process is not None:
        os.killpg(os.getpgid(aht20_process.pid), signal.SIGINT)
        aht20_process.wait()
        aht20_process = None

def on_closing_AHT20():
    global aht20_process
    if aht20_process is not None:
        os.killpg(os.getpgid(aht20_process.pid), signal.SIGINT)
        aht20_process.wait()
    root.destroy()





def draw_AHT20_monitoring():
    def on_ok():
        selected_ids = [var.get() for var in check_vars if var.get() != '']
        if selected_ids:
            sensor_list = ' '.join(selected_ids)
            print(f"Selected sensors: {sensor_list}")

            # 检查是否选择保存图表
            save_option = save_var.get()

            # 获取最新的文件夹
            folders = glob.glob('/home/pkumtd/Desktop/AHT20/QAQC_PKU_*')
            latest_folder = find_latest_folder(folders)

            # 获取当前时间戳
            timestamp = subprocess.check_output("date +\"%Y%m%d%H%M%S\"", shell=True).decode().strip()

            if save_option:
                # 构造保存路径，并用引号包裹
                save_path = os.path.join(latest_folder, f'Plots_{timestamp}.png')
                command = f"python3 /home/pkumtd/Desktop/AHT20/drawplot.py {sensor_list} \"({save_path})\""
            else:
                # 不保存图表
                command = f"python3 /home/pkumtd/Desktop/AHT20/drawplot.py {sensor_list}"
            
            subprocess.Popen(
                [command],
                shell=True,
                preexec_fn=os.setsid
            )
        else:
            print("No sensors selected.")

    def on_cancel():
        sensor_window.destroy()

    # 创建选择传感器的窗口
    sensor_window = tk.Toplevel(root)
    sensor_window.title("Select Sensors")

    # 获取传感器选项
    folders = glob.glob('/home/pkumtd/Desktop/AHT20/QAQC_PKU_*')
    latest_folder = find_latest_folder(folders)
    available_files = glob.glob(f'{latest_folder}/AHT20_*_*.txt') + glob.glob(f'{latest_folder}/average_*.txt')
    sensor_options = sorted(set(re.search(r'AHT20_(\d+)', file).group(0) for file in available_files if re.search(r'AHT20_(\d+)', file)) | {'average'})

    # 创建复选框
    check_vars = []
    for option in sensor_options:
        var = tk.StringVar()
        check_vars.append(var)
        tk.Checkbutton(sensor_window, text=option, variable=var, onvalue=option, offvalue='').pack(anchor=tk.W)

    # 创建保存选项复选框
    save_var = tk.BooleanVar()
    save_checkbox = tk.Checkbutton(sensor_window, text="Save Plot", variable=save_var)
    save_checkbox.pack(anchor=tk.W)
    
    # 设置加粗字体
    save_checkbox.config(font=('Helvetica', 11, 'bold'))

    # 创建输入框
    input_box = tk.Entry(sensor_window, width=50)
    input_box.pack(padx=10, pady=10)

    def update_input(*args):
        selected = [var.get() for var in check_vars if var.get() != '']
        input_box.delete(0, tk.END)
        input_box.insert(0, ' '.join(selected))

    for var in check_vars:
        var.trace_add("write", update_input)

    # 创建按钮
    button_frame = tk.Frame(sensor_window)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=10)  # 修改为side=tk.LEFT，使其在同一行

def find_latest_folder(folders):
    return max(folders, key=os.path.getmtime)

# 设置按钮
button_module = tk.Button(master=frame_buttons, text="Tem&Hum Monitoring", width=25, height=5, command=start_AHT20_monitoring)
button_module.pack()

button_plot = tk.Button(master=frame_buttons, text="Plotting Tem&Hum Monitoring", width=25, height=5, command=draw_AHT20_monitoring)
button_plot.pack()

button_stop = tk.Button(master=frame_buttons, text="Stop Tem&Hum Monitoring", width=25, height=5, command=stop_AHT20_monitoring)
button_stop.pack()

button_test = tk.Button(master=frame_buttons, text="Test Tem&Hum Monitoring", width=25, height=5, command=Test_AHT20_monitoring)
button_test.pack()

# 设置标签
num_columns = 2
rows = (8 + num_columns - 1) // num_columns + 1
bold_font = ('Helvetica', 11, 'bold')
normal_font = ('Helvetica', 10)

AHT20_text = {}

for row in range(rows):
    row_frame = tk.Frame(frame_temps)
    row_frame.pack()

    for col in range(num_columns):
        i = row * num_columns + col

        if i < 8:
            text_widget = tk.Text(row_frame, height=4, width=40, wrap=tk.WORD, font=normal_font, bd=0, bg=row_frame.cget('bg'))
            text_widget.insert(tk.END, f"AHT20_{i}:\n", 'bold')
            text_widget.insert(tk.END, f"Timestamp: -- \n", 'normal')
            text_widget.insert(tk.END, f"Temperature (°C): --\n", 'normal')
            text_widget.insert(tk.END, f"Humidity (%): --\n", 'normal')

            text_widget.tag_add('bold', '1.0', '1.8')
            text_widget.tag_configure('bold', font=bold_font)
            text_widget.tag_add('normal', '2.0', tk.END)
            text_widget.tag_configure('normal', font=normal_font)

            text_widget.config(state=tk.DISABLED)
            text_widget.pack(side=tk.LEFT)
            
            AHT20_text[i] = text_widget

        elif i == 8:
            average_text_widget = tk.Text(row_frame, height=4, width=40, wrap=tk.WORD, font=normal_font, bd=0, bg=row_frame.cget('bg'))
            average_text_widget.insert(tk.END, "Average:\n", 'bold')
            average_text_widget.insert(tk.END, "Timestamp: -- \n", 'normal')
            average_text_widget.insert(tk.END, "Temperature (°C): --\n", 'normal')
            average_text_widget.insert(tk.END, "Humidity (%): --\n", 'normal')

            average_text_widget.tag_add('bold', '1.0', '1.8')
            average_text_widget.tag_configure('bold', font=bold_font)
            average_text_widget.tag_add('normal', '2.0', tk.END)
            average_text_widget.tag_configure('normal', font=normal_font)

            average_text_widget.config(state=tk.DISABLED)
            average_text_widget.pack(side=tk.LEFT)

            AHT20_text[i] = average_text_widget

root.protocol("WM_DELETE_WINDOW", on_closing_AHT20)

# 启动主循环
root.mainloop()
