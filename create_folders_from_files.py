# -*- coding: utf-8 -*-
"""
Created on Sat Jun 17 10:27:57 2023

@author: Roy
"""

# create new folder for each file in a folder, named after the file
# then move the original file into the corresponding new folder

import os
import shutil

list_of_files = [file for file in os.listdir() if '.textgrid' in file.lower()]

print(list_of_files)

# print('TPS ' + 'Sophie M 2 hVd.TextGrid'[:-9].replace(' 2', ''))

for file in list_of_files:
    new_folder = 'TPS-Pre ' + file[:-9].replace(' 2', '')
    os.mkdir(new_folder)
    shutil.move(file, new_folder)
    

