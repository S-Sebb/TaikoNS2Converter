# -*- coding: utf-8 -*-
import binascii
import collections
import gzip
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
conversion_data_path = os.path.join(inputs_path, "conversion_data.xlsx")
outputs_path = os.path.join(root_path, "outputs")
tools_path = os.path.join(root_path, "tools")
outputs_fumen_path = os.path.join(outputs_path, "fumen")
outputs_sound_path = os.path.join(outputs_path, "sound")
input_datatable_path = os.path.join(inputs_path, "datatable")
output_datatable_path = os.path.join(outputs_path, "datatable")
template_path = os.path.join(src_path, "template.json")
temp_path = os.path.join(root_path, "temp")
base_game_path = os.path.join(inputs_path, "base_game")
encrypted_path = os.path.join(inputs_path, "encrypted")
decrypted_path = os.path.join(inputs_path, "decrypted")
extracted_path = os.path.join(inputs_path, "extracted")
acb2hcas_path = os.path.join(tools_path, "libcgss", "bin", "x64", "Release", "acb2hcas.exe")
vgmstream_path = os.path.join(tools_path, "vgmstream-win", "test.exe")
vgaudiocli_path = os.path.join(tools_path, "VGAudioCli", "VGAudioCli.exe")
ns2_key_a = "52539816150204134"
ns2_key_k = "00baa8af36327ee6"
music_ai_section_filename = "music_ai_section.bin"
music_attribute_filename = "music_attribute.bin"
music_order_filename = "music_order.bin"
musicinfo_filename = "musicinfo.bin"
wordlist_filename = "wordlist.bin"
datatable_filenames = [music_ai_section_filename, music_attribute_filename, music_order_filename, musicinfo_filename,
                       wordlist_filename]
input_datatable_filepaths = [os.path.join(input_datatable_path, filename) for filename in datatable_filenames]
output_datatable_filepaths = [os.path.join(output_datatable_path, filename) for filename in datatable_filenames]


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


def get_datatable_files() -> list:
    data_list = []
    for filepath in input_datatable_filepaths:
        try:
            with open(filepath, "rb") as f:
                json_data = json.loads(gzip.decompress(f.read()).decode("utf-8"))["items"]
            data_list.append(json_data)
        except Exception as e:
            print("Error found in %s" % filepath)
            print(e)
            exit()
    return data_list


def write_datatable_files(data_list: tuple) -> None:
    for filepath, data in zip(output_datatable_filepaths, data_list):
        with open(filepath, "wb") as f:
            f.write(gzip.compress(
                json.dumps({"items": data}, sort_keys=False, indent="\t", ensure_ascii=False).encode("utf-8")))


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
    for path in [temp_path, output_datatable_path]:
        remove_dir(path)
    for path in [inputs_path, outputs_path, encrypted_path, decrypted_path, extracted_path, tools_path,
                 temp_path, outputs_fumen_path, outputs_sound_path, output_datatable_path]:
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
    if not os.path.exists(conversion_data_path):
        print("conversion_data file not found.\n"
              "Please re-download it from this repo and fill in the data for the songs you wish to convert,\n"
              "and make sure the file \"conversion_data.xlsx\" is at" +
              conversion_data_path)
        input("Press Enter to exit...")
        exit()
    for filepath in input_datatable_filepaths:
        if not os.path.exists(filepath):
            print("%s" % filepath + " not found.\n")
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


def hex2int(input_hex: str) -> int:
    hex_data = bytearray.fromhex(input_hex)
    if len(hex_data) == 4:
        output = struct.unpack('<L', hex_data)[0]
    elif len(hex_data) == 2:
        output = struct.unpack('<H', hex_data)[0]
    else:
        output = 0
    return output


def hex2float(input_hex: str) -> float:
    hex_data = bytearray.fromhex(input_hex)
    output = struct.unpack('<f', hex_data)[0]
    return output


