# -*- coding: utf-8 -*-
from tqdm import tqdm

from convert_fumen import convert_fumen
from convert_sound import convert_sound
from utils import *

if __name__ == '__main__':
    init()
    extracted_filepaths, extracted_filenames = enumerate_files(extracted_path)

    song_dict_list = []
    fumen_endings = ["_e.bytes", "_e_1.bytes", "_e_2.bytes", "_n.bytes", "_n_1.bytes", "_n_2.bytes",
                     "_h.bytes", "_h_1.bytes", "_h_2.bytes", "_m.bytes", "_m_1.bytes", "_m_2.bytes",
                     "_x.bytes", "_x_1.bytes", "_x_2.bytes"]

    for filename in extracted_filenames:
        if not filename.endswith("_e.bytes"):
            continue
        song_dict = {}
        song_id = filename.split("_e.bytes")[0]
        if len(song_id) > 6:
            print("Invalid song ID: " + song_id)
        song_fumens = []
        for ending in fumen_endings:
            if song_id + ending in extracted_filenames:
                idx = extracted_filenames.index(song_id + ending)
                song_fumens.append(extracted_filepaths[idx])
        if len(song_fumens) < 12:
            song_fumens = []
            continue
        song_acb = "SONG_" + song_id.upper() + "_acb.bytes"
        if song_acb in extracted_filenames:
            idx = extracted_filenames.index(song_acb)
            song_acb = extracted_filepaths[idx]
        else:
            continue
        song_preview = "PSONG_" + song_id.upper() + "_acb.bytes"
        if song_preview in extracted_filenames:
            idx = extracted_filenames.index(song_preview)
            song_preview = extracted_filepaths[idx]
        else:
            song_preview = ""
        song_dict["id"] = song_id
        song_dict["fumens"] = song_fumens
        song_dict["acb"] = song_acb
        song_dict["preview"] = song_preview
        song_dict_list.append(song_dict)

    song_dict_list = sorted(song_dict_list, key=lambda x: x["id"])

    t = tqdm(range(len(song_dict_list)), position=0)
    current_song = tqdm(total=0, desc="Current song", position=1, bar_format='{desc}')
    current_status = tqdm(total=0, desc="", position=2, bar_format='{desc}')
    for i in t:
        song_dict = song_dict_list[i]
        song_id = song_dict["id"]
        current_song.set_description_str("Current song: " + song_id)
        song_fumens = song_dict["fumens"]
        song_acb = song_dict["acb"]
        song_preview = song_dict["preview"]

        song_temp_path = os.path.join(temp_path, song_id)
        make_dir(song_temp_path)
        os.chdir(song_temp_path)

        current_status.set_description_str("Converting fumen files...")
        fumen_filepaths = []
        for song_fumen in song_fumens:
            fumen_filepaths.append(convert_fumen(song_fumen))

        current_status.set_description_str("Converting sound files...")
        nus3bank_filepath = convert_sound(song_acb, song_preview, song_id)
        nus3bank_filename = os.path.basename(nus3bank_filepath)
        dst_nu3bank_filepath = os.path.join(outputs_sound_path, nus3bank_filename)
        if os.path.exists(dst_nu3bank_filepath):
            os.remove(dst_nu3bank_filepath)
        copy_file(nus3bank_filepath, dst_nu3bank_filepath)

        outputs_fumen_song_path = os.path.join(outputs_fumen_path, song_id)
        make_dir(outputs_fumen_song_path)
        for fumen_filepath in fumen_filepaths:
            fumen_filename = os.path.basename(fumen_filepath)
            dst_fumen_filepath = os.path.join(outputs_fumen_song_path, fumen_filename)
            copy_file(fumen_filepath, dst_fumen_filepath)
        os.chdir(root_path)
        remove_dir(temp_path)
    current_status.set_description_str("Complete")
