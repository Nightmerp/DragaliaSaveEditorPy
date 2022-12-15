# dragalia_save_editor_interface.py

import file_handling
import json_handling
import time
import sys

ELEMENT = {'FLAME': 1, 'WATER': 2, 'WIND': 3, 'LIGHT': 4, 'SHADOW': 5}
WEAPON = {'SWORD': 1, 'BLADE': 2, 'DAGGER': 3, 'AXE': 4, 'LANCE': 5,
          'BOW': 6, 'WAND': 7, 'STAFF': 8, 'MANACASTER': 9, 'GUN': 9}
ELEMENT_INVERSE = {'1': 'Flame', '2': 'Water', '3': 'Wind', '4': 'Light', '5': 'Shadow'}
WEAPON_INVERSE = {'1': 'Sword', '2': 'Blade', '3': 'Dagger', '4': 'Axe', '5': 'Lance',
                  '6': 'Bow', '7': 'Wand', '8': 'Staff', '9': 'Manacaster'}

def _is_int(string: str) -> bool:
    try:
        int(string.strip())
        return True
    except ValueError:
        return False

def _return_if_exists(field: str, data: dict) -> int:
    if field in data:
        return data[field]
    return 0

def _pretty_print(num: int) -> str:
    output = str(num)
    length = len(output)
    
    for i in range(length - 1, 0, -1):
        if (length - i) % 3 == 0:
            output = output[:i] + ',' + output[i:]
            
    return output

def _box_print(lines: list) -> None:
    max_len = 0
    
    for line in lines:
        if len(line) > max_len:
            max_len = len(line)
            
    max_len += 2
    if max_len > 60:
        max_len = 60
    
    print('+' + '-' * max_len + '+')
    for line in lines:
        print(' ' + line)
    print('+' + '-' * max_len + '+')

def _ask_y_n_question(question: str) -> bool:
    print(f'{question} (Y/N)')
    
    while True:
        user_input = input().upper()
        
        if user_input == 'Y' or user_input == 'YES':
            return True
        elif user_input == 'N' or user_input == 'NO':
            return False
        
        print('Invalid response, please try again.')

def _ask_int_question(question: str) -> int:
    print(question)
    
    while not _is_int(output := input().strip()):
        print('Invalid response, please try again.')

    return int(output)

def _print_mc_question(options: list[str],
                       prompt: str = 'What would you like to do?') -> None:
    print(prompt)
    index = 1

    for option in options:
        print(f'[{index}] {option}')
        index += 1

def _restructure_id(char_id: int) -> int:
    # because i don't like how the save file sorts adventurers
    char_id = str(char_id)
    output = char_id[5] + char_id[2] + str(5 - int(char_id[3])) + char_id[6:]
    return output

def _proper(string: str) -> str:
    split_string = string.split(' ')

    for i in range(len(split_string)):
        if '!' in split_string[i]:
            halves = split_string[i].split('!')
            halves[0] = halves[0].upper()
            halves[1] = halves[1].capitalize()
            split_string[i] = '!'.join(halves)
        else:
            split_string[i] = split_string[i].capitalize()

    output = ' '.join(split_string)
    return output

