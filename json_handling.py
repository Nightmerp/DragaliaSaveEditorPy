# json_handling.py

import json
import time
import math

class FileConversionError(Exception):
    pass

class ResourceConversionError(Exception):
    pass

class FileEncodingError(Exception):
    pass

class UserDataNotFoundError(Exception):
    pass

class CharactersNotFoundError(Exception):
    pass

class EncyclopediaBonusesNotFoundError(Exception):
    pass

class UnitStoryListNotFoundError(Exception):
    pass

def _is_int(string: str) -> bool:
    try:
        int(string)
        return True
    except ValueError:
        return False

class DragaliaSaveFile:
    def __init__(self, file_path: 'File path'):
        self._file = file_path
        self.all_character_data = None
        self.all_character_names = None
        self.epithet_data = None
        self.story_data = None
        
        self._data = None
        self._user_data = None
        self._summon_tickets = None
        self._character_data = None
        self._adv_encyclo = None
        self._dragon_encyclo = None
        self._stories = None

        self._initialize_all_character_data()
        self._initialize_all_character_names()
        self._initialize_epithet_data()
        self._initialize_story_data()
        
        self._initialize_data()
        self._initialize_user_data()
        self._initialize_summon_tickets()
        self._initialize_character_data()
        self._initialize_encyclo_bonuses()
        self._initialize_stories()

    def _initialize_all_character_data(self) -> None:
        file = open('data/adventurers.txt')
        try:
            self.all_character_data = json.load(file)
        except:
            raise ResourceConversionError
        finally:
            file.close()

    def _initialize_all_character_names(self) -> None:
        file = open('data/adventurer_aliases.txt')
        try:
            self.all_character_names = json.load(file)
        except:
            raise ResourceConversionError
        finally:
            file.close()

    def _initialize_epithet_data(self) -> None:
        file = open('data/epithets.txt')
        try:
            self.epithet_data = json.load(file)
        except:
            raise ResourceConversionError
        finally:
            file.close()

    def _initialize_story_data(self) -> None:
        file = open('data/stories.txt')
        try:
            self.story_data = json.load(file)
        except:
            raise ResourceConversionError
        finally:
            file.close()

    def _initialize_data(self) -> None:
        file = open(self._file)
        try:
            self._data = json.load(file)
        except:
            raise FileConversionError
        finally:
            file.close()

    def _initialize_user_data(self) -> None:
        try:
            self._user_data = self._data['data']['user_data']
        except KeyError:
            raise UserDataNotFoundError

    def _initialize_summon_tickets(self) -> None:
        self._summon_tickets = -1

    def _initialize_character_data(self) -> None:
        try:
            self._character_data = self._data['data']['chara_list']
        except:
            raise CharactersNotFoundError

    def _initialize_encyclo_bonuses(self) -> None:
        try:
            self._adv_encyclo = self._data['data']['fort_bonus_list']['chara_bonus_by_album']
            self._dragon_encyclo = self._data['data']['fort_bonus_list']['dragon_bonus_by_album']
        except:
            raise EncyclopediaBonusesNotFoundError

    def _initialize_stories(self) -> None:
        try:
            self._stories = self._data['data']['unit_story_list']
        except:
            raise UnitStoryListNotFoundError

    def get_user_data(self) -> dict:
        return self._user_data.copy()

    def get_character_data(self) -> list:
        return self._character_data[:]

    def modify_user_data(self, field: str, new_value: int | str) -> None:
        self._user_data[field] = new_value
        self._update()

    def add_char(self, char_id: int, has_spiral: bool = False,
                 shared_skill_cost: int = 0, max_hp: int = 0, max_atk: int = 0,
                 stories: list[int] = None, gettime: int = None,
                 group: bool = False) -> bool:
        char_exists = False
        index = -1
        for i in range(len(self._character_data)):
            if char_id == self._character_data[i]['chara_id']:
                char_exists = True
                index = i
                break

        if char_exists:
            gettime = self._character_data[index]['gettime']
            og_level = self._character_data[index]['level']
            og_mc = len(self._character_data[index]['mana_circle_piece_id_list'])

            self._character_data[index] = self._create_max_character(char_id, gettime = gettime)

            element = int(str(char_id)[5])
            has_spiral = self._character_data[i]['level'] == 100

            if self._character_data[i]['level'] != og_level:
                    if og_level < 80:
                        if has_spiral:
                            self._add_adv_encyclo_bonus(element, hp = 0.2)
                        else:
                            self._add_adv_encyclo_bonus(element, hp = 0.1)
                    else:
                        self._add_adv_encyclo_bonus(element, hp = 0.1)

            if len(self._character_data[i]['mana_circle_piece_id_list']) != og_mc:
                    if og_mc < 50:
                        if has_spiral:
                            self._add_adv_encyclo_bonus(element, atk = 0.2)
                        else:
                            self._add_adv_encyclo_bonus(element, atk = 0.1)
                    else:
                        self._add_adv_encyclo_bonus(element, atk = 0.1)
            
            output = False
        else:
            self._character_data.append(self._create_max_character(char_id, has_spiral, shared_skill_cost, max_hp, max_atk, stories, gettime))
            element = int(str(char_id)[5])
            has_spiral = self._character_data[-1]['level'] == 100

            if has_spiral:
                self._add_adv_encyclo_bonus(element, 0.3, 0.3)
            else:
                self._add_adv_encyclo_bonus(element, 0.2, 0.2)

            output = True
            
        if not group:
            self._update()

        return output

    def add_all_missing_chars(self) -> int:
        current_chars = set()
        count = 0
        
        for existing_char in self._character_data:
            current_chars.add(existing_char['chara_id'])

        for char_id in self.all_character_data:
            if int(char_id) not in current_chars and char_id != "19900004":
                self.add_char(int(char_id), group = True)
                count += 1

        self._update()
        return count

    def max_all_current_chars(self) -> None:
        for i in range(len(self._character_data)):
            char_id = self._character_data[i]['chara_id']
            
            if str(char_id) in self.all_character_data:
                gettime = self._character_data[i]['gettime']
                self.add_char(char_id, gettime = gettime, group = True)

        self._update()

    def max_out_character_list(self) -> None:
        self.max_all_current_chars()
        self.add_all_missing_chars()

    def _create_max_character(self, char_id: int, has_spiral: bool = False,
                              shared_skill_cost: int = 0, max_hp: int = 0,
                              max_atk: int = 0, stories: list[int] = None,
                              gettime: int = None) -> 'Character':
        if str(char_id) in self.all_character_data:
            char_data = self.all_character_data[str(char_id)].copy()
            has_spiral = 'ManaSpiralDate' in char_data
            shared_skill_cost = char_data['EditSkillCost']
            
            if has_spiral:
                max_hp = char_data['AddMaxHp1'] + char_data['PlusHp0'] + char_data['PlusHp1'] + char_data['PlusHp2'] + char_data['PlusHp3'] + char_data['PlusHp4'] + char_data['PlusHp5'] + char_data['McFullBonusHp5']
                max_atk = char_data['AddMaxAtk1'] + char_data['PlusAtk0'] + char_data['PlusAtk1'] + char_data['PlusAtk2'] + char_data['PlusAtk3'] + char_data['PlusAtk4'] + char_data['PlusAtk5'] + char_data['McFullBonusAtk5']
            else:
                max_hp = char_data['MaxHp'] + char_data['PlusHp0'] + char_data['PlusHp1'] + char_data['PlusHp2'] + char_data['PlusHp3'] + char_data['PlusHp4'] + char_data['McFullBonusHp5']
                max_atk = char_data['MaxAtk'] + char_data['PlusAtk0'] + char_data['PlusAtk1'] + char_data['PlusAtk2'] + char_data['PlusAtk3'] + char_data['PlusAtk4'] + char_data['McFullBonusAtk5']

        mc_list = []
        mc_level = 70 if has_spiral else 50

        for i in range(1, mc_level + 1):
            mc_list.append(i)

        new_char = dict()
        new_char['chara_id'] = char_id
        new_char['rarity'] = 5
        new_char['exp'] = 8866950 if has_spiral else 1191950
        new_char['level'] = 100 if has_spiral else 80
        new_char['additional_max_level'] = 20 if has_spiral else 0
        new_char['hp_plus_count'] = 100
        new_char['attack_plus_count'] = 100
        new_char['limit_break_count'] = 5 if has_spiral else 4
        new_char['is_new'] = 1
        new_char['gettime'] = gettime if gettime != None else int(time.time())
        new_char['skill_1_level'] = 4 if has_spiral else 3
        new_char['skill_2_level'] = 3 if has_spiral else 2
        new_char['ability_1_level'] = 3 if has_spiral else 2
        new_char['ability_2_level'] = 3 if has_spiral else 2
        new_char['ability_3_level'] = 2
        new_char['burst_attack_level'] = 2
        new_char['combo_buildup_count'] = 1 if has_spiral else 0
        new_char['hp'] = max_hp
        new_char['attack'] = max_atk
        new_char['ex_ability_level'] = 5
        new_char['ex_ability_2_level'] = 5
        new_char['is_temporary'] = 0
        new_char['is_unlock_edit_skill'] = shared_skill_cost
        new_char['mana_circle_piece_id_list'] = mc_list
        new_char['list_view_flag'] = 1

        self._add_stories(char_id, stories)
        
        return new_char

    def _add_adv_encyclo_bonus(self, elem: int, hp: float = 0,
                               atk: float = 0) -> None:
        if 1 <= elem <= 5:
            self._adv_encyclo[elem - 1]['hp'] = math.fsum(self._adv_encyclo[elem - 1]['hp'], hp)
            self._adv_encyclo[elem - 1]['attack'] = math.fsum(self._adv_encyclo[elem - 1]['attack'], atk)

    def _add_dragon_encyclo_bonus(self, elem: int, hp: float = 0,
                                  atk: float = 0) -> None:
        if 1 <= elem <= 5: 
            self._dragon_encyclo[elem - 1]['hp'] = math.fsum(self._dragon_encyclo[elem - 1]['hp'], hp)
            self._dragon_encyclo[elem - 1]['attack'] = math.fsum(self._dragon_encyclo[elem - 1]['attack'], atk)
        
    def _add_stories(self, char_id: int, stories: list[int] = None) -> None:
        current_stories = set()

        for story in self._stories:
            current_stories.add(story['unit_story_id'])

        if stories == None:
            if str(char_id) in self.story_data:
                for story in self.story_data[str(char_id)]:
                    if int(story) not in current_stories:
                        self._add_story(int(story))
        else:
            for story in stories:
                if story not in current_stories:
                    self._add_story(story)

    def _add_story(self, story_id: int, is_read: int = 0) -> None:
        self._stories.append({'unit_story_id': story_id, 'is_read': is_read})

    def _update(self) -> None:
        file = open(self._file, 'w')
        try:
            json.dump(self._data, file, indent = 2)
        except:
            raise FileEncodingError
        finally:
            file.close()
