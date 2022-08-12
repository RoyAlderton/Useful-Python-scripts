# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 14:47:44 2022

@author: Roy Alderton

This script prints out the file names of any stimuli that were re-recorded in
an experiment.

The script must be saved in the same folder as the WAV files. 

It should be run in the command line by navigating to the correct
folder and entering a command in the following format:
    
    python print_re-recorded_tokens.py
    
If using Linux, you may need to replace 'python' with 'python3'.

You may not be able to run this file from the IPS server, in which case,
just copy the files to your computer and run it locally.
"""

import os

# get list of all text files in the current folder
txt_file_names = [file_name for file_name in os.listdir() if file_name.endswith('.wav')]

# get above list but without suffix
no_suffix = [file_name[:-4] for file_name in txt_file_names]

# get all the repetition numbers at the end of each suffix-less file name
rep_numbers = [int(file_name[-2:]) for file_name in no_suffix]
#print(rep_numbers)

# get the most frequent repetition number (the mode)
# this is used instead of the more obvious minimum value, as occasionally speakers will be recording a token for the first time...
# ... in the re-recording if it was accidentally forgotten in the first session
mode = max(set(rep_numbers), key = rep_numbers.count)

# get above list but only where the final digit is higher than the mode
# (i.e. the re-recorded tokens)
repeats = [file_name for file_name in no_suffix if int(file_name[-1]) > mode]

if repeats:
    # print each file name from the above list on a new line
    print('\nOut of {} files, {} likely repeated tokens were found:\n'.format(len(no_suffix), len(repeats)), '\n'.join(repeats), sep = '')
else:
    print('\nNo repeated tokens found out of {}.'.format(len(no_suffix)))

reminder = """
Remember, the files ending in __{:02d} are NOT usually the ones you want to delete!
In most cases, you will want to delete the corresponding __{:02d} versions of these
files, as they are likely to contain errors (i.e. where the speaker messed up).
""".format(mode + 1, mode)

if repeats:
    print(reminder, end = '')