# -*- coding: utf-8 -*-
from utils import *
import json


def generate_datatable(tja_data, unique_id, duration, available_syougou_unique_ids):
    title = tja_data["TITLE"]
    subtitle = tja_data["SUBTITLE"]

    music_order_genre = tja_data["genre"]
    if music_order_genre == "17":
        music_info_genre = "4"
    else:
        music_info_genre = music_order_genre

    course_data_list = tja_data["course_data"]
    course_sequence = {"Edit": 4, "Oni": 3, "Hard": 2, "Normal": 1, "Easy": 0}
    course_data_list.sort(key=lambda x: course_sequence[x["COURSE"]])
    if len(course_data_list) == 5:
        has_ura = True
    else:
        has_ura = False

    try:
        syougou_list = json.loads(tja_data["syougou"])
        syougou_type_list = json.loads(tja_data["syougou_type"])
        syougou_rarity_list = json.loads(tja_data["syougou_rarity"])
    except Exception as e:
        print("Error parsing syougou data: %s" % e)
        exit()

    if type(syougou_list) == str and syougou_type_list == int and syougou_rarity_list == int:
        syougou_list = [syougou_list]
        syougou_type_list = [syougou_type_list]
        syougou_rarity_list = [syougou_rarity_list]

    if len(syougou_list) != len(syougou_type_list) or len(syougou_list) != len(syougou_rarity_list):
        print("Error parsing syougou data: length mismatch")
        exit()

    inits = []
    diffs = []
    levels = []
    syougous = []
    note_counts = []
    balloon_counts = []
    renda_durations = []
    for course_data in course_data_list:
        renda_duration = course_data["course_renda_duration"]
        balloon_count = course_data["course_balloon_count"]
        note_count = course_data["course_note_count"]
        score_init = course_data["scoreinit"]
        score_diff = course_data["score_max"]
        inits.append(score_init)
        diffs.append(score_diff)
        levels.append(course_data["LEVEL"])
        note_counts.append(note_count)
        balloon_counts.append(balloon_count)
        renda_durations.append(renda_duration)

    levels = [int(x) for x in levels]
    inits = [int(x) for x in inits]
    diffs = [int(x) for x in diffs]

    song_id = tja_data["song_id"]

    music_ai_section_num = 3 if duration < 100 else 5

    append_music_ai_section = {
        "id": song_id,
        "uniqueId": unique_id,
        "easy": music_ai_section_num,
        "normal": music_ai_section_num,
        "hard": music_ai_section_num,
        "oni": music_ai_section_num,
        "ura": music_ai_section_num if has_ura else 3,
        "oniLevel11": "o" if levels[3] >= 10 else "",
        "uraLevel11": "o" if has_ura and levels[4] >= 10 else ""
    }

    append_music_attribute = {
        "id": song_id,
        "uniqueId": unique_id,
        "new": True,
        "doublePlay": False,
        "isNotCopyright": True,
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
        "ensoPartsID1": 0,
        "ensoPartsID2": 0,
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

    append_music_order = []
    if music_order_genre != "17":
        append_music_order.append({
            "genreNo": int(music_order_genre),
            "id": song_id,
            "uniqueId": unique_id,
            "closeDispType": 0
        })

    append_music_usbsetting = {
        "id": song_id,
        "uniqueId": unique_id,
        "usbVer": ""
    }

    append_music_info = {
        "id": song_id,
        "uniqueId": unique_id,
        "genreNo": int(music_info_genre),
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
        "easyOnpuNum": int(note_counts[0]),
        "normalOnpuNum": int(note_counts[1]),
        "hardOnpuNum": int(note_counts[2]),
        "maniaOnpuNum": int(note_counts[3]),
        "uraOnpuNum": int(note_counts[4]) if has_ura else 1000,
        "rendaTimeEasy": renda_durations[0],
        "rendaTimeNormal": renda_durations[1],
        "rendaTimeHard": renda_durations[2],
        "rendaTimeMania": renda_durations[3],
        "rendaTimeUra": renda_durations[4] if has_ura else 1000,
        "fuusenTotalEasy": balloon_counts[0],
        "fuusenTotalNormal": balloon_counts[1],
        "fuusenTotalHard": balloon_counts[2],
        "fuusenTotalMania": balloon_counts[3],
        "fuusenTotalUra": balloon_counts[4] if has_ura else 1000,
        "spikeOnEasy": False,
        "spikeOnNormal": False,
        "spikeOnHard": False,
        "spikeOnOni": False,
        "spikeOnUra": False
    }

    append_wordlist = [
        {
            "key": "song_%s" % song_id,
            "japaneseText": title,
            "japaneseFontType": 0,
            "englishUsText": title,
            "englishUsFontType": 1,
            "chineseTText": title,
            "chineseTFontType": 2,
            "chineseSText": title,
            "chineseSFontType": 4
        },
        {
            "key": "song_sub_%s" % song_id,
            "japaneseText": subtitle,
            "japaneseFontType": 0,
            "englishUsText": subtitle,
            "englishUsFontType": 1,
            "chineseTText": subtitle,
            "chineseTFontType": 2,
            "chineseSText": subtitle,
            "chineseSFontType": 4
        },
        {
            "key": "song_detail_%s" % song_id,
            "japaneseText": "",
            "japaneseFontType": 0,
            "englishUsText": "",
            "englishUsFontType": 1,
            "chineseTText": "",
            "chineseTFontType": 2,
            "chineseSText": "",
            "chineseSFontType": 4
        }
    ]

    append_reward = []
    append_syougou = []

    for syougou, syougou_type, syougou_rarity in zip(syougou_list, syougou_type_list, syougou_rarity_list):
        if syougou == "":
            continue
        syougou_unique_id = available_syougou_unique_ids.pop(0)
        reward_message = "result_reward_fullcombo" if syougou_type in [0, 1] else "result_reward_get"
        new_syougou = {
            "uniqueId": syougou_unique_id,
            "rarity": int(syougou_rarity),
            "isNotCopyright": True
        }
        new_reward = {
            "releaseType": syougou_type,
            "songuid1": unique_id,
            "songuid2": -1,
            "songuid3": -1,
            "songuid4": -1,
            "songuid5": -1,
            "songtag": "",
            "tokenId": -1,
            "qrId": -1,
            "value": -1,
            "ensoType": -1,
            "reward_message": reward_message,
            "rewardType": 0,
            "rewardUniqueId": syougou_unique_id
        }
        new_wordlist = {
            "key": "syougou_%s" % syougou_unique_id,
            "japaneseText": str(syougou),
            "japaneseFontType": 0,
            "englishUsText": str(syougou),
            "englishUsFontType": 0,
            "chineseTText": str(syougou),
            "chineseTFontType": 0,
            "chineseSText": str(syougou),
            "chineseSFontType": 0
        }
        append_syougou.append(new_syougou)
        append_reward.append(new_reward)
        append_wordlist.append(new_wordlist)

    return append_music_ai_section, append_music_attribute, append_music_order, append_music_usbsetting, \
        append_music_info, append_wordlist, append_reward, append_syougou, available_syougou_unique_ids
