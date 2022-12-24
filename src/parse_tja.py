# -*- coding: utf-8 -*-
from charset_normalizer import from_path

from utils import *


def parse_tja(input_filepath: str) -> dict:
    song_id = os.path.basename(input_filepath).replace(".tja", "").lower()
    title = ""
    subtitle = ""
    course_data_list = []
    course_data = {}
    reading_course_data = False

    course_conversion_dict = {"4": "Edit", "3": "Oni", "2": "Hard", "1": "Normal", "0": "Easy",
                              "EDIT": "Edit", "ONI": "Oni", "HARD": "Hard", "NORMAL": "Normal", "EASY": "Easy"}

    tja_data = str(from_path(input_filepath).best())
    for i, line in enumerate(tja_data.splitlines()):
        try:
            if "//" in line:
                line = line.split("//", 1)[0]
            if "\\\\" in line:
                line = line.split("\\\\", 1)[0]
            line = line.strip()
            if line == "":
                continue
            if not reading_course_data:
                if line.startswith("TITLE:") or line.startswith("title:"):
                    title = line.split(":", 1)[1].strip()
                if line.startswith("SUBTITLE:") or line.startswith("subtitle:"):
                    if "--" in line:
                        subtitle = line.split("--", 1)[1].strip()
                    else:
                        subtitle = line.split(":", 1)[1].strip()
                if line.startswith("COURSE") or line.startswith("course"):
                    reading_course_data = True
                    course = line.split(":", 1)[1].strip().upper()
                    if course not in course_conversion_dict:
                        print("Invalid course %s in line %d in tja file %s" % (course, i, input_filepath))
                        return {}
                    course = course_conversion_dict[course]
                    course_data["COURSE"] = course
            else:
                if line.startswith("COURSE") or line.startswith("course"):
                    if reading_course_data:
                        course = course_data["COURSE"]
                        if "SCOREINIT" not in course_data:
                            print("No SCOREINIT in course %s in tja file %s" % (course, input_filepath))
                            return {}
                        if "SCOREDIFF" not in course_data:
                            print("No SCOREDIFF in course %s in tja file %s" % (course, input_filepath))
                            return {}
                        if "LEVEL" not in course_data:
                            print("No LEVEL in course %s in tja file %s" % (course, input_filepath))
                            return {}
                        course_data_list.append(course_data)
                        course_data = {}
                    reading_course_data = True
                    course = line.split(":", 1)[1].strip().upper()
                    if course not in course_conversion_dict:
                        print("Invalid course %s in line %d in tja file %s" % (course, i, input_filepath))
                        return {}
                    course = course_conversion_dict[course]
                    course_data["COURSE"] = course
                else:
                    if line.startswith("LEVEL") or line.startswith("level"):
                        course_data["LEVEL"] = line.split(":", 1)[1].strip()
                    if line.startswith("SCOREINIT") or line.startswith("scoreinit"):
                        scoreinit = line.split(":", 1)[1].strip()
                        if "," in scoreinit:
                            scoreinit = scoreinit.split(",", 1)[1]
                        if scoreinit == "":
                            scoreinit = "0"
                        course_data["SCOREINIT"] = scoreinit
                    if line.startswith("SCOREDIFF") or line.startswith("scorediff"):
                        scorediff = line.split(":", 1)[1].strip()
                        if "," in scorediff:
                            scorediff = scorediff.split(",", 1)[1]
                        if scorediff == "":
                            scorediff = "0"
                        course_data["SCOREDIFF"] = scorediff
        except Exception as e:
            print("Error parsing line %d in tja file %s: %s" % (i, input_filepath, e))
            return {}

    if reading_course_data:
        course = course_data["COURSE"]
        if "SCOREINIT" not in course_data:
            print("No SCOREINIT in course %s in tja file %s" % (course, input_filepath))
            return {}
        if "SCOREDIFF" not in course_data:
            print("No SCOREDIFF in course %s in tja file %s" % (course, input_filepath))
            return {}
        if "LEVEL" not in course_data:
            print("No LEVEL in course %s in tja file %s" % (course, input_filepath))
            return {}
        course_data_list.append(course_data)

    course_sequence = {"Edit": 0, "Oni": 1, "Hard": 2, "Normal": 3, "Easy": 4}
    course_data_list.sort(key=lambda x: course_sequence[x["COURSE"]])
    if len(course_data_list) < 4:
        print("Missing course in tja file: %s" % input_filepath)
        return {}
    data = {"song_id": song_id, "TITLE": title, "SUBTITLE": subtitle, "course_data": course_data_list}
    return data
