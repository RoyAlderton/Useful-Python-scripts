# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 13:35:28 2022

@author: Roy Alderton

This script takes a Praat TextGrid and creates a text file containing all the
text in the intervals of one tier, essentially making a transcript.

Currently, the script only works for one tier called 'text', and each interval
is separated with a new line in the transcript.
    
The script should be saved in a folder with a sub-folder called 'TextGrids',
where the TextGrids to be processed should be located.

The script should be run in the command line by navigating to the correct
folder and entering a command in the following format:
    
    python transcribe_textgrids.py
    
If using Linux, you may need to replace 'python' with 'python3'.

You may not be able to run this file from the IPS server, in which case,
just copy everything to your computer and run it locally.

You may need to install the textgrids library if it isn't already on your
computer. You can do this by entering the following into the command prompt:
    
    pip install praat-textgrids

"""

import os
import textgrids

# Specify folder path where the TextGrids are located
path = "TextGrids/"
dir_list = os.listdir(path)

# Get a list of TextGrid files in the folder
tg_list = [file for file in dir_list if 'practice' not in file and file.endswith('.TextGrid')]

# For each TextGrid file in the list...
for file in tg_list:
    
    # Load the file as a TextGrid in Python
    tg = textgrids.TextGrid(path + file)
    
    # Create a new text file and write each interval text to it
    with open(file[:-9] + '.txt', 'w') as transcript:
        for interval in tg['text']:
            transcript.write(interval.text + '\n')
    
    # Print a message to check that the file has been successfully processed
    # (When transcript is opened, it acts as a TextIOWrapper object, which has 
    # a 'name' attribute that has to be accessed explicitly.)
    print('Successfully created {}!'.format(transcript.name))