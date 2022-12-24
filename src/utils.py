# -*- coding: utf-8 -*-
import binascii
import json
import os
import shutil
import struct
import subprocess
import time
from pathlib import Path

src_path = Path(os.path.dirname(os.path.realpath(__file__)))
root_path = src_path.parent.absolute()
XOR_tool_path = os.path.join(root_path, "tools", "TNS2-XOR", "TNS2-XOR.exe")
inputs_path = os.path.join(root_path, "inputs")
musicinfo_path = os.path.join(inputs_path, "musicinfo")
inputs_tja_path = os.path.join(inputs_path, "tja")
outputs_path = os.path.join(root_path, "outputs")
tools_path = os.path.join(root_path, "tools")
outputs_fumen_path = os.path.join(outputs_path, "fumen")
outputs_sound_path = os.path.join(outputs_path, "sound")
outputs_datatable_path = os.path.join(outputs_path, "datatable")
template_path = os.path.join(src_path, "template.json")
temp_path = os.path.join(root_path, "temp")
JKSV_path = os.path.join(inputs_path, "JKSV")
decrypted_path = os.path.join(inputs_path, "decrypted")
extracted_path = os.path.join(inputs_path, "extracted")
acb2hcas_path = os.path.join(tools_path, "libcgss", "bin", "x64", "Release", "acb2hcas.exe")
vgmstream_path = os.path.join(tools_path, "vgmstream-win", "test.exe")
vgaudiocli_path = os.path.join(tools_path, "VGAudioCli", "VGAudioCli.exe")
ns2_key_a = "52539816150204134"
ns2_key_k = "00baa8af36327ee6"


def read_json(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return data


def get_nu3bank_template():
    template_data = read_json(template_path)
    return template_data["nus3bank_template"]


def get_music_order_template():
    template_data = read_json(template_path)
    return template_data["music_order_template"]


def get_musicinfo_template():
    template_data = read_json(template_path)
    return template_data["musicinfo_template"]


def get_music_attribute_template():
    template_data = read_json(template_path)
    return template_data["music_attribute_template"]


def get_wordlist_template():
    template_data = read_json(template_path)
    return template_data["wordlist_template"]


def get_music_ai_section_template() -> str:
    template_data = read_json(os.path.join(src_path, "template.json"))
    return template_data["music_ai_section_template"]


def get_musicinfo_data() -> list:
    musicinfo_data = read_json(musicinfo_path)["items"]
    return musicinfo_data


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
    time.sleep(0.1)
    p.terminate()
    p.wait()


def init():
    for path in [temp_path, outputs_datatable_path]:
        remove_dir(path)
    for path in [inputs_path, inputs_tja_path, outputs_path, JKSV_path, decrypted_path, extracted_path, tools_path,
                 temp_path, outputs_fumen_path, outputs_sound_path, outputs_datatable_path]:
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
    if not os.path.exists(vgmstream_path):
        print("vgmstream-win not found.\n"
              "Please download it from https://github.com/vgmstream/vgmstream/releases and make sure "
              "vgmstream-win is at " +
              vgmstream_path)
        input("\nPress Enter to exit...")
        exit()
    if not os.path.exists(vgaudiocli_path):
        print("VGAudioCli not found.\n"
              "Please download it from https://github.com/Thealexbarney/VGAudio/releases and make sure "
              "VGAudioCli is at " +
              vgaudiocli_path)
        input("\nPress Enter to exit...")
        exit()
    if not os.path.exists(template_path):
        print("template.json not found.\n"
              "Please re-download this repository and make sure template.json is at " + template_path)
        input("\nPress Enter to exit...")
        exit()
    if not os.path.exists(musicinfo_path):
        print("musicinfo file not found.\n"
              "Please extract it from your latest musicinfo.bin and make sure the file \"musicinfo\" is at" +
              musicinfo_path)
        input("Press Enter to exit...")
        exit()


def acb2hcas(acb_filepath):
    args = [acb2hcas_path, acb_filepath, "-a", ns2_key_a, "-k", ns2_key_k]
    p = subprocess.Popen(args, shell=False, stdout=subprocess.DEVNULL)
    p.wait()


def hcas2wav(hcas_filepath, wav_filepath):
    args = [vgmstream_path, "-o", wav_filepath, hcas_filepath]
    p = subprocess.Popen(args, shell=False, stdout=subprocess.DEVNULL)
    p.wait()


def wav2idsp(wav_filepath, idsp_filepath):
    args = [vgaudiocli_path, "-i", wav_filepath, "-o", idsp_filepath]
    p = subprocess.Popen(args, shell=False, stdout=subprocess.DEVNULL)
    p.wait()


def copy_file(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    if not os.path.exists(src):
        return
    if not os.path.exists(os.path.dirname(dst)):
        os.makedirs(os.path.dirname(dst))
    shutil.copy(src, dst)


def open_as_hex(filepath):
    with open(filepath, "rb") as f:
        hex_data = binascii.hexlify(f.read()).decode("ascii")
    return hex_data


def save_hex(filepath, hex_data):
    with open(filepath, "wb") as f:
        f.write(binascii.unhexlify(hex_data))


def str2hex(input_str):
    output = ""
    for char in input_str:
        output += struct.pack('<s', bytes(char, "utf-8")).hex()
    return output


def int2hex(input_int, hex_len):
    hex_data = struct.pack('<Q', input_int).hex()[:hex_len]
    return hex_data
