# -*- coding: utf-8 -*-
from utils import *


def convert_sound(acb_filepath, preview_filepath):
    wav_filepath = acb2wav(acb_filepath)
    if preview_filepath != "":
        preview_wav_filepath = acb2wav(preview_filepath)
    else:
        preview_wav_filepath = ""


def acb2wav(byte_filepath):
    byte_filename = os.path.basename(byte_filepath)
    new_byte_filepath = os.path.join(find_cur_dir(), byte_filename)
    if os.path.exists(new_byte_filepath):
        os.remove(new_byte_filepath)
    copy_file(byte_filepath, new_byte_filepath)
    acb2hcas(new_byte_filepath)
    hca_filepath = os.path.join(find_cur_dir(), "_acb_" + byte_filename, "internal", "cue_000000.hca")
    wav_filepath = os.path.join(find_cur_dir(), byte_filename.replace(".bytes", ".wav"))
    hcas2wav(hca_filepath, wav_filepath)
    return wav_filepath
