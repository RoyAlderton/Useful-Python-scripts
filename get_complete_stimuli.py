# -*- coding: utf-8 -*-
'''
This script takes text files of labial and nasal stimulus words and produces two new text files with two columns, separated by a tab. The user must specify the relevant language.
The first column contains each word (with non-ASCII characters replaced) and an ID number.
The second column contains each word inside the correct carrier phrase.
The script also produces XML files for SpeechRecorder.
'''

# import sys package to use the script in the command line
import sys

# import re package for searching text with regular expressions
import re

# import random package for randomisation
import random

import functools
import numpy as np

# save user-specified argments - the two text files and the language
labial_words = sys.argv[1]
nasal_words = sys.argv[2]
language = sys.argv[3].lower()

# specify arguments in the script for testing purposes
#labial_words = 'labials_messy.txt'
#nasal_words = 'nasals_messy.txt'
#language = 'de'

# generate the carrier phrases for all languages
english_labial_cp = '++___##\tBut Tessa had said “___” properly.'
english_nasal_cp = '++___##\tHe’ll tell Cleo “___” soon.'

german_labial_cp = '++___##\tAber Elsa legt gern „___“ beiseite.'
german_nasal_cp = '++___##\tEr las Kleo „___“ zweimal vor.'

french_labial_cp = '++___##\tMais elle déclarait « ___ » par hasard.'
french_nasal_cp = '++___##\tJe dis à Cléo « ___ » samedi.'

# specify which carrier phrases and other bits are required based on the language entered
if language[0] == 'e':
    labial_phrase = english_labial_cp
    nasal_phrase = english_nasal_cp
    language_name = 'english'
    break_text = 'Well done! Time for a quick break.'
    
elif language[0] == 'd' or language[0] == 'g':
    labial_phrase = german_labial_cp
    nasal_phrase = german_nasal_cp
    language_name = 'german'
    break_text = 'Sehr gut! Es ist Zeit für eine kurze Pause.'
    
elif language[0] == 'f':
    labial_phrase = french_labial_cp
    nasal_phrase = french_nasal_cp
    language_name = 'french'
    break_text = "Très bien ! Il est temps de faire une petite pause."
    
else:
    print('No valid language specified!')


# define function for copying and randomising word list (avoiding consecutive duplicates and minimal pairs)
def copy_and_pseudo_randomise(lst, pairs = None, n_copies = 3):
    
    # make a dictionary of minimal pairs
    if pairs:
        minimal_pair_dict = {}
        for i in pairs:
            minimal_pair_dict[i[0]] = i[1]
            minimal_pair_dict[i[1]] = i[0]
    
    # make copies of the list, specified by n_copies (default = 3); produces a list of lists    
    lst_times_n = [lst[:] for i in range(n_copies)]
    print(lst_times_n)
    
    # keep track of the number of shuffles for information purposes
    n_shuffles = 0
    
    for lst_copy in lst_times_n:
        
        # set the threshold with a placeholder number before the while loop
        # this can be any positive number
        threshold = 1
        
        # keep shuffling the list, only stopping if threshold is set to 0
        while threshold != 0:
            random.shuffle(lst_copy)
            n_shuffles += 1
            
            # (re)set count to 0
            count = 0
            
            # count number of consecutive (and two-away) duplicate items
            for i, v in enumerate(lst_copy):
                if lst_copy[i] == lst_copy[i - 1] or lst_copy[i] == lst_copy[i - 2]:
                    count += 1
                    
            # count number of consecutive (and two-away) minimal pairs
            if pairs:
                for i, v in enumerate(lst):
                    if lst_copy[i] == minimal_pair_dict[lst_copy[i - 1]] or lst_copy[i] == minimal_pair_dict[lst_copy[i - 2]]:
                        count += 1
            
            # update threshold with count, so that the loop can re-run or break as needed
            threshold = count
            
    # if the words either side of the breaks are duplicates, move the last word from the first list to the penultimate position (i.e. one place back)
    # the two-away randomisation procedure above will ensure no consecutive duplicates or minimal pairs, even after this movement has taken place        
    if lst_times_n[0][-1] == lst_times_n[1][0]:
        final_word = lst_times_n[0].pop(-1)
        lst_times_n[0].insert(-1, final_word)
        
    if lst_times_n[1][-1] == lst_times_n[2][0]:
        final_word = lst_times_n[1].pop(-1)
        lst_times_n[1].insert(-1, final_word)
        
    # print n_shuffles for info
    print('n_shuffles =', n_shuffles, end = '\n\n')
        
    # return final randomised list of lists with no consecutive duplicates
    return lst_times_n


