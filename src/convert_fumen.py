# -*- coding: utf-8 -*-
import binascii
import os.path

from utils import *


def convert_fumen(fumen_filepath):
    fumen_filename = os.path.basename(fumen_filepath)
    decrypt_file(fumen_filepath)
    ext_name = os.path.splitext(fumen_filename)[1]
    decrypted_filepath = os.path.join(find_cur_dir(), fumen_filename.replace(ext_name, "_dec" + ext_name))
    fumen_filepath = decrypted_filepath.replace("_dec" + ext_name, ".bin")
    if os.path.exists(fumen_filepath):
        os.remove(fumen_filepath)
    os.rename(decrypted_filepath, fumen_filepath)
    fix_hex(fumen_filepath)
    return fumen_filepath


def fix_hex(filepath):
    hex_data = open_as_hex(filepath)
    hex_data += "000000000000803f"
    save_hex(filepath, hex_data)
