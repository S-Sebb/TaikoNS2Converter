# -*- coding: utf-8 -*-

from tqdm import tqdm

from utils import *

if __name__ == '__main__':
    init()

    encrypted_filepaths = enumerate_files(JKSV_path)[0]

    if not encrypted_filepaths:
        print("No encrypted files found in inputs/JKSV")
        input("Press Enter to exit...")
        exit()

    os.chdir(decrypted_path)

    for i in tqdm(range(len(encrypted_filepaths)), leave=False):
        encrypted_filepath = encrypted_filepaths[i]
        decrypt_file(encrypted_filepath)

    print("Done! Output files are in inputs/decrypted.\n"
          "Please use AssetStudio to extract the decrypted files to inputs/extracted.\n")
