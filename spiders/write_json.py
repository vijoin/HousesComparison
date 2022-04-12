import json

def write_to_json_file(filename, data_dict):
    with open(filename, 'w', newline='') as f:
        json.dump(data_dict, f, ensure_ascii=False)