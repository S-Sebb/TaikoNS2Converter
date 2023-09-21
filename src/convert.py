# -*- coding: utf-8 -*-
import pandas as pd
from tqdm import tqdm

from convert_fumen import convert_fumen
from convert_sound import convert_sound
from generate_datatable import generate_datatable
from parse_fumen import parse_fumen
from utils import *

if __name__ == '__main__':
    init()

    if get_datatable_exist():
        (music_ai_section_list, music_attribute_list, music_order_list, musicinfo_list, wordlist_list,
         music_usbsetting_list, reward_list, shougou_list) = get_datatable_files()
        available_unique_ids = [_ for _ in range(1599)]
        for musicinfo in musicinfo_list:
            if musicinfo["uniqueId"] in available_unique_ids:
                available_unique_ids.remove(musicinfo["uniqueId"])
        available_unique_ids = sorted(available_unique_ids)
        available_shougou_unique_ids = [_ for _ in range(1599)]
        for shougou in shougou_list:
            if shougou["uniqueId"] in available_shougou_unique_ids:
                available_shougou_unique_ids.remove(shougou["uniqueId"])

    song_dict_list = []
    fumen_bytes_endings = ["_e.bytes", "_e_1.bytes", "_e_2.bytes", "_n.bytes", "_n_1.bytes", "_n_2.bytes",
                           "_h.bytes", "_h_1.bytes", "_h_2.bytes", "_m.bytes", "_m_1.bytes", "_m_2.bytes",
                           "_x.bytes", "_x_1.bytes", "_x_2.bytes"]
    fumen_endings = ["_e.bin", "_e_1.bin", "_e_2.bin", "_n.bin", "_n_1.bin", "_n_2.bin", "_h.bin",
                     "_h_1.bin", "_h_2.bin", "_m.bin", "_m_1.bin", "_m_2.bin", "_x.bin", "_x_1.bin",
                     "_x_2.bin"]

    possible_music_pass_preview_songs = []

    base_game_filepaths, base_game_filenames = enumerate_files(base_game_path)
    for filename in base_game_filenames:
        if filename.startswith("PSONG_"):
            possible_music_pass_preview_songs.append(filename)

    for filename in base_game_filenames:
        if filename.endswith("_e.bin") and not filename.startswith("ses0"):
            song_dict = {}
            song_id = filename.split("_e.bin")[0]
            song_fumens = []
            for ending in fumen_endings:
                if song_id + ending in base_game_filenames:
                    idx = base_game_filenames.index(song_id + ending)
                    song_fumens.append(base_game_filepaths[idx])
            song_acb = "SONG_" + song_id.upper() + ".acb"
            if song_acb in base_game_filenames:
                song_dict["acb"] = song_acb
                idx = base_game_filenames.index(song_acb)
                song_acb = base_game_filepaths[idx]
            else:
                print("acb not found for " + song_id)
                continue
            song_preview = "PSONG_" + song_id.upper() + ".acb"
            if song_preview in base_game_filenames:
                possible_music_pass_preview_songs.remove(song_preview)
                idx = base_game_filenames.index(song_preview)
                song_preview = base_game_filepaths[idx]
            else:
                print("preview not found for " + song_id)
                continue
            song_dict["id"] = song_id
            song_dict["fumens"] = song_fumens
            song_dict["acb"] = song_acb
            song_dict["preview"] = song_preview
            song_dict_list.append(song_dict)

    extracted_filepaths, extracted_filenames = enumerate_files(extracted_path)

    for filename in extracted_filenames:
        if not filename.endswith("_e.bytes"):
            continue
        song_dict = {}
        song_id = filename.split("_e.bytes")[0]
        if len(song_id) > 6:
            print("Invalid song ID: " + song_id)
        song_fumens = []
        for ending in fumen_bytes_endings:
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
            print("acb not found for " + song_id)
            continue
        song_preview = "PSONG_" + song_id.upper() + "_acb.bytes"
        if song_preview in extracted_filenames:
            idx = extracted_filenames.index(song_preview)
            song_preview = extracted_filepaths[idx]
        else:
            song_preview = "PSONG_" + song_id.upper() + ".acb"
            if song_preview in possible_music_pass_preview_songs:
                idx = base_game_filenames.index(song_preview)
                song_preview = base_game_filepaths[idx]
            else:
                print("preview not found for " + song_id)
                continue

        song_dict["id"] = song_id
        song_dict["fumens"] = song_fumens
        song_dict["acb"] = song_acb
        song_dict["preview"] = song_preview
        song_dict_list.append(song_dict)

    song_dict_list = sorted(song_dict_list, key=lambda x: x["id"])

    conversion_data = pd.read_excel(conversion_data_path, sheet_name="Sheet1").astype(str)
    tja_data_list = []
    for ind in conversion_data.index:
        tja_data = {"song_id": conversion_data["SONG_ID"][ind], "genre": conversion_data["GENRE"][ind],
                    "TITLE": conversion_data["TITLE"][ind], "SUBTITLE": conversion_data["SUBTITLE"][ind]}
        edit_data, oni_data, hard_data, normal_data, easy_data = {}, {}, {}, {}, {}
        edit_data["LEVEL"] = conversion_data["EDIT_LEVEL"][ind]
        edit_data["COURSE"] = "Edit"
        edit_data["SCOREINIT"] = conversion_data["EDIT_SCOREINIT"][ind]
        edit_data["SCOREDIFF"] = conversion_data["EDIT_MAX_SCORE"][ind]
        oni_data["LEVEL"] = conversion_data["ONI_LEVEL"][ind]
        oni_data["COURSE"] = "Oni"
        oni_data["SCOREINIT"] = conversion_data["ONI_SCOREINIT"][ind]
        oni_data["SCOREDIFF"] = conversion_data["ONI_MAX_SCORE"][ind]
        hard_data["LEVEL"] = conversion_data["HARD_LEVEL"][ind]
        hard_data["COURSE"] = "Hard"
        hard_data["SCOREINIT"] = conversion_data["HARD_SCOREINIT"][ind]
        hard_data["SCOREDIFF"] = conversion_data["HARD_MAX_SCORE"][ind]
        normal_data["LEVEL"] = conversion_data["NORMAL_LEVEL"][ind]
        normal_data["COURSE"] = "Normal"
        normal_data["SCOREINIT"] = conversion_data["NORMAL_SCOREINIT"][ind]
        normal_data["SCOREDIFF"] = conversion_data["NORMAL_MAX_SCORE"][ind]
        easy_data["LEVEL"] = conversion_data["EASY_LEVEL"][ind]
        easy_data["COURSE"] = "Easy"
        easy_data["SCOREINIT"] = conversion_data["EASY_SCOREINIT"][ind]
        easy_data["SCOREDIFF"] = conversion_data["EASY_MAX_SCORE"][ind]
        course_data_list = [edit_data, oni_data, hard_data, normal_data, easy_data]
        for i, course_data in enumerate(course_data_list):
            if course_data["LEVEL"] == "nan":
                course_data["LEVEL"] = 0
            else:
                course_data["LEVEL"] = int(float(course_data["LEVEL"]))
        tja_data["syougou"] = "[]"
        tja_data["syougou_type"] = "[]"
        tja_data["syougou_rarity"] = "[]"
        tja_data["course_data"] = course_data_list
        tja_data_list.append(tja_data)

    found_tja_data_list = []
    for tja_data in tja_data_list:
        song_id = tja_data["song_id"]
        if song_id.strip() != "" and song_id != "nan":
            found = False
            for song_dict in song_dict_list:
                if song_dict["id"] == song_id:
                    found = True
                    found_tja_data_list.append(tja_data)
                    break
            if not found:
                print("Song in conversion_data.xlsx not found: " + song_id)
                continue
    tja_data_list = found_tja_data_list

    if get_datatable_exist():
        if len(available_unique_ids) < len(tja_data_list):
            print("Not enough unique ids. Please delete some songs from musicinfo.")
            exit()

    t = tqdm(range(len(tja_data_list)), position=0, leave=False)
    current_song = tqdm(total=0, desc="Current song", position=1, bar_format='{desc}', leave=False)
    current_status = tqdm(total=0, desc="", position=2, bar_format='{desc}', leave=False)
    append_data = []
    for i in t:
        tja_data = tja_data_list[i]
        song_id = tja_data["song_id"]
        song_dict = {}
        for data in song_dict_list:
            if data["id"] == song_id:
                song_dict = data
                break

        current_song.set_description_str("Current song: " + song_id)
        song_fumens = song_dict["fumens"]
        song_acb = song_dict["acb"]
        song_preview = song_dict["preview"]

        temp_song_path = os.path.join(temp_path, song_id)
        make_dir(temp_song_path)
        os.chdir(temp_song_path)

        current_status.set_description_str("Converting fumen files...")
        fumen_filepaths = []
        for song_fumen in song_fumens:
            fumen_filepaths.append(convert_fumen(song_fumen))

        current_status.set_description_str("Converting sound files...")
        nus3bank_filepath, duration = convert_sound(song_acb, song_preview, song_id)
        nus3bank_filename = os.path.basename(nus3bank_filepath)
        dst_nus3bank_filepath = os.path.join(outputs_sound_path, nus3bank_filename)
        if os.path.exists(dst_nus3bank_filepath):
            os.remove(dst_nus3bank_filepath)
        copy_file(nus3bank_filepath, dst_nus3bank_filepath)

        outputs_fumen_song_path = os.path.join(outputs_fumen_path, song_id)
        make_dir(outputs_fumen_song_path)
        has_ura = False
        for fumen_filepath in fumen_filepaths:
            fumen_filename = os.path.basename(fumen_filepath)
            dst_fumen_filepath = os.path.join(outputs_fumen_song_path, fumen_filename)
            copy_file(fumen_filepath, dst_fumen_filepath)
            tja_data = parse_fumen(fumen_filepath, tja_data)
            fumen_data = open_as_hex(dst_fumen_filepath)
            encrypted_fumen_data = encrypt_fumen_data(fumen_data)
            with open(dst_fumen_filepath, "wb") as f:
                f.write(encrypted_fumen_data)
            if fumen_filepath.endswith("_x.bin"):
                has_ura = True
        if not has_ura:
            course_data_list = tja_data["course_data"]
            idx = 0
            for course_data in course_data_list:
                if course_data["COURSE"] == "Edit":
                    idx = course_data_list.index(course_data)
                    break
            course_data_list.pop(idx)
            tja_data["course_data"] = course_data_list

        if get_datatable_exist():
            unique_id = available_unique_ids.pop(0)
            current_status.set_description_str("Generating datatable...")
            (append_music_ai_section, append_music_attribute, append_music_order, append_music_usbsetting,
             append_music_info, append_wordlist, append_reward, append_syougou,
             available_syougou_unique_ids) = generate_datatable(
                tja_data, unique_id, duration, available_shougou_unique_ids
            )
            append_data.append((append_music_ai_section, append_music_attribute, append_music_order,
                                append_music_usbsetting, append_music_info, append_wordlist, append_reward,
                                append_syougou))
        os.chdir(root_path)
        remove_dir(temp_song_path)
        retry = 0

    if get_datatable_exist():
        for data in append_data:
            music_ai_section_list.append(data[0])
            music_attribute_list.append(data[1])
            for music_order_data in data[2]:
                music_order_list.append(music_order_data)
            music_usbsetting_list.append(data[3])
            musicinfo_list.append(data[4])
            for wordlist_data in data[5]:
                wordlist_list.append(wordlist_data)
            for reward_data in data[6]:
                reward_list.append(reward_data)
            for shougou_data in data[7]:
                shougou_list.append(shougou_data)

        music_order_list = sorted(music_order_list, key=lambda x: x["genreNo"])

        (music_ai_section_list, music_attribute_list, music_order_list, musicinfo_list, wordlist_list,
         music_usbsetting_list, reward_list, shougou_list) = sort_datatable_key_sequence(
            (music_ai_section_list, music_attribute_list, music_order_list, musicinfo_list, wordlist_list,
             music_usbsetting_list, reward_list, shougou_list))

        write_datatable_files(
            (music_ai_section_list, music_attribute_list, music_order_list, musicinfo_list, wordlist_list,
             music_usbsetting_list, reward_list, shougou_list))

    remove_dir(temp_path)
    t.close()
    current_song.close()
    current_status.close()
    print("Complete\n")
    if get_datatable_exist():
        print("Available unique ids: " + str(available_unique_ids) + "\n")
        print("Number of available unique ids: " + str(len(available_unique_ids)) + "\n")
