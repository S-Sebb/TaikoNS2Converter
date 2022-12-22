# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
root_path = dir_path.parent.absolute()
XOR_tool_path = os.path.join(root_path, "tools", "TNS2-XOR", "TNS2-XOR.exe")
inputs_path = os.path.join(root_path, "inputs")
JKSV_path = os.path.join(inputs_path, "JKSV")
decrypted_path = os.path.join(inputs_path, "decrypted")
extracted_path = os.path.join(inputs_path, "extracted")


def find_cur_dir():
    return os.getcwd()


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def enumerate_files(path):
    output_filepaths = []
    output_filenames = []
    for root, folder, filenames in os.walk(path):
        for filename in filenames:
            output_filepaths.append(os.path.join(root, filename))
            output_filenames.append(filename)
    return output_filepaths, output_filenames


def remove_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
