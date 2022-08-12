# -*- coding: utf-8 -*-
'''
Created on Thu Nov 11 11:31:04 2021

@author: Roy Alderton

This script takes text files of tab-separated stimulus codes and stimulus
phrases and generates XML files for SpeechRecorder.

The user must specify the source text files for labials and nasals (in that 
order), the relevant language and the desired number of XML files to be 
generated.

As part of the script, two extra text files ending in 'randomised' are 
generated. These keep a record of the randomised and copied stimuli and can be 
ignored.

The script can be run from the command line in Windows as below:

  python get_xml.py [labial_text_file] [nasal_text_file] [language] [n_files]

E.g. if 3 XML files for German are desired:
    
  python get_xml.py de_labials.txt de_nasals.txt de 3

If using Linux, you may need to specify 'python3' instead of 'python'.

If attempting to run the script from the DFG-AHRC project folder, you may
not be able to navigate there properly in the command line. In this case, you
may need to copy and paste the script and the relevant stimulus files onto
your local drive.

Known issues:
    The script is not perfect at dealing with consecutive duplicates, as
    duplicate words that are members of different minimal pairs
    (e.g. p13 'lotte' and p22 'lotte') will not be treated as duplicates and
    may end up within one or two spaces of each other. I have decided that this
    is too much hassle to fix and have no plans of doing so unless the
    current situation with the scripts is deemed unsatisfactory.

'''

# import packages
import sys
import re
import random
import functools
import numpy as np

# save user-specified argments - the two text files, the language and the number of files to be produced
labial_file = sys.argv[1]
nasal_file = sys.argv[2]
language = sys.argv[3].lower()
n_files = sys.argv[4]

# specify arguments in the script for testing in an editor
# labial_file = 'english_labials_for_coding.txt'
# nasal_file = 'english_nasals_for_coding.txt'
# language = 'en'
# n_files = 3

# specify various text elements based on the language entered
if language[0] == 'e':
    language_name = 'english'
    language_code = language_name[0:2]
    labial_phrase = 'But Tessa had said “{}” pleasantly.'
    nasal_phrase = 'He’ll tell Cleo “{}” soon.'
    labial_practice_words = ['cake', 'hood']
    nasal_practice_words = ['pat', 'moat']
    instruction_text01 = 'When the traffic light goes green, please read out the sentence.\n\
        The first two sentences will be for practice.'
    instruction_text02 = 'The real sentences start now.\n\
        If you have any questions, please ask the experimenter.'
    break_text = 'Well done! Time for a quick break.'
    
elif language[0] == 'd' or language[0] == 'g':
    language_name = 'german'
    language_code = 'de'
    labial_phrase = 'Aber Elsa legt gern „{}“ beiseite.'
    nasal_phrase = 'Er las Kleo „{}“ zweimal vor.'
    labial_practice_words = ['Tier', 'locker']
    nasal_practice_words = ['lag', 'Not']
    instruction_text01 = 'Wenn die Ampel grün wird, lesen Sie den Satz vor.\n\
        Die ersten beiden Sätze sind zur Übung gedacht.'
    instruction_text02 = 'Die echten Sätze beginnen jetzt.\n\
        Wenn Sie Fragen haben, wenden Sie sich bitte an den Versuchsleiter.'
    break_text = 'Sehr gut! Es ist Zeit für eine kurze Pause.'
    
elif language[0] == 'f':
    language_name = 'french'
    language_code = language_name[0:2]
    labial_phrase = 'Mais elle déclarait « {} » par hasard.'
    nasal_phrase = 'Je dis à Cléo « {} » samedi.'
    labial_practice_words = ['lit', 'sort']
    nasal_practice_words = ['lotte', 'noix']
    instruction_text01 = "Quand le feu passe au vert, lisez la phrase.\n\
        Les deux premières phrases sont pour pratiquer."
    instruction_text02 = "Maintenant, vous allez lire les vraies phrases.\n\
        Si vous avez des questions, veuillez les poser à l’expérimentateur."
    break_text = "Très bien ! Il est temps de faire une petite pause."
    
else:
    print('No valid language specified!')
    
    
# open text file and get items
with open(labial_file, encoding = 'UTF-8') as file:
    contents = file.read()
    labial_items = re.findall(r'^.*$', contents, flags = re.MULTILINE | re.UNICODE)
    
