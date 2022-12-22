# -*- coding: utf-8 -*-
import os.path
import wave

from utils import *


def convert_sound(acb_filepath, preview_filepath, song_id):
    wav_filepath = acb2wav(acb_filepath)
    idsp_filepath = wav_filepath.replace(".wav", ".idsp")
    wav2idsp(wav_filepath, idsp_filepath)
    template_nus3bank_data = get_nu3bank_template()

    has_preview = preview_filepath != ""

    if has_preview:
        preview_wav_filepath = acb2wav(preview_filepath)
        preview_idsp_filepath = preview_wav_filepath.replace(".wav", ".idsp")
        wav2idsp(preview_wav_filepath, preview_idsp_filepath)
        with wave.open(wav_filepath) as f:
            preview_time = f.getnframes() / f.getframerate()
        file_size = os.path.getsize(preview_idsp_filepath) + os.path.getsize(idsp_filepath)
    else:
        preview_time = 0
        file_size = os.path.getsize(idsp_filepath)
        preview_idsp_filepath = ""

    # Replace unique ID
    unique_id = abs(hash(song_id)) % 65536
    unique_id = int2hex(unique_id, 4)
    template_nus3bank_data = template_nus3bank_data.replace("aaaa", unique_id)

    # Replace preview time
    preview_time = int(preview_time * 1000)
    preview_time = int2hex(preview_time, 8)
    template_nus3bank_data = template_nus3bank_data.replace("bbbbbbbb", preview_time)

    # Replace audio file size
    file_size = int2hex(file_size, 8)
    template_nus3bank_data = template_nus3bank_data.replace("cccccccc", file_size)

    # Replace song id
    template_nus3bank_data = template_nus3bank_data.replace(str2hex("NIJIRO"), str2hex(song_id))

    # Inject idsp
    template_nus3bank_data += open_as_hex(idsp_filepath)
    if has_preview:
        template_nus3bank_data += open_as_hex(preview_idsp_filepath)

    # Save nus3bank
    nus3bank_filepath = os.path.join(find_cur_dir(), "song_" + song_id + ".nus3bank")
    save_hex(nus3bank_filepath, template_nus3bank_data)
    return nus3bank_filepath


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
