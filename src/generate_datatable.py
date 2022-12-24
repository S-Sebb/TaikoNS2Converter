# -*- coding: utf-8 -*-
from utils import *
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


if __name__ == '__main__':
    init()

    filepaths = enumerate_files(inputs_tja_path)[0]
    tja_filepaths = [filepath for filepath in filepaths if filepath.endswith(".tja")]

    if not tja_filepaths:
        print("No TJA files found in inputs/tja")
        input("Press Enter to exit...")
        exit()

    existing_musicinfo_data = get_musicinfo_data()
    available_unique_ids = [_ for _ in range(1599)]
    for musicinfo in existing_musicinfo_data:
        available_unique_ids.remove(musicinfo["uniqueId"])
    available_unique_ids = sorted(available_unique_ids)

    for i in range(len(tja_filepaths)):
        tja_filepath = tja_filepaths[i]
        cur_tja_data = parse_tja(tja_filepath)
        genre = os.path.basename(os.path.dirname(tja_filepath)).split(" ")[0]
        cur_tja_data["genre"] = genre
        cur_unique_id = available_unique_ids.pop(0)
        generate_datatable(cur_tja_data, cur_unique_id, 101)

    print("Done! Output files are in outputs/datatable.")