# open text file and get items
with open(nasal_file, encoding = 'UTF-8') as file:
    contents = file.read()
    nasal_items = re.findall(r'^.*$', contents, flags = re.MULTILINE | re.UNICODE)


def make_minimal_pair_dictionary(items): 
    '''
    Create a dictionary of minimal pairs based on the pair numbers in the
    item codes, e.g. 'p01'. Used to ensure that the randomisation avoids 
    consecutive minimal pairs.

    Parameters
    ----------
    items : list
        A list of stimulus codes and carrier phrases. In practice, this is 
        each line from the input text file.

    Returns
    -------
    minimal_pair_dict : dict
        A dictionary where each key is a stimulus item and its value is the
        corresponding stimulus item that is the opposite minimal pair member.

    '''
    # make list of pair IDs from codes, e.g. 'p01'
    pair_ids = []
    for item in items:
        pair_id = re.search(r'p\d{2}', item).group()
        pair_ids.append(pair_id)
    
    # make list of lists based on pair IDs
    # each sub-list contains the two members of each minimal pair
    pair_list = []
    for pair_id in set(pair_ids):
        pair = []
        for item in items:
            if pair_id in item:
                pair.append(item)
        pair_list.append(pair)
    
    # make dictionary of minimal pair codes
    minimal_pair_dict = {}
    for pair in pair_list:
        minimal_pair_dict[pair[0]] = pair[1]
        minimal_pair_dict[pair[1]] = pair[0]
        
    return minimal_pair_dict



def copy_and_pseudo_randomise(lst, minimal_pair_dict, n_copies = 3):
    '''
    Copy and pseudo-randomise a list of stimluli creating several experimental
    blocks. The randomisation prohibits duplicate items or minimal pairs to 
    appear consecutively or two positions away from one another.

    Parameters
    ----------
    lst : list
        A list of stimulus codes and carrier phrases. In practice, this is 
        each line from the input text file.
    minimal_pair_dict : dict
        A dictionary of minimal pairs, as produced by the
        make_minimal_pair_dictionary() function.
    n_copies : int, optional
        The number of copies to make of the stimulus list. Corresponds to the
        number of blocks in the experiment. The default is 3.

    Returns
    -------
    lst_times_n : list
        A list of lists, where each sub-list is a pseudo-randomised block of
        stimulus items.

    '''
     
    # make copies of the list, specified by n_copies (default = 3); produces a list of lists    
    lst_times_n = [lst[:] for i in range(n_copies)]
    
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
        
    # return final randomised list of lists with no consecutive duplicates or minimal pairs
    return lst_times_n



def make_randomised_item_text_file(randomised_items, new_file_name, n_blocks = 3):
    '''
    Generate a new text file with all all the copied and randomised stimulus 
    items. The text file is saved with the word 'randomised' at the end and is
    only required for further processing by this script, not for anything 
    further along in the experimental pipeline.
    
    Parameters
    ----------
    randomised_items : list
        A list of lists, where each sub-list is a pseudo-randomised block of
        stimulus items, as produced by the copy_and_pseudo_randomise()
        function.
    new_file_name : str
        The file name for the new text file that is generated.
    n_blocks : int, optional
        The number of experimental blocks represented by the list of lists.
        Required so that break text is not inserted at the end of the 
        experiment. The default is 3.

    Returns
    -------
    None.

    '''
    # generate the ID numbers
    # make a list of numbers based on the total number of stimuli (list of lists)
    # https://www.kite.com/python/answers/how-to-get-the-size-of-a-list-of-lists-in-python
    id_nums = list(range(1, functools.reduce(lambda count, element: count + len(element), randomised_items, 0) + 1))
    
    # split the list of ID numbers into n equally sized sub-lists
    # this function is from numpy, so the list needs to be converted to a numpy array
    id_blocks = np.split(np.array(id_nums), n_blocks)
    
    # insert item codes for breaks in id_blocks
    id_blocks_with_breaks = np.append(id_blocks[0], 'break01')
    id_blocks_with_breaks = np.append(id_blocks_with_breaks[1], 'break02')
    
    # create a new text file with the above file name
    # then do various text processing tasks on each item in each block
    with open(new_file_name, 'w', encoding = 'UTF-8') as file:
        
        # keep track of number of blocks (repetitions)
        block_count = 0
        
        for item_block, id_block in zip(randomised_items, id_blocks):
            
            # add 1 to block_count for each block
            block_count += 1
            
            for item, id_num in zip(item_block, id_block):
                
                # replace the underscores in the carrier phrase with the word
                line = re.sub(r'_\t', f'_{block_count:01d}_{id_num:02d}\t', item)
                
                # print each line in the console and write it to the new text file
                print(line)
                file.write('%s\n' % line)
            
             # add the break items at the end of all blocks except the last one
            if block_count <= n_blocks - 1:
                 file.write('%s\n' % f'break_{block_count:02d}\t{break_text}')
                 
    # print message to signal that the function above has finished running
    print('\nCreated text files!')
    


