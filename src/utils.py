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
music_usbsetting_filename = "music_usbsetting.bin"
reward_filename = "reward.bin"
shougou_filename = "shougou.bin"
datatable_filenames = [music_ai_section_filename, music_attribute_filename, music_order_filename,
                       musicinfo_filename, wordlist_filename, music_usbsetting_filename,
                       reward_filename, shougou_filename]
input_datatable_filepaths = [os.path.join(input_datatable_path, filename) for filename in datatable_filenames]
output_datatable_filepaths = [os.path.join(output_datatable_path, filename) for filename in datatable_filenames]
datatable_exist = False
fumen_key = "4434423946383537303842433443383030333843444132343339373531353830"
datatable_key = "3530304242323633353537423431384139353134383346433246464231354534"
openssl_path = os.path.join(tools_path, "OpenSSL")
openssl_exe_path = os.path.join(openssl_path, "openssl.exe")


def read_json(json_path):
    with open(json_path) as f:
        data = json.load(f)
    return data


def get_datatable_exist() -> bool:
    return datatable_exist


def get_nu3bank_template():
    template_data = read_json(template_path)
    return template_data["nus3bank_template"]

def get_datatable_files() -> list:
    data_list = []
    for filepath in input_datatable_filepaths:
        try:
            with open(filepath, "rb") as f:
                data = f.read()
                decrypted_data = decrypt_datatable_data(data)
                json_data = json.loads(gzip.decompress(decrypted_data).decode("utf-8"))["items"]
            data_list.append(json_data)
        except Exception as e:
            print("Error found in %s" % filepath)
            print(e)
            exit()
    return data_list

def decrypt_datatable_data(data: bytes) -> bytes:
    # Write data to temp path
    temp_filepath = os.path.join(temp_path, "temp.bin")
    temp_decrypted_filepath = os.path.join(temp_path, "temp_decrypted.bin")
    with open(temp_filepath, "wb") as f:
        f.write(data)
    iv = data[:16]
    iv = hex2string(iv)
    # Decrypt with openssl AES-256
    args = [openssl_exe_path, "aes-256-cbc", "-d", "-in", temp_filepath, "-out", temp_decrypted_filepath, "-K",
            datatable_key, "-iv", iv]
    p = subprocess.Popen(args, shell=False, stdout=subprocess.DEVNULL)
    p.wait()
    # Remove first 16 bytes of the decrypted file
    with open(temp_decrypted_filepath, "rb") as f:
        decrypted_data = f.read()
    decrypted_data = decrypted_data[16:]
    return decrypted_data


def write_datatable_files(data_list: tuple) -> None:
    for filepath, data in zip(output_datatable_filepaths, data_list):
        with open(filepath, "wb") as f:
            json_data = json.dumps({"items": data}, sort_keys=False, indent="\t", ensure_ascii=False).encode("utf-8")
            encrypted_data = encrypt_datatable_data(gzip.compress(json_data))
            f.write(encrypted_data)


def encrypt_datatable_data(data: bytes) -> bytes:
    iv = "0" * 32
    # Write data to temp path
    temp_filepath = os.path.join(temp_path, "temp_datatable.bin")
    temp_encrypted_filepath = os.path.join(temp_path, "temp_encrypted_datatable.bin")
    with open(temp_filepath, "wb") as f:
        f.write(data)
    # Encrypt with openssl AES-256
    args = [openssl_exe_path, "aes-256-cbc", "-in", temp_filepath, "-out", temp_encrypted_filepath, "-K", datatable_key,
            "-iv", iv]
    p = subprocess.Popen(args, shell=False, stdout=subprocess.DEVNULL)
    p.wait()
    # Append IV to the first 16 bytes of the encrypted file
    with open(temp_encrypted_filepath, "rb") as f:
        encrypted_data = f.read()
    new_iv = str2hex_byte(iv)
    encrypted_data = new_iv + encrypted_data
    return encrypted_data


