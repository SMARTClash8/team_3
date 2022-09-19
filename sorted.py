import os      # work with file system
import sys     # for command line
import re      # string func
import shutil  # copy file
import time
import asyncio
from aiopath import AsyncWindowsPath, AsyncPath

path_test = "C:\\Users\\Ultra\\Desktop\\garbage"
TRANS = {}


def make_trans_dict():
    CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j",
                   "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
                   "f", "h", "ts", "ch", "sh", "sch", "",
                   "y", "", "e", "yu", "u", "ja", "je", "ji", "g")
    CYR = []
    for item in CYRILLIC_SYMBOLS:
        CYR.append(item)
    for item, jtem in zip(CYR, TRANSLATION):
        TRANS[ord(item)] = jtem
        TRANS[ord(item.upper())] = jtem.upper()


def check_name(name_a):
    name_a_conv = name_a.translate(TRANS)
    return re.sub(r'[^a-zA-Z0-9.]', '_', name_a_conv)


def check_empty_dir(path_in):
    """Check, if folder is empty then  True
       if folder not empty ot not is then False
    """
    if os.path.exists(path_in):
        sz = os.path.getsize(path_in)
        if sz == 0:
            return True
        else:
            return False
    else:
        return False


async def del_empty_dir(path_in):
    """Delete empty dir
       Check before that size of folder is 0
    """
    ls_pathes = os.listdir(path_in)
    # check for chaild empty folder
    if bool(ls_pathes) is True:
        path_in_n = os.path.join(path_in, ls_pathes[0])
        await del_empty_dir(path_in_n)
        ls_pathes.pop(0)
        if bool(ls_pathes) is True:
            await del_empty_dir(path_in)
        else:
            apath_in = AsyncPath(path_in)
            await apath_in.rmdir()
            return
    else:
        # delete folder - root
        apath_in = AsyncPath(path_in)
        await apath_in.rmdir()


