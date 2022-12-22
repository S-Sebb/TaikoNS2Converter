# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import time
from pathlib import Path

dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
root_path = dir_path.parent.absolute()
XOR_tool_path = os.path.join(root_path, "tools", "TNS2-XOR", "TNS2-XOR.exe")
inputs_path = os.path.join(root_path, "inputs")
temp_path = os.path.join(root_path, "temp")
JKSV_path = os.path.join(inputs_path, "JKSV")
decrypted_path = os.path.join(inputs_path, "decrypted")
extracted_path = os.path.join(inputs_path, "extracted")
acb2hcas_path = os.path.join(root_path, "tools", "libcgss", "bin", "x64", "Release", "acb2hcas.exe")
ns2_key_a = "52539816150204134"
ns2_key_k = "00baa8af36327ee6"
vgmstream_path = os.path.join(root_path, "tools", "vgmstream-win", "test.exe")


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


def decrypt_file(filepath):
    p = subprocess.Popen([XOR_tool_path, filepath], shell=False, stdout=subprocess.DEVNULL)
    time.sleep(0.05)
    p.terminate()
    p.wait()


def init_check():
    for path in [inputs_path, JKSV_path, decrypted_path, extracted_path, temp_path]:
        make_dir(path)
    if not os.path.exists(XOR_tool_path):
        print("TNS2-XOR.exe not found.\n"
              "Please download it from discord and make sure TNS2-XOR.exe is at " + XOR_tool_path)
        input("\nPress Enter to exit...")
        exit()
    if not os.path.exists(acb2hcas_path):
        print("acb2hcas.exe not found.\n"
              "Please download it from https://github.com/hozuki/libcgss/releases and make sure acb2hcas.exe is at " +
              acb2hcas_path)
        input("\nPress Enter to exit...")
        exit()


def acb2hcas(acb_filepath):
    args = [acb2hcas_path, acb_filepath, "-a", ns2_key_a, "-k", ns2_key_k]
    p = subprocess.Popen(args, shell=False, stdout=subprocess.DEVNULL)
    time.sleep(0.1)
    p.terminate()
    p.wait()


def hcas2wav(hcas_filepath, wav_filepath):
    args = [vgmstream_path, "-o", wav_filepath, hcas_filepath]
    subprocess.Popen(args, shell=False, stdout=subprocess.DEVNULL)


def copy_file(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    time.sleep(0.05)
    if not os.path.exists(src):
        return
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    shutil.copy(src, dst)
