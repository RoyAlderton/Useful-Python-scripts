# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 16:50:49 2021

@author: Roy Alderton

This script produces text files containing the stimulus text of a set of WAV
files to be used with the WebMAUS automatic segmentation and labelling tool.

The script must be saved in the same folder as the WAV files. The folder must
also contain a text file with the tab-separated stimulus codes and phrases
used for the experiment. This is the text file produced by the 'get_xml.py' 
script when creating SpeechRecorder XML files, e.g. '01_de_nasals_randomised.txt'.
The script will produce a text file with the same name as each WAV file in the
folder. The content of each text file will match the stimulus phrase for that
particular file.

The script should be run in the command line by navigating to the correct
folder and entering a command in the following format:
    
    python make_webmaus_text_files.py [stimulus_text_file]
    
An example for German nasals in Windows is shown below:
    
    python make_webmaus_text_files.py 01_de_nasals_randomised.txt
    
If using Linux, you may need to replace 'python' with 'python3'.

You may not be able to run this file from the IPS server, in which case,
just copy everything to your computer and run it locally.
"""

# import relevant packages
import os
import sys
import re

# specify stimulus list text file as the argument in the command line
stimulus_list_file_name = sys.argv[1]

# get list of all WAV files in the current folder
wav_file_names = [file_name for file_name in os.listdir() if file_name.endswith('.wav')]

# make version of above list but without '.wav'
no_wav = [file_name[:-4] for file_name in wav_file_names]

# make version of above list but without the speaker ID, nor the repetition 
# and order numbers
no_prefixes_or_suffixes = [file_name[4:-8] for file_name in wav_file_names]

# open the stimulus list and extract the ID codes and phrases as separate lists
with open(stimulus_list_file_name, encoding = 'UTF-8') as file:
    contents = file.read()
    stimulus_ids = re.findall(r'(^.*)\t', contents, flags = re.MULTILINE | re.UNICODE)
    stimulus_phrases = re.findall(r'\t(.*)$', contents, flags = re.MULTILINE | re.UNICODE)

# make a dictionary where each ID code is the key and its corresponding phrase
# is the value
id_phrase_dict = {}
for stimulus_id, stimulus_phrase in zip(stimulus_ids, stimulus_phrases):
    id_phrase_dict[stimulus_id] = stimulus_phrase

# make a dictionary where each file name (sans '.wav') is the key and its 
# corresponding ID code is the value
file_id_dict = {}
for long_file_name, short_file_name in zip(no_wav, no_prefixes_or_suffixes):
    file_id_dict[long_file_name] = short_file_name

# over-write the values in file_id_dict with the values from id_phrase_dict,
# i.e. the stimulus phrases
for non_wav_file_name, stimulus in file_id_dict.items():
    file_id_dict[non_wav_file_name] = id_phrase_dict[stimulus]

print(file_id_dict)

# for each pair of WAV file names and phrases in file_id_dict, make a new text
# file with the same name and write the corresponding phrase to it
for non_wav_file_name, phrase in file_id_dict.items():
    with open(non_wav_file_name + '.txt', 'w', encoding = 'UTF-8') as file: 
        file.write(phrase)