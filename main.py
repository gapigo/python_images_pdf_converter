from PIL import Image
import os
from winreg import *

def get_valid_directory_or_return(message, accept_empty = False):
    while True:
        reading_directory = str(input(message)).strip()
        if not reading_directory and accept_empty:
            return None
        if os.path.isdir(reading_directory):
            return reading_directory
        else:
            if os.path.exists(reading_directory):
                print("This is not a directory, but a file.", end=' ')
            else:
                print("Directory not found.", end=' ')
            if (input('Press enter to try again. Write something to quit. ')):
                return False


def get_download_directory():
    download_directory = get_valid_directory_or_return('Inform a download folder (leave empty to downloads).\n$ ', accept_empty=True)
    if download_directory is None:    
        with OpenKey(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
            download_directory = QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]
    return False if download_directory is False else download_directory


def check_directory():
    directory = get_valid_directory_or_return('Inform the desiring directory to get images in alphabetical order in a PDF.\n$ ')
    if not directory:
        return False
    os.chdir(directory)
    return os.getcwd()

def get_relative_name(root_directory: str, current_directory):
    path_components_rd = root_directory.split('/' if '/' in root_directory else '\\')
    path_components_cd = current_directory.split('/' if '/' in current_directory else '\\')
    root_folder = path_components_rd[-1]
    if root_folder not in current_directory:
        raise FileNotFoundError('Current Directory must to be a child of root directory')
    merge = False
    path = ''
    for component in path_components_cd:
        if not merge and component == root_folder:
            merge = True
        if merge:
            path += f'{component}-'
    if path == '':
        path = 'root_folder'
    else:
        path = path[:-1]
    
    return path
    
directories_number = 0
def get_images_from_each_directory_hash_table(root_directory, res_hash_table={}):
    global directories_number, verboseActivated
    if verboseActivated:
        directories_number += 1
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'{directories_number} directories read.')
    dirs = []
    images = []
    for item in os.listdir():
        if (os.path.isdir(os.path.join(os.getcwd(), item))):
            dirs.append(item)
        else:
            if item.endswith('png') or item.endswith('jpg') or item.endswith('jpeg'):
                images.append(item)
                
    for d in dirs:
        os.chdir(d)
        res_hash_table = get_images_from_each_directory_hash_table(root_directory, res_hash_table)

    if images:
        res_hash_table[os.getcwd()] = images
    os.chdir('..')
    return res_hash_table
    

def log_pdf_mounting(pdf_counter: int, pdf_number: int, image_counter: int, images_number: int, mounting_pdf: bool = False):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{directories_number} directories read.')
    print(f'PDF: {pdf_counter} of {pdf_number}| Fetching Image: {image_counter} of {images_number}', end=' ')
    if mounting_pdf:
        print('| Mounting PDF...')
    print('\n')

 
def mount_and_download_all_pdfs(hash_table: dict, root_directory: str, download_folder: str):
    global verboseActivated
    pdf_counter = 0
    pdf_number = len(hash_table)
    for d, images_paths in hash_table.items():
        pdf_counter += 1
        os.chdir(d)
        images = []
        image_counter = 0
        images_number = len(images_paths)
        for image_path in images_paths:
            image_counter += 1
            fetching_image = Image.open(image_path)
            if fetching_image.mode == 'RGBA':
                backgrounded_image = Image.new("RGB", fetching_image.size, (255, 255, 255))
                backgrounded_image.paste(fetching_image, mask=fetching_image.split()[3])
                images.append(backgrounded_image)
            else:
                images.append(fetching_image)
            if verboseActivated:
                log_pdf_mounting(pdf_counter, pdf_number, image_counter, images_number)
        first_image: Image= images.pop(0)
        if verboseActivated:
            log_pdf_mounting(pdf_counter, pdf_number, image_counter, images_number, mounting_pdf=True)
        first_image.save(os.path.join(download_folder, f'{get_relative_name(root_directory, d)}.pdf'), save_all=True, append_images=images)

verboseActivated = False
def main():
    global verboseActivated
    if not (root_folder := check_directory()):
        return
    if not (download_folder := get_download_directory()):
        return
    if (str(input('Verbose? [N/y] ')).lower().strip() == 'y'):
        verboseActivated = True
    images_from_dirs_hash_table = get_images_from_each_directory_hash_table(os.getcwd())
    mount_and_download_all_pdfs(images_from_dirs_hash_table, root_folder, download_folder)

if __name__ == "__main__":
    main()
