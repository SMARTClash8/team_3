import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor


FOLDERS = ["images", "documents", "audio", "video", "archives", "others"]

folder_ext_dict = {"images": ["JPEG", "PNG", "JPG", "SVG"],
                   "documents": ["DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX"],
                   "audio": ["MP3", "OGG", "WAV", "AMR"],
                   "video": ["AVI", "MP4", "MOV", "MKV"],
                   "archives": ["ZIP", "GZ", "TAR"],
                   "others": ["IPYNB"]}


def create_sorted_folders(cwd_path):

    for folder in FOLDERS:
        os.makedirs(f"{cwd_path}/{folder}", exist_ok=True)


def normalize(name):

    cyrillic = ['а', 'б', 'в', 'г', 'ґ', 'д', 'е', 'є', 'ж', 'з', 'и', 'і', 'ї', 'й', 'к',
                'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ь', 'ю', 'я']
    latin = ['a', 'b', 'v', 'h', 'g', 'd', 'e', 'ye', 'zh', 'z', 'y', 'i', 'yi', 'y', 'k', 'l', 'm',
             'n', 'o', 'p', 'r', 's', 't', 'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', '', 'yu', 'ya']

    name = "".join([x if x.isalnum() else "_" for x in name])

    mytable = {ord(cyr): lat for cyr, lat in zip(cyrillic, latin)}
    mytable.update({ord(cyr.upper()): lat.upper()
                   for cyr, lat in zip(cyrillic, latin)})

    result = name.translate(mytable)

    return result


def sort_docs(path, base_path=None):

    if not base_path:
        base_path = path
    directories = os.listdir(path)
    item_path = path


    files_list = []
    directories_list = []

    def map_directories(item):

        nonlocal files_list
        nonlocal directories_list

        if os.path.isfile(f"{path}/{item}"):
            files_list.append(item)
        elif os.path.isdir(f"{path}/{item}") and (item not in FOLDERS):
            directories_list.append(item)


    with ThreadPoolExecutor() as executor:
        search = list(map(map_directories, list(directories)))

    
    def move_files(item):

        item_path = f"{path}/{item}"
        folder_to_move = "others"


        file_name = item[:item.rfind(".")]
        file_type = item.split(".")[-1]

        item = ".".join([normalize(file_name), file_type])

        for k, v in folder_ext_dict.items():

            if file_type.upper() in folder_ext_dict.get(k):
                folder_to_move = k
                break

        move_file_to_path = f"{base_path}/{folder_to_move}/{item}"

        if folder_to_move == "archives":

            shutil.unpack_archive(item_path, move_file_to_path, file_type)
            os.remove(item_path)

        else:
            shutil.move(item_path, move_file_to_path)

        item_path = os.path.dirname(item_path)
        return item_path


    if files_list:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(move_files, files_list))

        item_path = results[0]


    def directories_handler(item):
        item_path = f"{path}/{item}"

        if os.listdir(item_path):
            sort_docs(item_path, base_path)
        else:
            shutil.rmtree(item_path)
            item_path = os.path.dirname(item_path)
            return item_path
    
    if directories_list:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(directories_handler, directories_list))
        item_path = results[0]


    while (not os.listdir(item_path)) and os.path.dirname(item_path) not in FOLDERS:

        shutil.rmtree(item_path)
        item_path = os.path.dirname(item_path)


def sort_folder(folder_path):

    try:
        create_sorted_folders(folder_path)
    except ValueError:
        "Please enter a correct path"

    sort_docs(folder_path)


if __name__=="__main__":

    if len(sys.argv) > 1:

        create_sorted_folders(sys.argv[1])
        sort_folder(sys.argv[1])
    
    else:

        folder_path=input("Please enter the path: ")
        sort_folder(folder_path)