def encrypt_fumen_data(fumen_data: str) -> bytes:
    # write to temp path
    temp_filepath = os.path.join(temp_path, "temp_fumen.bin")
    temp_encrypted_filepath = os.path.join(temp_path, "temp_encrypted_fumen.bin")
    save_str2hex(temp_filepath, fumen_data)
    with open(temp_filepath, "rb") as f:
        fumen_data = f.read()
    fumen_data = gzip.compress(fumen_data)
    with open(temp_filepath, "wb") as f:
        f.write(fumen_data)
    iv = "0" * 32
    # Encrypt with openssl AES-256
    args = [openssl_exe_path, "aes-256-cbc", "-in", temp_filepath, "-out", temp_encrypted_filepath, "-K", fumen_key,
            "-iv", iv]
    p = subprocess.Popen(args, shell=False, stdout=subprocess.DEVNULL)
    p.wait()
    # Append IV to the first 16 bytes of the encrypted file
    with open(temp_encrypted_filepath, "rb") as f:
        encrypted_data = f.read()
    new_iv = str2hex_byte(iv)
    encrypted_data = new_iv + encrypted_data
    return encrypted_data

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
    global datatable_exist

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
    datatable_exist = True
    for filepath in input_datatable_filepaths:
        if not os.path.exists(filepath):
            datatable_exist = False
            print(filepath + " not found.\n"
                             "Running in fumen/sound conversion only mode")


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

def save_str2hex(filepath: str, hex_data: str) -> None:
    with open(filepath, "wb") as f:
        f.write(binascii.unhexlify(hex_data))

def save_hex(filepath, hex_data):
    with open(filepath, "wb") as f:
        f.write(binascii.unhexlify(hex_data))


def str2hex(input_str):
    output = ""
    for char in input_str:
        output += struct.pack('<s', bytes(char, "utf-8")).hex()
    return output

def str2hex_byte(input_str: str) -> bytes:
    output = binascii.unhexlify(input_str)
    return output


