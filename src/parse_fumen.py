# -*- coding: utf-8 -*-
from utils import *
import math

def parse_fumen(fumen_filepath, tja_data):
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

    total_balloon_hit_count = 0
    note_type_count = {}
    total_renda_duration = 0
    for j in range(1, 14):
        note_type_count[j] = 0
    try:
        while start_pos < len(hex_data):
            while hex_data[start_pos: start_pos + 4 * 2] == "00000000":
                start_pos += 64 * 2
                if start_pos >= len(hex_data):
                    break
            if start_pos >= len(hex_data):
                break
            note_type_start = start_pos
            note_type_end = note_type_start + note_type_length
            note_type = hex2int(hex_data[note_type_start:note_type_end])
            is_renda = False
            if note_type == 10 or note_type == 12:
                balloon_hit_count = hex2int(hex_data[start_pos + 16 * 2: start_pos + 20 * 2])
                if balloon_hit_count < 300:
                    total_balloon_hit_count += balloon_hit_count
                elif balloon_hit_count < 1000:
                    is_renda = True
            elif note_type == 6 or note_type == 9:
                is_renda = True
            if is_renda:
                renda_duration = hex2float(hex_data[start_pos + 20 * 2:start_pos + 24 * 2])
                total_renda_duration += renda_duration
            note_type_count[note_type] += 1
            if note_type == 6 or note_type == 9:
                start_pos += 8 * 2
            start_pos += note_data_length

        total_renda_duration /= 1000
        note_sum = 0
        for j in [1, 2, 3, 4, 5, 7, 8]:
            note_sum += note_type_count[j]
        if course == "Edit" or course == "Oni":
            renda_per_sec = 17
        elif course == "Hard":
            renda_per_sec = 11
        elif course == "Normal":
            renda_per_sec = 8
        else:
            renda_per_sec = 6
        scoreinit = math.ceil(((1000000 - total_balloon_hit_count * 100 -
                                total_renda_duration * renda_per_sec * 100) / note_sum) / 10) * 10
        score_max = round((total_renda_duration * renda_per_sec * 100 +
                           note_sum * scoreinit + total_balloon_hit_count * 100) / 10) * 10
    except Exception as e:
        print("\n")
        print("Branching detected in fumen file: %s, unsupported operation, exiting..." % fumen_filepath)
        exit()
    course_data_list.append({"COURSE": course, "LEVEL": level, "scoreinit": str(scoreinit),
                             "score_max": str(score_max), "course_renda_duration": total_renda_duration,
                             "course_note_count": note_sum, "course_balloon_count": total_balloon_hit_count})
    tja_data["course_data"] = course_data_list

    return tja_data