async def main():
    """Enrtypoint - check path from commandline
        or prompt via input
    """
    log_list = []
    ls_files = []

    if len(sys.argv) >= 2:
        path = sys.argv[1]
        apath = AsyncPath(path)
        if await apath.exists():
            print(path)
            print("Папка существует, продолжаем")
        else:
            # dont exist path, prompt via input
            print("Ошибка в комстроке пути к папке либо папки не существует")
            path = input("Введите путь к папке:\nИспользуйте двойной Бэкслеш \\\\ \
как разделитель\n")
            print(path)
            log_list.append(f"Папка для расхламления {path}\n")
    else:
        # path is empty, prompt via input
        print("Путь в комстроке пуст")
        path = input("Введите путь к папке:\nИспользуйте двойной Бэкслеш \\\\ \
как разделитель\n")
        print(path)
        log_list.append(f"Папка для расхламления {path}\n")

    # make dict for transliteration
    make_trans_dict()

    # Making target folders - async mode
    apath = AsyncPath(path)
    if not await apath.exists():
        print("Ошибка в пути к папке")
        os._exit(-1)
    else:
        apath_img = AsyncPath(path+'\\images')
        if not await apath_img.exists():
            task_img = asyncio.create_task(AsyncWindowsPath.mkdir(AsyncPath(path+'\\images')))
            await asyncio.gather(task_img)
        apath_doc = AsyncPath(path+'\\documents')
        if not await apath_doc.exists():
            task_doc = asyncio.create_task(AsyncWindowsPath.mkdir(AsyncPath(path+'\\documents')))
            await asyncio.gather(task_doc)
        apath_aud = AsyncPath(path+'\\audio')
        if not await apath_aud.exists():
            task_aud = asyncio.create_task(AsyncWindowsPath.mkdir(AsyncPath(path+'\\audio')))
            await asyncio.gather(task_aud)
        apath_vid = AsyncPath(path+'\\video')
        if not await apath_vid.exists():
            task_vid = asyncio.create_task(AsyncWindowsPath.mkdir(AsyncPath(path+'\\video')))
            await asyncio.gather(task_vid)
        apath_arc = AsyncPath(path+'\\archives')
        if not await apath_arc.exists():
            task_arc = asyncio.create_task(AsyncWindowsPath.mkdir(AsyncPath(path+'\\archives')))
            await asyncio.gather(task_arc)
        apath_oth = AsyncPath(path+'\\others')
        if not await apath_oth.exists():
            task_oth = asyncio.create_task(AsyncWindowsPath.mkdir(AsyncPath(path+'\\others')))
            await asyncio.gather(task_oth)

    # Get all pathes to all files in target path
    # in blocking mode, os.walk dont have analog in async
    print("Список существующих файлов в выбранной папке:")
    log_list.append("Список существующих файлов в выбранной папке:\n")
    for root, dirs, files in os.walk(path):
        for f in files:
            full_adr = os.path.join(root, f)
            print(full_adr)
            log_list.append(full_adr+'\n')
            ls_files.append(full_adr)
    print(' ')

    # Copy all files to target folders of extenstion - non_block mode
    # OS dont support any file operations in async mode
    for full_adr_s in ls_files:
        if (("images" in full_adr_s) or ("documents" in full_adr_s) or
                ("video" in full_adr_s) or ("audio" in full_adr_s) or
                ("archives" in full_adr_s) or ("other" in full_adr_s)):
            # dont touch files existing in target folders
            continue
        elif ((".xlsx" in full_adr_s) or (".txt" in full_adr_s) or
              (".doc" in full_adr_s) or (".docx" in full_adr_s) or
              (".pdf" in full_adr_s) or (".pptx" in full_adr_s)):
            normal_name = check_name(os.path.basename(full_adr_s))
            full_adr_d = os.path.join(path+'\\documents', normal_name)
            try:
                shutil.copyfile(full_adr_s, full_adr_d)
            except Exception:
                print("Ошибка в путях либо копировании файлов")
                log_list.append("Ошибка в путях либо копировании файлов\n")
                os._exit(-2)
            os.remove(full_adr_s)
            print(f"Перемещение \n{full_adr_s} в \n{full_adr_d}")
            log_list.append(f"Перемещение \n{full_adr_s} \
в \n{full_adr_d}\n")
        elif ((".jpeg" in full_adr_s) or (".bmp" in full_adr_s) or
              (".jpg" in full_adr_s) or (".png" in full_adr_s)):
            normal_name = check_name(os.path.basename(full_adr_s))
            full_adr_d = os.path.join(path+'\\images', normal_name)
            try:
                shutil.copyfile(full_adr_s, full_adr_d)
            except Exception:
                print("Ошибка в путях либо копировании файлов")
                log_list.append("Ошибка в путях либо копировании файлов\n")
                os._exit(-2)
            os.remove(full_adr_s)
            print(f"Перемещение \n{full_adr_s} в \n{full_adr_d}")
            log_list.append(f"Перемещение \n{full_adr_s} \
в \n{full_adr_d}\n")
        elif ((".avi" in full_adr_s) or (".mpeg" in full_adr_s) or
              (".mp4" in full_adr_s) or (".mov" in full_adr_s)):
            normal_name = check_name(os.path.basename(full_adr_s))
            full_adr_d = os.path.join(path+'\\video', normal_name)
            try:
                shutil.copyfile(full_adr_s, full_adr_d)
            except Exception:
                print("Ошибка в путях либо копировании файлов")
                log_list.append("Ошибка в путях либо копировании файлов\n")
                os._exit(-2)
            os.remove(full_adr_s)
            print(f"Перемещение \n{full_adr_s} в \n{full_adr_d}")
            log_list.append(f"Перемещение \n{full_adr_s} \
в \n{full_adr_d}\n")
        elif ((".mp3" in full_adr_s) or (".ogg" in full_adr_s) or
              (".wav" in full_adr_s) or (".amr" in full_adr_s)):
            normal_name = check_name(os.path.basename(full_adr_s))
            full_adr_d = os.path.join(path+'\\audio', normal_name)
            try:
                shutil.copyfile(full_adr_s, full_adr_d)
            except Exception:
                print("Ошибка в путях либо копировании файлов")
                log_list.append("Ошибка в путях либо копировании файлов\n")
                os._exit(-2)
            os.remove(full_adr_s)
            print(f"Перемещение \n{full_adr_s} в \n{full_adr_d}")
            log_list.append(f"Перемещение \n{full_adr_s} \
в \n{full_adr_d}\n")
        elif ((".zip" in full_adr_s) or (".rar" in full_adr_s) or
              (".tar" in full_adr_s) or (".gz" in full_adr_s)):
            normal_name = check_name(os.path.basename(full_adr_s))
            full_adr_d = os.path.join(path+'\\archives', normal_name)
            try:
                shutil.copyfile(full_adr_s, full_adr_d)
            except Exception:
                print("Ошибка в путях либо копировании файлов")
                log_list.append("Ошибка в путях либо копировании файлов\n")
                os._exit(-2)
            os.remove(full_adr_s)
            print(f"Перемещение \n{full_adr_s} в \n{full_adr_d}")
            log_list.append(f"Перемещение \n{full_adr_s} \
в \n{full_adr_d}\n")
        else:
            normal_name = check_name(os.path.basename(full_adr_s))
            full_adr_d = os.path.join(path+'\\others', normal_name)
            try:
                shutil.copyfile(full_adr_s, full_adr_d)
            except Exception:
                print("Ошибка в путях либо копировании файлов")
                log_list.append("Ошибка в путях либо копировании файлов\n")
                os._exit(-2)
            os.remove(full_adr_s)
            print(f"Перемещение \n{full_adr_s} в \n{full_adr_d}")
            log_list.append(f"Перемещение \n{full_adr_s} \
в \n{full_adr_d}\n")

    # Delete empty folders and subfolders - async mode for delete
    print("Список удаляемых пустых папок:")
    log_list.append("Список удаляемых пустых папок:\n")
    ls_dirs_1 = os.listdir(path)
    for d in ls_dirs_1:
        full_adr = os.path.join(path, d)
        if check_empty_dir(full_adr):
            if (("images" in full_adr) or ("documents" in full_adr) or
                    ("video" in full_adr) or ("audio" in full_adr) or
                    ("archives" in full_adr) or ("other" in full_adr)):
                # dont touch empty folders in target folders
                continue
            else:
                print(f"Удаление пустой папки\n{full_adr}")
                log_list.append(f"Удаление пустой папки\n{full_adr}\n")
                # delelte empty folder and subfolders - recursion
                try:
                    await del_empty_dir(full_adr)
                except Exception:
                    print("Ошибка в удалении пустых папок")
    print(' ')

    # Create logfile
    local_time = time.asctime()
    print(f"Создан логфайл {local_time}.txt")
    with open(path+"\\log.txt", 'x') as file_log:
        file_log.write((f"Файл логирования сортировки папки {path}\
                       \nсоздан {local_time} \n"))
        s_log = ''
        for item in log_list:
            s_log += item
        file_log.write(s_log)


asyncio.run(main())