def hex2string(hex_data: bytes) -> str:
    output = binascii.hexlify(hex_data).decode("ascii")
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
    music_ai_section_key_sequence = {"id": 0, "uniqueId": 1, "easy": 2, "normal": 3, "hard": 4, "oni": 5, "ura": 6,
                                     "oniLevel11": 7, "uraLevel11": 8}
    music_attribute_key_sequence = {"id": 0, "uniqueId": 1, "new": 2, "doublePlay": 3, "isNotCopyright": 4, "tag1": 5,
                                    "tag2": 6, "tag3": 7, "tag4": 8, "tag5": 9, "tag6": 10, "tag7": 11, "tag8": 12,
                                    "tag9": 13, "tag10": 14, "ensoPartsID1": 15, "ensoPartsID2": 16, "donBg1p": 17,
                                    "donBg2p": 18, "dancerDai": 19, "dancer": 20, "danceNormalBg": 21,
                                    "danceFeverBg": 22, "rendaEffect": 23, "fever": 24, "donBg1p1": 25, "donBg2p1": 26,
                                    "dancerDai1": 27, "dancer1": 28, "danceNormalBg1": 29, "danceFeverBg1": 30,
                                    "rendaEffect1": 31, "fever1": 32}
    music_order_key_sequence = {"genreNo": 0, "id": 1, "uniqueId": 2, "closeDispType": 3}
    musicinfo_key_sequence = {"id": 0, "uniqueId": 1, "genreNo": 2, "songFileName": 3, "papamama": 4, "branchEasy": 5,
                              "branchNormal": 6, "branchHard": 7, "branchMania": 8, "branchUra": 9, "starEasy": 10,
                              "starNormal": 11, "starHard": 12, "starMania": 13, "starUra": 14, "shinutiEasy": 15,
                              "shinutiNormal": 16, "shinutiHard": 17, "shinutiMania": 18, "shinutiUra": 19,
                              "shinutiEasyDuet": 20, "shinutiNormalDuet": 21, "shinutiHardDuet": 22,
                              "shinutiManiaDuet": 23, "shinutiUraDuet": 24, "shinutiScoreEasy": 25,
                              "shinutiScoreNormal": 26, "shinutiScoreHard": 27, "shinutiScoreMania": 28,
                              "shinutiScoreUra": 29, "shinutiScoreEasyDuet": 30, "shinutiScoreNormalDuet": 31,
                              "shinutiScoreHardDuet": 32, "shinutiScoreManiaDuet": 33, "shinutiScoreUraDuet": 34,
                              "easyOnpuNum": 35, "normalOnpuNum": 36, "hardOnpuNum": 37, "maniaOnpuNum": 38,
                              "uraOnpuNum": 39, "rendaTimeEasy": 40, "rendaTimeNormal": 41, "rendaTimeHard": 42,
                              "rendaTimeMania": 43, "rendaTimeUra": 44, "fuusenTotalEasy": 45, "fuusenTotalNormal": 46,
                              "fuusenTotalHard": 47, "fuusenTotalMania": 48, "fuusenTotalUra": 49, "spikeOnEasy": 50,
                              "spikeOnNormal": 51, "spikeOnHard": 52, "spikeOnOni": 53, "spikeOnUra": 54}
    wordlist_key_sequence = {"key": 0, "japaneseText": 1, "japaneseFontType": 2, "englishUsText": 3,
                             "englishUsFontType": 4, "chineseTText": 5, "chineseTFontType": 6, "koreanText": 7,
                             "koreanFontType": 8, "chineseSText": 9, "chineseSFontType": 10}
    music_usbsetting_key_sequence = {"id": 0, "uniqueId": 1, "usbVer": 2}
    reward_key_sequence = {"releaseType": 0, "songuid1": 1, "songuid2": 2, "songuid3": 3, "songuid4": 4, "songuid5": 5,
                           "songtag": 6, "tokenId": 7, "qrId": 8, "value": 9, "ensoType": 9, "reward_message": 10,
                           "rewardType": 11, "rewardUniqueId": 12}
    shougou_key_sequence = {"uniqueId": 0, "rarity": 1, "isNotCopyright": 2}

    music_ai_section_list, music_attribute_list, music_order_list, musicinfo_list, wordlist_list, music_usbsetting_list, reward_list, shougou_list = data_list

    for i, music_ai_section in enumerate(music_ai_section_list):
        music_ai_section = collections.OrderedDict(
            sorted(music_ai_section.items(), key=lambda x: music_ai_section_key_sequence[x[0]]))
        music_ai_section_list[i] = music_ai_section
    for i, music_attribute in enumerate(music_attribute_list):
        music_attribute = collections.OrderedDict(
            sorted(music_attribute.items(), key=lambda x: music_attribute_key_sequence[x[0]]))
        music_attribute_list[i] = music_attribute
    for i, musicinfo in enumerate(musicinfo_list):
        musicinfo = collections.OrderedDict(sorted(musicinfo.items(), key=lambda x: musicinfo_key_sequence[x[0]]))
        musicinfo_list[i] = musicinfo
    for i, music_usbsetting in enumerate(music_usbsetting_list):
        music_usbsetting = collections.OrderedDict(
            sorted(music_usbsetting.items(), key=lambda x: music_usbsetting_key_sequence[x[0]]))
        music_usbsetting_list[i] = music_usbsetting
    for i, wordlist in enumerate(wordlist_list):
        wordlist = collections.OrderedDict(sorted(wordlist.items(), key=lambda x: wordlist_key_sequence[x[0]]))
        wordlist_list[i] = wordlist
    for i, music_order in enumerate(music_order_list):
        music_order = collections.OrderedDict(sorted(music_order.items(), key=lambda x: music_order_key_sequence[x[0]]))
        music_order_list[i] = music_order
    for i, reward in enumerate(reward_list):
        reward = collections.OrderedDict(sorted(reward.items(), key=lambda x: reward_key_sequence[x[0]]))
        reward_list[i] = reward
    for i, shougou in enumerate(shougou_list):
        shougou = collections.OrderedDict(sorted(shougou.items(), key=lambda x: shougou_key_sequence[x[0]]))
        shougou_list[i] = shougou
    return music_ai_section_list, music_attribute_list, music_order_list, musicinfo_list, wordlist_list, music_usbsetting_list, reward_list, shougou_list
