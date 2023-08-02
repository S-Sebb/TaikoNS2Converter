# -*- coding: utf-8 -*-
from utils import *


def generate_datatable(tja_data, unique_id, duration):
    title = tja_data["TITLE"]
    subtitle = tja_data["SUBTITLE"]
    if title == "nan":
        title = ""
    if subtitle == "nan":
        subtitle = ""

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

    if music_order_genre != "nan":
        music_order_genre = int(float(music_order_genre))
    else:
        music_order_genre = 0
    if music_info_genre != "nan":
        music_info_genre = int(float(music_info_genre))
    else:
        music_info_genre = 0

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
        inits.append(score_init)
        diffs.append(score_diff)
        if course_data["LEVEL"] != "nan":
            levels.append(int(course_data["LEVEL"]))
        else:
            levels.append(0)

    if not has_ura:
        inits.append("1000")
        diffs.append("10000")
        levels.append(0)

    song_id = tja_data["song_id"]

    music_ai_section_num = "3" if duration < 100 else "5"


    append_music_ai_section = {
        "id": song_id,
        "uniqueId": unique_id,
        "easy": music_ai_section_num,
        "normal": music_ai_section_num,
        "hard": music_ai_section_num,
        "oni": music_ai_section_num,
        "ura": music_ai_section_num if has_ura else 3
    }

    append_music_attribute = {
        "id": song_id,
        "uniqueId": unique_id,
        "new": True,
        "canPlayUra": has_ura,
        "doublePlay": False,
        "tag1": "",
        "tag2": "",
        "tag3": "",
        "tag4": "",
        "tag5": "",
        "tag6": "",
        "tag7": "",
        "tag8": "",
        "tag9": "",
        "tag10": "",
        "donBg1p": "",
        "donBg2p": "",
        "dancerDai": "",
        "dancer": "",
        "danceNormalBg": "",
        "danceFeverBg": "",
        "rendaEffect": "",
        "fever": "",
        "donBg1p1": "",
        "donBg2p1": "",
        "dancerDai1": "",
        "dancer1": "",
        "danceNormalBg1": "",
        "danceFeverBg1": "",
        "rendaEffect1": "",
        "fever1": ""
    }

    append_music_order = {
        "genreNo": music_order_genre,
        "id": song_id,
        "uniqueId": unique_id,
        "closeDispType": 0
    }

    append_music_info = {
        "id": song_id,
        "uniqueId": unique_id,
        "genreNo": music_info_genre,
        "songFileName": "sound/song_%s" % song_id,
        "papamama": False,
        "branchEasy": False,
        "branchNormal": False,
        "branchHard": False,
        "branchMania": False,
        "branchUra": False,
        "starEasy": int(levels[0]),
        "starNormal": int(levels[1]),
        "starHard": int(levels[2]),
        "starMania": int(levels[3]),
        "starUra": int(levels[4]) if has_ura else 0,
        "shinutiEasy": int(inits[0]),
        "shinutiNormal": int(inits[1]),
        "shinutiHard": int(inits[2]),
        "shinutiMania": int(inits[3]),
        "shinutiUra": int(inits[4]) if has_ura else 1000,
        "shinutiEasyDuet": int(inits[0]),
        "shinutiNormalDuet": int(inits[1]),
        "shinutiHardDuet": int(inits[2]),
        "shinutiManiaDuet": int(inits[3]),
        "shinutiUraDuet": int(inits[4]) if has_ura else 1000,
        "shinutiScoreEasy": int(diffs[0]),
        "shinutiScoreNormal": int(diffs[1]),
        "shinutiScoreHard": int(diffs[2]),
        "shinutiScoreMania": int(diffs[3]),
        "shinutiScoreUra": int(diffs[4]) if has_ura else 10000,
        "shinutiScoreEasyDuet": int(diffs[0]),
        "shinutiScoreNormalDuet": int(diffs[1]),
        "shinutiScoreHardDuet": int(diffs[2]),
        "shinutiScoreManiaDuet": int(diffs[3]),
        "shinutiScoreUraDuet": int(diffs[4]) if has_ura else 10000,
    }

    append_wordlist = [
        {
            "key": "song_%s" % song_id,
            "japaneseText": title,
            "japaneseFontType": 0
        },
        {
            "key": "song_sub_%s" % song_id,
            "japaneseText": subtitle,
            "japaneseFontType": 0
        },
        {
            "key": "song_detail_%s" % song_id,
            "japaneseText": "",
            "japaneseFontType": 0
        }
    ]

    return append_music_ai_section, append_music_attribute, append_music_order, append_music_info, append_wordlist
