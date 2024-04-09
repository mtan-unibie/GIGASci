import json
import os
import shutil

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        json_string = f.read()
        # Convert the JSON string to a dictionary
        data = json.loads(json_string)
    return data

def create_folders(data):
    for key, file_list in data.items():
        folder_path = os.path.join('Testset', key)
        os.makedirs(folder_path, exist_ok=True)

def copy_files(data):
    for key, file_list in data.items():
        for file_name in file_list:
            source_path = os.path.join('UDE Diatoms in the Wild 2024/images', file_name)
            target_path = os.path.join('Testset', key, file_name)
            shutil.copyfile(source_path, target_path)

def main():
    data = read_json_file('testset.json')
    print(data)
    create_folders(data)
    copy_files(data)

if __name__ == "__main__":
    main()
