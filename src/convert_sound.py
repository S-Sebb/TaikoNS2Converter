# -*- coding: utf-8 -*-
from utils import *


def convert_sound(acb_filepath, preview_filepath):
    acb_filename = os.path.basename(acb_filepath)
    new_acb_filepath = os.path.join(find_cur_dir(), acb_filename)
    if os.path.exists(new_acb_filepath):
        os.remove(new_acb_filepath)
    copy_file(acb_filepath, new_acb_filepath)
    acb2hcas(new_acb_filepath)