def make_SpeechRecorder_xml(input_file_name, experiment, language_name = language_name):
    '''
    Generates an XML file for SpeechRecorder based on the copied and randomised
    list of stimuli.

    Parameters
    ----------
    input_file_name : str
        The file name for the new text file that was generated by the
        make_randomised_item_text_file() function.
    experiment : str
        'labials' or 'nasals'.
    language_name : str, optional
        DESCRIPTION. The default is language_name, as specified at the very
        start of the script.

    Returns
    -------
    None.

    '''
    
    # specify input file name based on new_file_name generated earlier
    #input_file_name = language_name + '_' + experiment + '.txt'

    # extract the pairs of item codes and sentences from the newly created code + sentence text file
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
        <section mode="autoprogress" name="stimuli" order="sequential" promptphase="idle" speakerdisplay="true">\n\n'

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
</recording>\n'

    # set ending text for the XML file
    ending = '\n\
        </section>\n\
    </recordingscript>\n\
</script>'
    
    # set output XML file name
    xml_file_name = input_file_name[:-14] + 'script.xml'
    
    # create new XML file and write each item text to it, plus opening and ending text
    # the .format parts show what will fill in the curly bracket {} slots in the text
    with open(xml_file_name, 'w', encoding = 'UTF-8') as file:
        
        # write opening text to file
        file.write(opening.format(language_name.capitalize(), experiment.capitalize()))
        
        # write instruction text and practice items to file
        file.write(break_item.format('instr01', instruction_text01))
        
        if experiment == 'labials':
            for i, word in enumerate(labial_practice_words):
                file.write(item.format(f'practice{i + 1:02d}', labial_phrase.format(word)))
        else:
            for i, word in enumerate(nasal_practice_words):
                file.write(item.format(f'practice{i + 1:02d}', nasal_phrase.format(word))) 
        
        file.write(break_item.format('instr02', instruction_text02))
        
        # write item text to file, with break variant as needed
        for text_pair in text_pairs:
            if 'break' in text_pair[0]:
                file.write(break_item.format(text_pair[0], text_pair[1]))
            else:
                file.write(item.format(text_pair[0], text_pair[1]))
                
        # write ending text to file    
        file.write(ending)


# apply make_minimal_pair_dictionary function to items
labial_minimal_pair_dict = make_minimal_pair_dictionary(labial_items)
nasal_minimal_pair_dict = make_minimal_pair_dictionary(nasal_items)

# randomise items and create files according to the number of runs specified in n_files
for i in range(0, int(n_files)):

    # apply the copy_and_pseudo_randomise function to the stimulus words
    randomised_labial_items = copy_and_pseudo_randomise(labial_items, labial_minimal_pair_dict, n_copies = 3)
    randomised_nasal_items = copy_and_pseudo_randomise(nasal_items, nasal_minimal_pair_dict, n_copies = 3)
    
    
    # generate the file names for the new text files based on the language and the experiment    
    new_labial_file_name = '{}_'.format(f'{i + 1:02d}') + language_code + '_labials_randomised.txt'
    new_nasal_file_name = '{}_'.format(f'{i + 1:02d}') + language_code + '_nasals_randomised.txt'
    
    
    # apply make_randomised_item_text_file function to randomised items and new file names
    make_randomised_item_text_file(randomised_labial_items, new_labial_file_name)
    make_randomised_item_text_file(randomised_nasal_items, new_nasal_file_name)
    
    
    # apply the make_SpeechRecorder_xml function to the labial and nasal stimulus codes and sentences 
    make_SpeechRecorder_xml(new_labial_file_name, 'labials')
    make_SpeechRecorder_xml(new_nasal_file_name, 'nasals')

# print message to signal that the script has finished running
print('\nCreated XML files!')

             












