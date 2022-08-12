# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 11:38:38 2022

@author: Roy Alderton

This script renames files so that their pair numbers are correct, in cases where the pair numbers were based on the larger set of German stimuli with word-medial velar tokens.

The script should be saved in the same folder as the files to be renamed. The file extension of the files to be renamed (e.g. WAV, TextGrid, etc) must be specified as an argument.

The script should be run in the command line by navigating to the correct
folder and entering a command in the following format:
    
    python correct_pair_numbers.py [file_extension]
    
E.g. if you are running the script on .wav files, you would enter:
    
    python correct_pair_numbers.py .wav
    
If using Linux, you may need to replace 'python' with 'python3'.

You may not be able to run this file from the IPS server, in which case,
just copy everything to your computer and run it locally.
"""

import os
import sys
import re

file_extension = sys.argv[1]

# Get list of all files in the current folder with specified file extension
file_names = [file_name for file_name in os.listdir() if os.path.splitext(file_name)[1] == file_extension]

# Make version of above list but without file extension suffix
no_suffix = [os.path.splitext(file_name)[0] for file_name in file_names]

# Set regex pattern to get pair numbers
pattern = re.compile("p(\d{2})")

# Sort no_suffix list by pair number
no_suffix.sort(key = lambda x: int(pattern.search(x).group(1)))

# Take pair numbers from file names and subtract values from them as
# appropriate, then put them into a list of new file names.
# Pair numbers 1-5 don't need changing
# Pair numbers 6-9 need reducing by 1
# Pair numbers 10+ need reducing by 2
new_names = []
for item in no_suffix:
    pair_no = int(re.search(r'p(\d{2})', item).group(1))
    if pair_no > 6 and pair_no < 10:
        pair_no -= 1
    elif pair_no >= 10:
        pair_no -= 2
    pair_id = 'p' + f'{pair_no:02d}'
    new_name = re.sub(r'p\d{2}', pair_id, item)
    new_names.append(new_name)
    
# Rename each file, replacing the old file name with the new one
for old_name, new_name in zip(no_suffix, new_names):
    print(old_name, new_name)
    os.rename(old_name + file_extension, new_name + file_extension)
