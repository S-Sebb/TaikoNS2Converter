# -*- coding: utf-8 -*-
import math

from parse_tja import *


def generate_datatable(tja_data, unique_id, duration):
    title = tja_data["TITLE"]
    subtitle = tja_data["SUBTITLE"]

    music_order_genre = tja_data["genre"]
    if music_order_genre == "7":
        music_info_genre = "4"
    elif music_order_genre == "8":
        music_info_genre = "5"
    elif music_order_genre == "17":
        music_info_genre = "4"
    elif music_order_genre == "18":
        music_info_genre = "0"
    else:
        music_info_genre = music_order_genre

    course_data_list = tja_data["course_data"]
    course_sequence = {"Edit": 4, "Oni": 3, "Hard": 2, "Normal": 1, "Easy": 0}
    course_data_list.sort(key=lambda x: course_sequence[x["COURSE"]])
    if len(course_data_list) == 5:
        has_ura = True
        ura_flag = "true"
    else:
        has_ura = False
        ura_flag = "false"

    inits = []
    diffs = []
    levels = []
    for course_data in course_data_list:
        score_init = course_data["SCOREINIT"]
        score_diff = course_data["SCOREDIFF"]
        if int(score_diff) < 1000000:
            score_diff = "1000000"
        inits.append(score_init)
        diffs.append(score_diff)
        levels.append(course_data["LEVEL"])

    if not has_ura:
        inits.append("1000")
        diffs.append("10000")
        levels.append("0")

    song_id = tja_data["song_id"]

    music_ai_section_num = "3" if duration < 100 else "5"

    music_order_data = get_music_order_template() % (music_order_genre, song_id, unique_id)
    musicinfo_data = get_musicinfo_template() % (song_id, unique_id, music_info_genre, song_id,
                                                 levels[0], levels[1], levels[2], levels[3], levels[4],
                                                 inits[0], inits[1], inits[2], inits[3], inits[4],
                                                 inits[0], inits[1], inits[2], inits[3], inits[4],
                                                 diffs[0], diffs[1], diffs[2], diffs[3], diffs[4],
                                                 diffs[0], diffs[1], diffs[2], diffs[3], diffs[4])
    music_attribute_data = get_music_attribute_template() % (song_id, unique_id, ura_flag)
    wordlist_data = get_wordlist_template() % (song_id, title, song_id, subtitle, song_id)
    music_ai_section_data = get_music_ai_section_template() % (song_id, unique_id, music_ai_section_num,
                                                               music_ai_section_num, music_ai_section_num,
                                                               music_ai_section_num, music_ai_section_num)

    music_order_filepath = os.path.join(outputs_datatable_path, "music_order.txt")
    musicinfo_filepath = os.path.join(outputs_datatable_path, "musicinfo.txt")
    music_attribute_filepath = os.path.join(outputs_datatable_path, "music_attribute.txt")
    wordlist_filepath = os.path.join(outputs_datatable_path, "wordlist.txt")
    music_ai_section_filepath = os.path.join(outputs_datatable_path, "music_ai_section.txt")

    for filepath in [music_order_filepath, musicinfo_filepath, music_attribute_filepath, wordlist_filepath,
                     music_ai_section_filepath]:
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("")

    with open(music_order_filepath, "a", encoding="utf-8") as f:
        f.write(music_order_data)
    with open(musicinfo_filepath, "a", encoding="utf-8") as f:
        f.write(musicinfo_data)
    with open(music_attribute_filepath, "a", encoding="utf-8") as f:
        f.write(music_attribute_data)
    with open(wordlist_filepath, "a", encoding="utf-8") as f:
        f.write(wordlist_data)
    with open(music_ai_section_filepath, "a", encoding="utf-8") as f:
        f.write(music_ai_section_data)


def process_fumen(fumen_filepath, tja_data):
    filename_course_dict = {"_x.bin": "Edit", "_m.bin": "Oni", "_h.bin": "Hard", "_n.bin": "Normal", "_e.bin": "Easy"}
    filename = os.path.basename(fumen_filepath)
    course = ""
    for key in filename_course_dict:
        if filename.endswith(key):
            course = filename_course_dict[key]
            break
    if course == "":
        return tja_data
    hex_data = open_as_hex(fumen_filepath)
    course_data_list = tja_data["course_data"]
    course_data = {}
    index = -1
    for data in course_data_list:
        if data["COURSE"] == course:
            course_data = data
            index = course_data_list.index(data)
            break
    if index == -1:
        return tja_data
    course_data_list.pop(index)
    scoreinit = course_data["SCOREINIT"]
    scorediff = course_data["SCOREDIFF"]
    level = course_data["LEVEL"]

    if scoreinit != "0" and scorediff != "0" and scoreinit != "nan" and scorediff != "nan":
        if scoreinit.strip() != "" and scorediff.strip() != "":
            return tja_data

    start_pos = 568 * 2  # 568 = 0x238 start of fumen data
    note_data_length = 24 * 2
    note_type_length = 4 * 2
    scoreinit_length = 4 * 2

    total_balloon = 0
    note_type_count = {}
    total_renda_duration = 0
    for j in range(1, 13):
        note_type_count[j] = 0
    print(fumen_filepath)
    while start_pos < len(hex_data):
        note_type_start = start_pos
        note_type_end = note_type_start + note_type_length
        note_type = hex2int(hex_data[note_type_start:note_type_end])

        scoreinit_start = start_pos + 16 * 2
        scoreinit_end = scoreinit_start + scoreinit_length
        scoreinit = hex2int(hex_data[scoreinit_start:scoreinit_end])

        while note_type == 0:
            # Jump to next note
            while hex_data[start_pos:start_pos + 4 * 2] != "ffffffff":
                if start_pos >= len(hex_data):
                    break
                start_pos += 4 * 2
            while hex_data[start_pos:start_pos + 4 * 2] == "ffffffff":
                if start_pos >= len(hex_data):
                    break
                start_pos += 4 * 2
            start_pos += 12 * 2
            if start_pos >= len(hex_data):
                break
            note_type_start = start_pos
            note_type_end = note_type_start + note_type_length
            note_type = hex2int(hex_data[note_type_start:note_type_end])

            scoreinit_start = start_pos + 16 * 2
            scoreinit_end = scoreinit_start + scoreinit_length
            scoreinit = hex2int(hex_data[scoreinit_start:scoreinit_end])
        if note_type != 0:
            is_renda = False
            if note_type == 10 or note_type == 12:
                if scoreinit < 300:
                    total_balloon += scoreinit
                else:
                    is_renda = True
            if note_type == 6 or note_type == 9 or is_renda:
                renda_duration_start = start_pos + 20 * 2
                renda_duration_end = renda_duration_start + 4 * 2
                renda_duration = hex2float(hex_data[renda_duration_start:renda_duration_end])
                total_renda_duration += renda_duration
            note_type_count[note_type] += 1
        start_pos += note_data_length

    total_renda_duration /= 1000
    note_sum = 0
    for j in [1, 2, 3, 4, 5, 7, 8]:
        note_sum += note_type_count[j]
    scoreinit = math.ceil(((1000000 - total_balloon * 100 - total_renda_duration * 17 * 100) / note_sum) / 10) * 10
    score_max = round((total_renda_duration * 17 * 100 + note_sum * scoreinit + total_balloon * 100) / 10) * 10
    course_data_list.append({"COURSE": course, "LEVEL": level, "SCOREINIT": str(scoreinit),
                             "SCOREDIFF": str(score_max)})
    tja_data["course_data"] = course_data_list

    return tja_data
