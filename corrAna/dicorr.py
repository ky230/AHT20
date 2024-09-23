import shutil
import os

# Temperature corrections for each module
corrections = {
    'Moudle_6': -0.4,
    'Moudle_4': 0,
    'Moudle_2': 0.3,
    'Moudle_0': 0.3,
    'Moudle_7': 0.2,
    'Moudle_5': -0.1,
    'Moudle_3': 1,
    'Moudle_1': -0.1
}

# Function to remove correction and save to a new file
def undo_correction(filename, correction):
    # Copy original file to a backup
    origin_filename = filename.replace('.txt', '_origin.txt')
    shutil.copy(filename, origin_filename)

    # Open the original file and the new file for writing
    with open(filename, 'r') as original_file, open(origin_filename, 'w') as new_file:
        for line in original_file:
            if "Timestamp" in line:  # Keep the header unchanged
                new_file.write(line)
                continue
            parts = line.strip().split()  # Split line by whitespace
            if len(parts) >= 3:
                timestamp, temperature, humidity = parts[0], float(parts[2]), parts[3]
                # Remove the correction
                new_temperature = temperature + correction
                new_file.write(f"{parts[0]} {parts[1]} {new_temperature:.2f} {humidity}\n")

# List all files in the current directory and process them
for filename in os.listdir():
    if filename.startswith('Moudle_') and filename.endswith('.txt'):
        module_name = filename.split('.')[0]
        if module_name in corrections:
            undo_correction(filename, corrections[module_name])

print("Correction undoing completed.")
