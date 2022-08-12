# -*- coding: utf-8 -*-
'''
This script takes text files of labial and nasal stimulus words and produces two new text files with two columns, separated by a tab. The user must specify the relevant language.
The first column contains each word (with non-ASCII characters replaced) and an ID number.
The second column contains each word inside the correct carrier phrase.
The script also produces XML files for SpeechRecorder.

This version does not randomise the stimuli!!
'''

# import sys package to use the script in the command line
import sys

# import re package for searching text with regular expressions
import re

# import random package for randomisation
import random

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

# specify which carrier phrases are required based on the language entered
if language[0] == 'e':
    labial_phrase = english_labial_cp
    nasal_phrase = english_nasal_cp
    language_name = 'english'
    
elif language[0] == 'd' or language[0] == 'g':
    labial_phrase = german_labial_cp
    nasal_phrase = german_nasal_cp
    language_name = 'german'
    
elif language[0] == 'f':
    labial_phrase = french_labial_cp
    nasal_phrase = french_nasal_cp
    language_name = 'french'
    
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
    
    # flatten lst_times_n so that it's one big list with no sub-lists
    flat_lst_times_n = [item for sublist in lst_times_n for item in sublist]
    
    # make a copy of flat_lst_times_n
    lst_copy = flat_lst_times_n[:]
    
    # set the threshold with a placeholder number before the while-loop
    # this can be any positive number
    threshold = 1
    
    # keep track of the number of shuffles for information purposes
    n_shuffles = 0
    
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
            for i, v in enumerate(lst_copy):
                if lst_copy[i] == minimal_pair_dict[lst_copy[i - 1]] or lst_copy[i] == minimal_pair_dict[lst_copy[i - 2]]:
                    count += 1
        
        # update threshold with count, so that the loop can re-run or break as needed
        threshold = count
        
    # print n_shuffles for info
    print('n_shuffles =', n_shuffles, end = '\n\n')
        
    # return final randomised list with no consecutive duplicates
    return lst_copy


# define function for putting words in carrier phrases
def put_words_in_phrases(word_list, phrase, experiment):
    
    # extract the stimulus words and minimal pairs from the text file
    with open(word_list, encoding = 'UTF-8') as file:
        contents = file.read()
        contents = re.sub(r'\ble\b ', 'le_', contents)
        words = re.findall(r"[\w'’]+", contents, re.UNICODE)
        word_pairs = re.findall(r"([\w'’]+)\s*\/\s*([\w'’]+)", contents, re.UNICODE)
    
    # apply the copy_and_pseudo_randomise function to the stimulus words
    #randomised_words = copy_and_pseudo_randomise(words, word_pairs, n_copies = 3)
    
    # make a dictionary with minimal pairs as keys and numbers as values
    num_pair_dict = {}
    for pair, num in zip(word_pairs, range(1, len(word_pairs) + 1)):
        num_pair_dict[pair] = f'pair{num:02d}_'    
    
    # generate the file name for the new text files based on the language and the experiment    
    new_file_name = language_name + '_' + experiment + '.txt'
    
    # generate the ID numbers
    id_nums = range(1, len(words) + 1)
    
    # create a new text file with the above file name  
    # then for each word, replace the underscores in the carrier phrase with the word
    # then save each completed phrase to the new text file
    with open(new_file_name, 'w', encoding = 'UTF-8') as file:
        for word, id_num in zip(words, id_nums):
            line = phrase.replace('___', word)
            
            # add an underscore and ID number to each item code
            line = line.replace('##', f'_{id_num:02d}')
            
            # add an underscore and a minimal pair number to each item code
            for pair, num in num_pair_dict.items():
                if word in pair:
                    line = line.replace('++', num_pair_dict[pair])         
                
            # replace the first accented letter with an equivalent to ensure compatibility with ASCII
            # this is only required for the item names, not the actual stimulus text
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
            
            # replace underscore in 'le Caire' (etc) with space in the carrier phrase only (not the ID)
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
<recording beep="true" prerecdelay="800" recduration="4000" postrecdelay="100" itemcode="{}">\n\
    <recprompt>\n\
        <mediaitem mimetype="text/UTF-8">\n\
		{}\n\
		</mediaitem>\n\
    </recprompt>\n\
</recording>\n'

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
        
        file.write(opening.format(language_name.capitalize(), experiment.capitalize()))
        
        for text_pair in text_pairs:
            file.write(item.format(text_pair[0], text_pair[1]))
            
        file.write(ending)

# apply the make_SpeechRecorder_xml function to the labial and nasal stimulus codes and sentences 
make_SpeechRecorder_xml(language_name, 'labials')
make_SpeechRecorder_xml(language_name, 'nasals')

# print message to signal that the script has finished running
print('\nCreated XML files!')