# define function for putting words in carrier phrases
def put_words_in_phrases(word_list, phrase, experiment):
    
    # extract the stimulus words and minimal pairs from the text file
    with open(word_list, encoding = 'UTF-8') as file:
        contents = file.read()
        contents = re.sub(r'\ble\b ', 'le_', contents)
        words = re.findall(r"[\w'’]+", contents, re.UNICODE)
        word_pairs = re.findall(r"([\w'’]+)\s*\/\s*([\w'’]+)", contents, re.UNICODE)
    
    # apply the copy_and_pseudo_randomise function to the stimulus words
    randomised_words = copy_and_pseudo_randomise(words, word_pairs, n_copies = 3)
    
    # make a dictionary with minimal pairs as keys and numbers as values
    num_pair_dict = {}
    for pair, num in zip(word_pairs, range(1, len(word_pairs) + 1)):
        num_pair_dict[pair] = f'pair{num:02d}_'    
    
    # generate the file name for the new text files based on the language and the experiment    
    new_file_name = language_name + '_' + experiment + '.txt'
    
    # generate the ID numbers
    # make a list of numbers based on the total number of stimuli (list of lists)
    # https://www.kite.com/python/answers/how-to-get-the-size-of-a-list-of-lists-in-python
    #id_nums = range(1, len(randomised_words) + 1)
    id_nums = list(range(1, functools.reduce(lambda count, element: count + len(element), randomised_words, 0) + 1))
    
    # split the list of ID numbers into 3 equally sized sub-lists
    id_blocks = np.split(np.array(id_nums), 3)
    
    # insert item codes for breaks in id_blocks
    id_blocks_with_breaks = np.append(id_blocks[0], 'break01')
    id_blocks_with_breaks = np.append(id_blocks_with_breaks[1], 'break02')
    
    # create a new text file with the above file name
    # then do various text processing tasks on each item in each block
    with open(new_file_name, 'w', encoding = 'UTF-8') as file:
        
        # keep track of number of blocks (repetitions)
        block_count = 0
        
        for word_block, id_block in zip(randomised_words, id_blocks):
            
            # add 1 to block_count for each block
            block_count += 1
            
            for word, id_num in zip(word_block, id_block):
                
                # replace the underscores in the carrier phrase with the word
                line = phrase.replace('___', word)
                
                # add block number and ID number to each item code
                line = line.replace('##', f'_{block_count:01d}_{id_num:02d}')
                
                # add an underscore and a minimal pair number to each item code
                for pair, num in num_pair_dict.items():
                    if word in pair:
                        line = line.replace('++', num_pair_dict[pair])         
                    
                # replace the accented letters in item codes with ASCII equivalents
                # German letters
                line = line.replace('ä', 'ae', 1)
                line = line.replace('Ä', 'Ae', 1)
                line = line.replace('ö', 'oe', 1)
                line = line.replace('Ö', 'Oe', 1)
                line = line.replace('ü', 'ue', 1)
                line = line.replace('Ü', 'Ue', 1)
                line = line.replace('ß', 'ss', 1)
                
                # French letters
                line = line.replace('à', 'a', 1)
                line = line.replace('â', 'a', 1)
                line = line.replace('ç', 'c', 1)
                line = line.replace('é', 'e', 1)
                line = line.replace('ê', 'e', 1)
                line = line.replace('è', 'e', 1)
                line = line.replace('ë', 'e', 1)
                line = line.replace('î', 'i', 1)
                line = line.replace('ï', 'i', 1)
                line = line.replace('œ', 'oe', 1)
                line = line.replace('û', 'u', 1)
                
                # special cases (e.g. if there are two of the same accented letter in the word)
                line = line.replace('eté', 'ete')
                if language_name == 'french':
                    line = line.replace('Cleo', 'Cléo')
                
                # replace underscore after 'le' with a space in the carrier phrase only (not the ID)
                line = line.replace(' le_', ' le ', 1)
                
                # replace apostrophe (two variants) with nothing in ID only
                line = line.replace("'", '', 1)
                line = line.replace("’", '', 1)
                
                # reset words in the carrier phrase in case characters were overwritten
                line = line.replace('declarait', 'déclarait')
                line = line.replace(' a ', ' à ')
                line = line.replace('Hell', "He’ll")
                
                # print each line in the console and write it to the new text file
                print(line)
                file.write('%s\n' % line)
            
            # add the break items at the end of blocks 1 and 2
            if block_count <= 2:
                file.write('%s\n' % f'break_{block_count:02d}\t{break_text}')
            
