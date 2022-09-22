import os
import shutil
import sys
import aioshutil
from aiopath import AsyncPath
from asyncio import run, gather
from queue import Queue



FOLDERS = ["images", "documents", "audio", "video", "archives", "others"]

folder_extension_dict = {"images": ["JPEG", "PNG", "JPG", "SVG"],
                   "documents": ["DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX"],
                   "audio": ["MP3", "OGG", "WAV", "AMR"],
                   "video": ["AVI", "MP4", "MOV", "MKV"],
                   "archives": ["ZIP", "GZ", "TAR"],
                   "others": ["IPYNB", "PY"]}


def create_sorted_folders(cwd_path):

    for folder in FOLDERS:
        gen_path = os.path.join(cwd_path,folder)
        os.makedirs(gen_path, exist_ok=True)


def normalize(name):

    cyrillic = ['а', 'б', 'в', 'г', 'ґ', 'д', 'е', 'є', 'ж', 'з', 'и', 'і', 'ї', 'й', 'к',
                'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я']
    latin = ['a', 'b', 'v', 'h', 'g', 'd', 'e', 'ye', 'zh', 'z', 'y', 'i', 'yi', 'y', 'k', 'l', 'm',
             'n', 'o', 'p', 'r', 's', 't', 'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', '', 'yu', 'ya']

    name = name.strip()
    name = "".join([x if x.isalnum() else "_" for x in name])

    mytable = {ord(cyr): lat for cyr, lat in zip(cyrillic, latin)}
    mytable.update({ord(cyr.upper()): lat.upper()
                   for cyr, lat in zip(cyrillic, latin)})

    result = name.translate(mytable)

    return result

files_path_list = []
directories_list = Queue()


async def files_handler(base_path, path):

        
        item_path = path
        item = str(path)
        folder_to_move = "others"


        file_name = item[item.rfind("\\"):item.rfind(".")]
        file_type = item.split(".")[-1]

        new_name = ".".join([normalize(file_name), file_type])

        for key in folder_extension_dict.keys():

            if file_type.upper() in folder_extension_dict.get(key):
                folder_to_move = key
                break

        #move_file_to_path = f"{base_path}/{folder_to_move}/{new_name}"
        move_file_to_path = os.path.join(base_path,folder_to_move, new_name)

        if folder_to_move == "archives":
            while True:
                try:
                    await aioshutil.unpack_archive(str(item_path), move_file_to_path, file_type)
                    break
                except PermissionError:
                    move_file_to_path = f"{move_file_to_path}-copy"
            os.remove(item_path)

        else:
            while True:
                try:
                    await aioshutil.move(item_path, move_file_to_path)
                    break
                except PermissionError:
                    move_file_to_path = f"{move_file_to_path}-copy"
        return


async def main_move(base_path):
        items = files_path_list
        features = (files_handler(base_path, file) for file in items)
        await gather(*features)


async def map_directories(path):


    item_path = AsyncPath(path)
    full_path = item_path
    file_check = await item_path.is_file()


    if file_check:
        files_path_list.append(full_path)
    elif os.path.dirname(path) not in FOLDERS:
        directories_list.put(full_path)

    
async def main_maping(path1):
    
    directories = [name_dir.path for name_dir in os.scandir(path1)]
    if directories:
        features = (map_directories(file) for file in list(directories))
        await gather(*features)


def sort_folder(folder_path):
    try:
        create_sorted_folders(folder_path)
        directories_list.put(folder_path)

        while not directories_list.empty():
            path = directories_list.get()
            run(main_maping(path))

        run(main_move(folder_path))

        for folder in os.listdir(folder_path):
            if folder not in FOLDERS:
                shutil.rmtree(os.path.join(folder_path,folder))
        global files_path_list
        files_path_list = []

    except ValueError:
        raise FileNotFoundError("Please enter a correct path")


if __name__=="__main__":


    if len(sys.argv) > 1:
        sort_folder(sys.argv[1])
    else:
        folder_path=input("Please enter the path: ")
        sort_folder(folder_path)
