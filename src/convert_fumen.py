# -*- coding: utf-8 -*-
import binascii

from utils import *


def convert_fumen(fumen_filepath):
    fumen_filename = os.path.basename(fumen_filepath)
    decrypt_file(fumen_filepath)
    decrypted_filepath = os.path.join(find_cur_dir(), fumen_filename.replace(".bytes", "_dec.bytes"))
    rename = decrypted_filepath.replace("_dec.bytes", ".bin")
    if os.path.exists(rename):
        os.remove(rename)
    os.rename(decrypted_filepath, rename)
    fix_hex(rename)
    return rename


def fix_hex(filepath):
    with open(filepath, 'rb') as f:
        hex_data = binascii.hexlify(f.read()).decode("ascii")
    hex_data += "000000000000803f"
    with open(filepath, 'wb') as f:
        f.write(binascii.unhexlify(hex_data))