# apply the put_words_in_phrases function to the labial and nasal stimulus words        
put_words_in_phrases(labial_words, labial_phrase, 'labials')
print('\n', end = '')
put_words_in_phrases(nasal_words, nasal_phrase, 'nasals')

# print message to signal that the function above has finished running
print('\nCreated text files!')


# define function to make XML file for SpeechRecorder
def make_SpeechRecorder_xml(language_name, experiment):
    
    # specify input file name based on new_file_name generated earlier
    input_file_name = language_name + '_' + experiment + '.txt'

    # extract the pairs of item codes and sentences from the code + sentence text file
    with open(input_file_name, encoding = 'UTF-8') as file:
        new_contents = file.read()
        text_pairs = re.findall(r'(\S+)\t(.*)', new_contents)
        #print(text_pairs)
    
# set opening text for the XML file
# each pair of curly brackets {} represents a slot to be filled in with text  
    opening = '\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n\
<!DOCTYPE script SYSTEM "SpeechRecPrompts_4.dtd">\n\
<script id="{}_{}">\n\
    <recordingscript>\n\
        <section mode="autoprogress" name="stimuli" order="sequential" promptphase="idle" speakerdisplay="false">\n\n'

# set text for each item for the XML file
# each pair of curly brackets {} represents a slot to be filled in with text    
    item = '\
<recording prerecdelay="800" recduration="4000" postrecdelay="100" beep="true" itemcode="{}">\n\
    <recprompt>\n\
        <mediaitem mimetype="text/UTF-8">\n\
		{}\n\
		</mediaitem>\n\
    </recprompt>\n\
</recording>\n'

# set text for break items for the XML file
# each pair of curly brackets {} represents a slot to be filled in with text  
    break_item = '\
<recording prerecdelay="800" recduration="4000" postrecdelay="100" beep="false" itemcode="{}">\n\
    <recprompt>\n\
        <mediaitem mimetype="text/UTF-8">\n\
		{}\n\
		</mediaitem>\n\
    </recprompt>\n\
</recording>\n' # file.write(break_item.format('break01 / break02', break_text))

# set ending text for the XML file
    ending = '\n\
        </section>\n\
    </recordingscript>\n\
</script>'
    
    # set output XML file name
    xml_file_name = input_file_name[:-4] + '_for_SpeechRecorder.xml'
    
    # create new XML file and write each item text to it, plus opening and ending text
    # the .format parts show what will fill in the curly bracket {} slots in the text
    with open(xml_file_name, 'w', encoding = 'UTF-8') as file:
        
        # write opening text to file
        file.write(opening.format(language_name.capitalize(), experiment.capitalize()))
        
        # write item text to file, with break variant as needed
        for text_pair in text_pairs:
            if 'break' in text_pair[0]:
                file.write(break_item.format(text_pair[0], text_pair[1]))
            else:
                file.write(item.format(text_pair[0], text_pair[1]))
                
        # write ending text to file    
        file.write(ending)


# apply the make_SpeechRecorder_xml function to the labial and nasal stimulus codes and sentences 
make_SpeechRecorder_xml(language_name, 'labials')
make_SpeechRecorder_xml(language_name, 'nasals')

# print message to signal that the script has finished running
print('\nCreated XML files!')