def sort_datatable_key_sequence(data_list: tuple) -> tuple:
    music_ai_section_key_sequence = {"id": 0,
                                     "uniqueId": 1,
                                     "easy": 2,
                                     "normal": 3,
                                     "hard": 4,
                                     "oni": 5,
                                     "ura": 6}
    music_attribute_key_sequence = {"id": 0,
                                    "uniqueId": 1,
                                    "new": 2,
                                    "canPlayUra": 3,
                                    "doublePlay": 4,
                                    "tag1": 5,
                                    "tag2": 6,
                                    "tag3": 7,
                                    "tag4": 8,
                                    "tag5": 9,
                                    "tag6": 10,
                                    "tag7": 11,
                                    "tag8": 12,
                                    "tag9": 13,
                                    "tag10": 14,
                                    "donBg1p": 15,
                                    "donBg2p": 16,
                                    "dancerDai": 17,
                                    "dancer": 18,
                                    "danceNormalBg": 19,
                                    "danceFeverBg": 20,
                                    "rendaEffect": 21,
                                    "fever": 22,
                                    "donBg1p1": 23,
                                    "donBg2p1": 24,
                                    "dancerDai1": 25,
                                    "dancer1": 26,
                                    "danceNormalBg1": 27,
                                    "danceFeverBg1": 28,
                                    "rendaEffect1": 29,
                                    "fever1": 30}
    music_order_key_sequence = {"genreNo": 0,
                                "id": 1,
                                "uniqueId": 2,
                                "closeDispType": 3}
    musicinfo_key_sequence = {"id": 0,
                              "uniqueId": 1,
                              "genreNo": 2,
                              "songFileName": 3,
                              "papamama": 4,
                              "branchEasy": 5,
                              "branchNormal": 6,
                              "branchHard": 7,
                              "branchMania": 8,
                              "branchUra": 9,
                              "starEasy": 10,
                              "starNormal": 11,
                              "starHard": 12,
                              "starMania": 13,
                              "starUra": 14,
                              "shinutiEasy": 15,
                              "shinutiNormal": 16,
                              "shinutiHard": 17,
                              "shinutiMania": 18,
                              "shinutiUra": 19,
                              "shinutiEasyDuet": 20,
                              "shinutiNormalDuet": 21,
                              "shinutiHardDuet": 22,
                              "shinutiManiaDuet": 23,
                              "shinutiUraDuet": 24,
                              "shinutiScoreEasy": 25,
                              "shinutiScoreNormal": 26,
                              "shinutiScoreHard": 27,
                              "shinutiScoreMania": 28,
                              "shinutiScoreUra": 29,
                              "shinutiScoreEasyDuet": 30,
                              "shinutiScoreNormalDuet": 31,
                              "shinutiScoreHardDuet": 32,
                              "shinutiScoreManiaDuet": 33,
                              "shinutiScoreUraDuet": 34,
                              "easyOnpuNum": 35,
                              "normalOnpuNum": 36,
                              "hardOnpuNum": 37,
                              "maniaOnpuNum": 38,
                              "uraOnpuNum": 39,
                              "fuusenTotalEasy": 40,
                              "fuusenTotalNormal": 41,
                              "fuusenTotalHard": 42,
                              "fuusenTotalMania": 43,
                              "fuusenTotalUra": 44,
                              "rendaTimeEasy": 45,
                              "rendaTimeNormal": 46,
                              "rendaTimeHard": 47,
                              "rendaTimeMania": 48,
                              "rendaTimeUra": 49}
    wordlist_key_sequence = {"key": 0,
                             "japaneseText": 1,
                             "japaneseFontType": 2,
                             "englishUsText": 3,
                             "englishUsFontType": 4,
                             "chineseTText": 5,
                             "chineseTFontType": 6,
                             "koreanText": 7,
                             "koreanFontType": 8,
                             "frenchText": 9,
                             "frenchFontType": 10}

    music_ai_section_list, music_attribute_list, music_order_list, musicinfo_list, wordlist_list = data_list

    for i, music_ai_section in enumerate(music_ai_section_list):
        music_ai_section = collections.OrderedDict(sorted(music_ai_section.items(),
                                                          key=lambda x: music_ai_section_key_sequence[x[0]]))
        music_ai_section_list[i] = music_ai_section
    for i, music_attribute in enumerate(music_attribute_list):
        # music_attribute["new"] = False
        music_attribute = collections.OrderedDict(sorted(music_attribute.items(),
                                                         key=lambda x: music_attribute_key_sequence[x[0]]))
        music_attribute_list[i] = music_attribute
    for i, music_order in enumerate(music_order_list):
        music_order = collections.OrderedDict(sorted(music_order.items(),
                                                     key=lambda x: music_order_key_sequence[x[0]]))
        music_order_list[i] = music_order
    for i, musicinfo in enumerate(musicinfo_list):
        if musicinfo["genreNo"] == 7:
            musicinfo["genreNo"] = 4
        elif musicinfo["genreNo"] == 8:
            musicinfo["genreNo"] = 5
        elif musicinfo["genreNo"] == 17:
            musicinfo["genreNo"] = 4
        elif musicinfo["genreNo"] == 18:
            musicinfo["genreNo"] = 0
        musicinfo = collections.OrderedDict(sorted(musicinfo.items(),
                                                   key=lambda x: musicinfo_key_sequence[x[0]]))
        musicinfo_list[i] = musicinfo
    for i, wordlist in enumerate(wordlist_list):
        wordlist = collections.OrderedDict(sorted(wordlist.items(),
                                                  key=lambda x: wordlist_key_sequence[x[0]]))
        wordlist_list[i] = wordlist
    return music_ai_section_list, music_attribute_list, music_order_list, musicinfo_list, wordlist_list