class DragaliaSaveEditorInterface:
    def __init__(self):
        self._save_file = None
        self._backup = None
        self._json = None
        self._running = True
        self._char_elem_filter = set()
        self._char_weapon_filter = set()

    def _welcome_banner(self) -> None:
        print('-' * 40)
        print('  Welcome to the Dragalia Save Editor!  ')
        print('-' * 40)
        print()
    
    def _set_save_file(self) -> None:
        self._save_file = None
        
        while self._save_file == None:
            file = None
            print('Please input the directory path for your save file.')

            while (file := file_handling.find_file(input())) == None:
                print('Could not find a file at that location, please try again.')

            response = _ask_y_n_question(
                f'Is your save file named {file_handling.get_file_name(file)} \
inside the directory {file_handling.get_parent_directory(file)}?')

            if response:
                self._set_save_file_to(file)

    def _set_save_file_to(self, file: 'File path') -> None:
        self._save_file = file
        print(f'Save file set to {file}.')

    def _ask_create_backup(self) -> None:
        backup = file_handling.get_parent_directory(self._save_file)/'backup.txt'
        print('***It is highly recommended to have a backup file saved in case \
something goes wrong.***')

        if file_handling.find_file(backup) == None:
            question = f'No backup file detected within this directory. Would \
you like to create one?'
        else:
            question = 'A file named backup.txt has been detected within this \
directory. Would you still like to create a backup file?'

        response = _ask_y_n_question(question)

        if response:
            self._backup = backup
            self._ask_overwrite()
        else:
            print('No backup file was created.')

    def _ask_overwrite(self) -> None:
        if file_handling.find_file(self._backup) == None:
            self._create_backup_file()
        else:
            response = _ask_y_n_question(
                f'Would you like to overwrite the file at {self._backup}?')

            if response:
                self._create_backup_file()
            else:
                response = _ask_y_n_question(
                    'Then would you like to specify another name/location?')

                if response:
                    self._set_backup_name()
                else:
                    self._ask_quit_creating_backup(self._ask_overwrite)

    def _set_backup_name(self) -> None:
        backup_directory = None
        backup_name = None
        print(f'Specify a directory for the backup file to be created in. If \
this is left blank, the backup directory will default to what it is set to \
currently, at {file_handling.get_parent_directory(self._backup)}.')
        
        while backup_directory == None:
            directory = input()
            if directory.strip() == '':
                backup_directory = file_handling.get_parent_directory(self._backup)
                continue
            backup_directory = file_handling.find_directory(directory)

            if backup_directory == None:
                print('Directory not found, please try again.')

        print(f'Specify a name for the backup file. If this is left blank, the \
name of the backup file will default to what it is set to currently, \
{file_handling.get_file_name(self._backup)}.')
        
        file = input()
        if file.strip() == '':
            backup_name = file_handling.get_file_name(self._backup)
        else:
            backup_name = file
            
        self._backup = backup_directory / backup_name
        warning = ''
        
        if len(self._backup.suffixes) == 0:
            self._backup = backup_directory / f'{backup_name}.txt'
        else:
            if not len(self._backup.suffixes) == 1 or not self._backup.suffix == '.txt':
                warning = f'***WARNING***\n{backup_name} does not appear to \
be a txt file, which may cause the file to be corrupted/unreadable.\n'

        response = _ask_y_n_question(f'{warning}Create backup file at {self._backup}?')

        if response:
            self._ask_overwrite()
        else:
            self._ask_quit_creating_backup(self._set_backup_name)

    def _ask_quit_creating_backup(self, func: 'Function') -> None:
        response = _ask_y_n_question('Quit creating backup file?')

        if response:
            print('No backup file was created.')
            self._backup = None
        else:
            func()

    def _create_backup_file(self) -> None:
        try:
            file_handling.copy_file(self._save_file, self._backup)
            print(f'Created backup file at {self._backup}.')
        except file_handling.CopyFileError:
            response = _ask_y_n_question(f'Failed to create backup file at \
{self._backup}. Would you like to specify another location and try again?')

            if response:
                self._set_backup_file()
            else:
                self._ask_quit_creating_backup(self._set_backup_name)

    def _load_json(self) -> None:
        try:
            self._json = json_handling.DragaliaSaveFile(self._save_file)
        except json_handling.ResourceConversionError:
            print('Unable to load resources. Please make sure you have downloaded \
all corresponding files for this program.')
            sys.exit()
        except json_handling.FileConversionError:
            print('The given file was unable to be loaded as a JSON object. \
Please make sure that the file is your Dragalia save file.')
            print(f'File location: {self._save_file}')
            sys.exit()
        except json_handling.UserDataNotFoundError:
            print('Unable to retrieve user data from save file. Please make \
sure that the given file is your Dragalia save file.')
            sys.exit()
        except json_handling.CharactersNotFoundError:
            print('Unable to retrieve character data from save file. Please \
make sure that the given file is your Dragalia save file.')
            sys.exit()
        except json_handling.EncyclopediaBonusesNotFoundError:
            print('Unable to retrieve encyclopedia bonuses from save file. \
Please make sure that the given file is your Dragalia save file.')
            sys.exit()
        except json_handling.UnitStoryListNotFoundError:
            print('Unable to retrieve story list from save file. \
Please make sure that the given file is your Dragalia save file.')
            sys.exit()

    def _main_menu(self) -> None:
        options = [
            'User Profile',
            'Characters',
            'Dragons',
            'Wyrmprints',
            'Weapons',
            'Quit Editor']

        _print_mc_question(options, 'Please select one of the following.')

        while True:
            selection = input().strip().upper()

            match selection:
                case '1' | 'USER PROFILE' | 'PROFILE' | 'USER':
                    while self._user_profile():
                        continue
                    return

                case '2' | 'CHARACTERS' | 'ADVENTURERS' | 'CHARACTER' | 'CHARS' | 'ADVS':
                    while self._characters():
                        continue
                    return

                case '3' | 'DRAGONS' | 'DRAGON':
                    print('Not implemented yet')
                    return

                case '4' | 'WYRMPRINTS' | 'WYRMPRINT' | 'PRINTS' | 'PRINT' | 'WPS' | 'WP':
                    print('Not implemented yet')
                    return

                case '5' | 'WEAPONS' | 'WEAPON':
                    print('Not implemented yet')
                    return

                case '6' | 'QUIT EDITOR' | 'QUIT' | 'Q' | 'EXIT':
                    self._ask_quit_editor()
                    return

                case _:
                    print('Invalid input, please try again.')

    def _user_profile(self) -> bool:
        self._display_user_data()
        options = [
            'Modify Data',
            'Back']

        _print_mc_question(options)

        while True:
            selection = input().strip().upper()

            match selection:
                case '1' | 'MODIFY DATA' | 'MODIFY':
                    self._modify_user_data()
                    return True

                case '2' | 'BACK' | 'B' | 'QUIT' | 'Q' | 'EXIT':
                    return False

                case _:
                    print('Invalid input, please try again.')

    def _display_user_data(self) -> None:
        output = []
        user_data = self._json.get_user_data()
        epithets = self._json.epithet_data

        if str(user_data['emblem_id']) in epithets:
            epithet = epithets[str(user_data['emblem_id'])]
        else:
            epithet = 'None'
        
        output.append(f'Player Name: {user_data["name"]}')
        output.append(f'Epithet: {epithet}')
        output.append(f'User ID: {user_data["viewer_id"]}')
        output.append(f'Player Level: {_return_if_exists("level", user_data)}')
        output.append('')
        output.append(f'Wyrmite: {_pretty_print(_return_if_exists("crystal", user_data))}')
        output.append(f'Rupies: {_pretty_print(_return_if_exists("coin", user_data))}')
        output.append(f'Mana: {_pretty_print(_return_if_exists("mana_point", user_data))}')
        output.append(f'Eldwater: {_pretty_print(_return_if_exists("dew_point", user_data))}')

        _box_print(output)

    def _modify_user_data(self) -> None:
        options = [
            'Player Name',
            'Epithet',
            'Wyrmite',
            'Rupies',
            'Mana',
            'Eldwater',
            'Back']

        _print_mc_question(options, 'What would you like to change?')

        while True:
            selection = input().strip().upper()
            
            match selection:
                case '1' | 'PLAYER NAME' | 'NAME' | 'PLAYER':
                    print('What would you like to change your account name to?')

                    while (new_name := input()) == '':
                        print('Invalid name, please try again.')

                    self._json.modify_user_data('name', new_name)
                    print(f'Changed name to {new_name}.')
                    return

                case '2' | 'EPITHET' | 'EMBLEM':
                    print('What would you like to change your epithet to?')
                    print('Please make sure your spelling is exact.')

                    epithets = self._json.epithet_data

                    while _proper(new_epithet := input().strip()) not in epithets:
                        print(f'Could not find {new_epithet} in the list of epithets in game. Please try again.')

                    if _is_int(new_epithet):
                        new_epithet_id = int(new_epithet)
                    else:
                        new_epithet_id = int(epithets[_proper(new_epithet)])
                    
                    self._json.modify_user_data('emblem_id', new_epithet_id)
                    print(f'Changed epithet to {epithets[str(new_epithet_id)]}.')
                    return

                case '3' | 'WYRMITE' | 'CRYSTAL' | 'CRYSTALS':
                    print('What would you like to set your wyrmite stash to?')
                    print('(cannot exceed 32 bit integer limit)')

                    while _is_int(new_value := input()) == False or int(new_value) < 0:
                        print('Invalid value, please try again.')

                    new_value = int(new_value)
                    if new_value > 2147483647:
                        new_value = 2147483647

                    self._json.modify_user_data('crystal', new_value)
                    print(f'Set wyrmite stash to {_pretty_print(str(new_value))}.')
                    return

                case '4' | 'RUPIES' | 'COIN' | 'COINS':
                    print('What would you like to set your rupie count to?')

                    while _is_int(new_value := input()) == False or int(new_value) < 0:
                        print('Invalid value, please try again.')

                    self._json.modify_user_data('coin', int(new_value))
                    print(f'Set rupie count to {_pretty_print(new_value)}.')
                    return

                case '5' | 'MANA':
                    print('What would you like to set your mana count to?')
                    print('***WARNING*** setting this higher than the 32 bit \
integer limit will break your save file!')

                    while _is_int(new_value := input()) == False or int(new_value) < 0:
                        print('Invalid value, please try again.')

                    new_value = int(new_value)
                    if new_value > 2147483647:
                        new_value = 2147483647

                    self._json.modify_user_data('mana_point', int(new_value))
                    print(f'Set mana count to {_pretty_print(new_value)}.')
                    return

                case '6' | 'ELDWATER' | 'WATER':
                    print('What would you like to set your eldwater count to?')
                    print('***WARNING*** setting this higher than the 32 bit \
integer limit will break your save file!')

                    while _is_int(new_value := input()) == False or int(new_value) < 0:
                        print('Invalid value, please try again.')

                    new_value = int(new_value)
                    if new_value > 2147483647:
                        new_value = 2147483647

                    self._json.modify_user_data('dew_point', int(new_value))
                    print(f'Set eldwater count to {_pretty_print(new_value)}.')
                    return

                case '7' | 'BACK' | 'B' | 'QUIT' | 'Q' | 'EXIT':
                    return

                case _:
                    print('Invalid response, please try again.')

    def _characters(self) -> bool:
        print(f'You currently have {len(self._json.get_character_data())} \
characters in your collection.')

        options = [
            'View Characters',
            'Add/Max Out Character',
            'Add All Missing Characters (from original game)(comes with max stats)',
            'Max Out All Current Characters (from original game)',
            'Max Out Account (adds and maxes out all characters from original game)',
            'Back']

        _print_mc_question(options)

        while True:
            selection = input().strip().upper()

            match selection:
                case '1' | 'VIEW CHARACTERS' | 'VIEW CHARAS' | 'VIEW CHAR' | 'VIEW':
                    self._view_characters()
                    return True

                case '2' | 'ADD/MAX OUT CHARACTER' | 'ADD CHARACTER' | 'MAX OUT CHARACTER' | 'MAX CHARACTER' | 'ADD ONE' | 'MAX OUT ONE' | 'ADD SINGLE' | 'MAX OUT SINGLE' | 'MAX ONE' | 'MAX SINGLE':
                    self._add_character_prompt()
                    return True

                case '3' | 'ADD ALL MISSING CHARACTERS' | 'ADD ALL MISSING CHARACTER' | 'ADD ALL':
                    self._add_missing_characters()
                    return True

                case '4' | 'MAX OUT ALL CURRENT CHARACTERS' | 'MAX OUT CURRENT' | 'MAX ALL CURRENT' | 'MAX CURRENT CHARACTERS' | 'MAX OUT ALL CURRENT' | 'MAX OUT CURRENT CHARACTERS':
                    self._max_current_characters()
                    return True

                case '5' | 'MAX OUT ACCOUNT' | 'MAX ACCOUNT':
                    self._max_character_list()
                    return True

                case '6' | 'BACK' | 'B' | 'QUIT' | 'Q' | 'EXIT':
                    return False

                case _:
                    print('Invalid response, please try again.')

    def _view_characters(self) -> None:
        if len(self._char_elem_filter) == 0 and len(self._char_weapon_filter) == 0:
            response = _ask_y_n_question('No filter detected, would you like \
to set one?')

            if response:
                self._set_character_filter()
        else:
            elem_filter = str(self._char_elem_filter)[1:-1] if len(self._char_elem_filter) != 0 else 'N/A'
            weapon_filter = str(self._char_weapon_filter)[1:-1] if len(self._char_weapon_filter) != 0 else 'N/A'
            print('Current filter settings:')
            print(f'Elements: {elem_filter}')
            print(f'Weapons: {weapon_filter}')
            response = _ask_y_n_question('Would you like to change these settings?')

            if response:
                self._set_character_filter()

        characters = self._json.get_character_data()
        all_characters = self._json.all_character_data
        characters = sorted(characters, key = lambda char: int(_restructure_id(char['chara_id'])))

        for char in characters:
            if (len(self._char_elem_filter) == 0 or (str(char['chara_id'])[5] in ELEMENT_INVERSE and ELEMENT_INVERSE[str(char['chara_id'])[5]].upper() in self._char_elem_filter)) and (len(self._char_weapon_filter) == 0 or (str(char['chara_id'])[2] in WEAPON_INVERSE and WEAPON_INVERSE[str(char['chara_id'])[2]].upper() in self._char_weapon_filter)):
                if str(char['chara_id']) in all_characters:
                    name = all_characters[str(char['chara_id'])]['FullName']
                else:
                    name = 'Unknown'
                rarity = str(char['chara_id'])[3]
                
                try:
                    element = ELEMENT_INVERSE[str(char['chara_id'])[5]]
                except KeyError:
                    element = 'Unknown'

                try:
                    weapon = WEAPON_INVERSE[str(char['chara_id'])[2]]
                except KeyError:
                    weapon = 'Unknown'
                    
                level = char['level']
                mc = len(char['mana_circle_piece_id_list'])
                augments = char['hp_plus_count'] + char['attack_plus_count']
                gettime = time.strftime('%A, %B %d, %Y at %H:%M:%S',
                                        time.localtime(char['gettime']))
                print(f'{name} ({rarity}* {element}/{weapon})')
                print(f'Level {level} | {mc} MC | +{augments}')
                print(f'Obtained on {gettime}.')
                print()

    def _set_character_filter(self) -> None:
        self._char_elem_filter = set()
        self._char_weapon_filter = set()
        
        print('Enter a comma separated list of elements you would like to \
filter for out of flame, water, wind, light, and shadow. Ex. flame, water \
would filter for those two elements. Entering nothing means all elements will \
be considered.')
        line = input()
        elements = line.split(',')

        if line.strip() == '':
            self._char_elem_filter = set()
        else:
            for elem in elements:
                if elem.strip().upper() in ELEMENT:
                    self._char_elem_filter.add(elem.strip().upper())
                else:
                    print(f'Ignored {elem}; not viable option.')

        if len(self._char_elem_filter) == 5:
            self._char_elem_filter = set()

        print('Enter a comma separated list of weapons you would like to \
filter for out of sword, blade, dagger, axe, lance, bow, wand, staff, and \
manacaster. Entering nothing means all weapons will be considered.')
        line = input()
        weapons = line.split(',')

        if line.strip() == '':
            self._char_weapon_filter = set()
        else:
            for weapon in weapons:
                if weapon.strip().upper() in WEAPON:
                    if weapon.strip().upper() == 'GUN':
                        self._char_weapon_filter.add('MANACASTER')
                    else:
                        self._char_weapon_filter.add(weapon.strip().upper())
                else:
                    print(f'Ignored {weapon}; not viable option.')

        if len(self._char_weapon_filter) == 9:
            self._char_weapon_filter = set()

    def _add_character_prompt(self) -> None:
        print('If the character you specify already exists in your account, \
their stats will be maxed out.')
        response = _ask_y_n_question('Is the character you want to add from the base game?')

        if response:
            self._add_character(True)
        else:
            self._add_character(False)
    
    def _add_character(self, is_char: bool) -> None:
        if is_char:
            print('Which character would you like to add?')

            while ((char := _proper(input().strip())) not in self._json.all_character_names) and (not _is_int(char) or char not in self._json.all_character_data):
                print(f'Could not find {char}, please try again.')

            if _is_int(char):
                char_name = self._json.all_character_data[char]['FullName']
                added_char = self._json.add_char(int(char))
            else:
                char_name = self._json.all_character_data[str(self._json.all_character_names[char])]['FullName']
                added_char = self._json.add_char(self._json.all_character_names[char])

            action = 'Added' if added_char else 'Maxed out'
            print(f'{action} the character {char_name}.')
        else:
            char_id = _ask_int_question("What is the character's id number?")
            has_spiral = _ask_y_n_question('Does the character have a spiral?')

            has_ss = _ask_y_n_question("Can the character's shared skill be shared?")
            if has_ss:
                ss_cost = _ask_int_question('How much does their shared skill cost?')
            else:
                ss_cost = 0
                
            max_hp = _ask_int_question('What is their max HP?')
            max_atk = _ask_int_question('What is their max attack?')

            stories = None
            has_stories = _ask_y_n_question('Does the character have any unit stories?')
            if has_stories:
                print('Please input their corresponding story IDs in a comma separated list.')

                while True:
                    stories = input().split(',')
                    are_ints = True

                    for i in range(len(stories)):
                        if not _is_int(stories[i]):
                            are_ints = False
                            break
                        else:
                            stories[i] = int(stories[i])

                    if are_ints:
                        break
                    else:
                        print('Invalid response, please try again.')

            added_char = self._json.add_char(char_id, has_spiral, ss_cost, max_hp, max_atk, stories)
            action = 'Added' if added_char else 'Maxed out'
            print(f'{action} character with id {char_id}.')

    def _add_missing_characters(self) -> None:
        num_added = self._json.add_all_missing_chars()
        print(f'Added {num_added} characters.')

    def _max_current_characters(self) -> None:
        self._json.max_all_current_chars()
        print('Maxed out current character roster.')

    def _max_character_list(self) -> None:
        self._json.max_out_character_list()
        print('Maxed out all characters.')
            
    def _ask_quit_editor(self) -> None:
        response = _ask_y_n_question('Are you sure you want to quit?')
        if response:
            print('Goodbye!')
            sys.exit()
    
    def run(self) -> None:
        self._welcome_banner()
        self._set_save_file()
        self._ask_create_backup()
        self._load_json()
        while self._running:
            self._main_menu()

if __name__ == '__main__':
    DragaliaSaveEditorInterface().run()
