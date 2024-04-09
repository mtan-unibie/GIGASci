import json
import os
import shutil

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def create_folders(data):
    for item in data:
        for key in item.keys():
            folder_path = os.path.join('Test', key)
            os.makedirs(folder_path, exist_ok=True)

def copy_files(data):
    for item in data:
        for key, file_list in item.items():
            for file_name in file_list:
                source_path = os.path.join('diatom', file_name)
                target_path = os.path.join('Test', key, file_name)
                shutil.copyfile(source_path, target_path)

def main():
    data = read_json_file('data.json')
    create_folders(data)
    copy_files(data)

if __name__ == "__main__":
    main()
