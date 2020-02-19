import hashlib
import os
from random import choice
from string import ascii_letters
import argparse
import json
from collections import namedtuple
import magic

class ClientError(Exception):
    pass 

def _clear_dir(path):
    file_list = [f for f in os.listdir(path)]
    print("Accept remove files form path {}".format(path))
    answer = input("[y/n]")
    if answer == "y":
        for f in file_list:
            os.remove(os.path.join(path, f))

def _get_hash_md5(block):
    if block is not None:
        m = hashlib.md5()
        m.update(block)
        return m.hexdigest()

def _read_file_to_array(dir_filename, volume_bytes):
    array = []
    with open(dir_filename, 'rb') as f:
        while True:
            data = f.read(volume_bytes)
            array.append(data)
            if not data:
                break
        return array
    
def _read_file(dir_filename):
    with open(dir_filename, 'rb') as f:
        while True:
            data = f.read()
            return data

def _save_file(dir_filename, text, type_w):
    with open(dir_filename, type_w) as f:
        f.write(text)

def _random_word():
    return ''.join(choice(ascii_letters) for i in range(8))

def read_config(_path):
    _json_config = {
        'working_file' : 'machine.jpg',
        'current_path' : _path,
        'N' : 1024,
        'file_md5' : "_order.md5",
        'file_config' : "config.txt"
    }
    _config = namedtuple('field',_json_config.keys())(*_json_config.values())
    _path_config = os.path.join(_path, "config.txt")
    try:
        if not os.path.exists(_path_config):
            return _config
        with open(_path_config, 'r') as file:
            raw_data = file.read()
            if raw_data:
                _json_config = json.loads(raw_data)
                _config = namedtuple('field',_json_config.keys())(*_json_config.values())
                return _config
    except:
        return ClientError
           
def write_config(_config):
    with open(os.path.join(_config.current_path, 'config.txt'),'w') as f:
        f.write(json.dumps(_config._asdict()))

def parse_command():
    _list_commands = ("split", "join")
    parser = argparse.ArgumentParser(description='Описание скрипта')
    parser.add_argument('--c', action='store', required=True, dest='command', type=str, help='Command') #split join
    _args = parser.parse_args()
    if _args.command in _list_commands:
        return _args.command
    else:
        raise ClientError
    



def split_file(current_path, working_file, N, order_file):
    """Split file on split size N"""
    _clear_dir(current_path + '/files')
    
    # 1 побайтово прочитали файл, разбив его на отдельные блоки по N байта
    byte_file = _read_file_to_array(current_path + '/' + working_file, N)

    # 2 получили хеши блоков данных в правильном порядке
    hex_files = list(map(_get_hash_md5,byte_file))

    # 3 сохранили эти хеши в правильном порядке в файл "order.md5"
    array = [str(i) + "\n" for i in hex_files]
    s = "".join(array)
    path2 = current_path + "/" + order_file
    _save_file(path2, s, 'w')

    # 4 сохраним в отдельные файлы блоки данных с рандомными именами
    for i in enumerate(byte_file):
        _save_file(current_path + "/files" + '/' + f"{i[0]:03}" + " " + _random_word() + ".xex", i[1], 'wb')

    return len(byte_file)

def join_file(current_path, order_file, result_file):
    """Create file from file-slits"""
    
    # 1 прочитаем файлы
    names = list(current_path + "/files/" + i for i in os.listdir(current_path + "/files"))
    name_files = [i for i in names if i.endswith(".xex")]
    
    array_files = list()
    for name in name_files:
        array_files.append(_read_file(name))
    print("Прочитано {} файлов".format(len(name_files)))
    #print(array_files[0:10])

    #порядок
    order = _read_file(current_path + "/" + order_file)
    array_order = order.decode("utf-8").split("\n")
    #print("прочитан порядок")
    #print(array_order[0:10])

    #2 посчитаем их хеши
    hash_f = list(map(_get_hash_md5,array_files))
    #print("hash_f:")
    #print(hash_f[0:10])

    #3 упорядочим
    big_file = b''
    for i in array_order:
        k = 0
        for j in hash_f:
            if i == j:
                big_file = big_file + array_files[k]
            k = k + 1    
    #print("big_file")
    #print(big_file)

    dict_mime = {
        'text/plain':'txt', 
        'image/jpeg':'jpg'}
    mime = magic.from_file(current_path + "/" + result_file, mime = True)
    suf = dict_mime[mime]
    _save_file(current_path + "/" + result_file + "." + suf, big_file, "wb")
    return len(big_file)


if __name__ == "__main__":
    command = parse_command()
    config = read_config(os.getcwd())
    if command == "split":
        count_files = split_file(config.current_path, config.working_file, config.N, "order.md5")
        print("Файл {} разбин на {} частей".format(config.working_file, count_files))
    elif command == "join":
        size_file = join_file(config.current_path, "order.md5", "result")
        print("Создан файл размером {}".format(size_file))
    write_config(config)
