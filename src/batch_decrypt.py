# -*- coding: utf-8 -*-
import subprocess
import time

from tqdm import tqdm

from utils import *

if __name__ == '__main__':
    for path in [inputs_path, JKSV_path, decrypted_path, extracted_path]:
        make_dir(path)

    encrypted_filepaths = enumerate_files(JKSV_path)[0]

    if not encrypted_filepaths:
        print("No encrypted files found in inputs/JKSV")
        input("Press Enter to exit...")
        exit()

    os.chdir(decrypted_path)

    for i in tqdm(range(len(encrypted_filepaths))):
        encrypted_filepath = encrypted_filepaths[i]
        p = subprocess.Popen([XOR_tool_path, encrypted_filepath], shell=False, stdout=subprocess.DEVNULL)
        time.sleep(0.05)
        p.terminate()
        p.wait()

    print("Done! Output files are in inputs/decrypted.\n"
          "Please use AssetStudio to extract the decrypted files to inputs/extracted.\n"
          "Press Enter to exit...")
    input()
