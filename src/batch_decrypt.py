# -*- coding: utf-8 -*-
import os
import time
from pathlib import Path
import subprocess

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
root_path = dir_path.parent.absolute()
XOR_tool_path = os.path.join(root_path, "tools", "TNS2-XOR", "TNS2-XOR.exe")

if __name__ == '__main__':
    inputs_path = os.path.join(root_path, "inputs")
    if not os.path.exists(inputs_path):
        os.makedirs(inputs_path)

    JKSV_path = os.path.join(inputs_path, "JKSV")
    if not os.path.exists(JKSV_path):
        os.makedirs(JKSV_path)

    decrypted_path = os.path.join(inputs_path, "decrypted")
    if not os.path.exists(decrypted_path):
        os.makedirs(decrypted_path)

    encrypted_filepaths = []
    for root, folder, filenames in os.walk(JKSV_path):
        if filenames:
            for filename in filenames:
                encrypted_filepaths.append(os.path.join(root, filename))

    if not encrypted_filepaths:
        print("No encrypted files found in inputs/JKSV")
        input("Press Enter to exit...")
        exit()

    os.chdir(decrypted_path)

    for encrypted_filepath in encrypted_filepaths:
        print("Decrypting", encrypted_filepath)
        p = subprocess.Popen([XOR_tool_path, encrypted_filepath])
        time.sleep(0.1)
        p.terminate()
        p.wait()


