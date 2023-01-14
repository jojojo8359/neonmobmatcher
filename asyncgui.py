#!/usr/bin/python3

# ****************************************************************************
# NeonMob Trade Matcher Tool
# Version: 1.1.0
# ****************************************************************************
# Copyright (c) 2022 Joel Keaton
# All rights reserved.
# ****************************************************************************


# Builtins
import hashlib
import os
import sys
import threading
import traceback
import json
from json import JSONDecodeError
from os import path
import time
import webbrowser
import re
from typing import *

# pip packages
import PySimpleGUI as sg
import requests

import gifs

sg.theme('DarkGrey9')

get_types = Union[str, int]

DB_MD5_URL = "https://raw.githubusercontent.com/jojojo8359/neonmob-set-db/main/all-sets.md5"
DB_JSON_URL = "https://raw.githubusercontent.com/jojojo8359/neonmob-set-db/main/all-sets.json"

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})


def get_json(url):
    """Uses requests to get json data from a specific url

    :param str url: The url to get json data from
    :returns: json data if successfully fetched, -1 otherwise
    """
    try:
        # r = requests.request('GET', url)
        r = SESSION.get(url)
        r.raise_for_status()
        json_data = r.json()
        return json_data
    except requests.exceptions.ConnectionError as e:
        print('Network problem has occurred.', e)
        return -1
    except requests.exceptions.HTTPError as e:
        print('An HTTP error has occurred.', e)
        return -1
    except requests.exceptions.Timeout as e:
        print('Request timed out.', e)
        return -1
    except requests.exceptions.TooManyRedirects as e:
        print('Request redirected too many times.', e)
        return -1
    except requests.exceptions.RequestException as e:
        print('Other request error has occurred.', e)
        return -1


def get_text(url):
    """

    :param url: The url to get text from
    :type url: str
    :return: text if successfully fetched, -1 otherwise
    :rtype:
    """
    try:
        # r = requests.request('GET', url)
        r = SESSION.get(url)
        r.raise_for_status()
        text_data = r.text
        return text_data
    except requests.exceptions.ConnectionError as e:
        print('Network problem has occurred.', e)
        return -1
    except requests.exceptions.HTTPError as e:
        print('An HTTP error has occurred.', e)
        return -1
    except requests.exceptions.Timeout as e:
        print('Request timed out.', e)
        return -1
    except requests.exceptions.TooManyRedirects as e:
        print('Request redirected too many times.', e)
        return -1
    except requests.exceptions.RequestException as e:
        print('Other request error has occurred.', e)
        return -1


def get_db_md5():
    md5 = get_text(DB_MD5_URL)
    if md5 == -1:
        print('An error occurred while downloading the md5 hash.')
    return md5.split('  ')[0]


def download_db():
    db = get_json(DB_JSON_URL)
    if db == -1:
        print('An error occurred while downloading the database.')
    else:
        with open('db.json', 'w') as f:  # TODO: pass in custom db location
            json.dump(db, f)


def verify_db_md5(github_md5):
    try:
        with open('db.json', 'rb') as f:
            data = f.read()
            local_md5 = hashlib.md5(data).hexdigest()
    except OSError:  # TODO: Include some kind of output when error occurs
        with open('db.json', 'w') as f:
            f.write("[]")
        return False
    return github_md5 == local_md5


def db_attempt_update(show_status=True):
    if not verify_db_md5(get_db_md5()):
        result = sg.popup_yes_no('Database is not up to date. Download latest version?')
        if result == 'Yes':
            download_db()
            if not verify_db_md5(get_db_md5()):
                sg.popup_error('Database is still not up to date, please update manually. https://github.com/jojojo8359/neonmob-set-db/blob/main/all-sets.json')
            else:
                sg.popup_ok('Database has been successfully updated.')
    else:
        if show_status:
            sg.popup_ok('Database is up to date.')


def load_set_db():
    global SETDB
    try:
        with open('db.json', 'r') as f:
            SETDB = json.load(f)
        return SETDB
    except OSError:
        with open('db.json', 'w') as f:
            f.write("[]")
        SETDB = []


def load_recent(window):
    global RECENT
    try:
        with open('recent.json', 'r') as f:
            RECENT = json.load(f)
        window.write_event_value('-RECENT-LOADED-', RECENT)
    except OSError:
        save_recent()
    except JSONDecodeError:
        save_recent()


def save_recent():
    global RECENT, MAX_RECENT
    del RECENT[MAX_RECENT:]
    with open('recent.json', 'w') as f:
        json.dump(RECENT, f)


def load_cards(setid):
    if path.exists('cache/cards/' + str(setid) + '.json'):
        with open('cache/cards/' + str(setid) + '.json', 'r') as f:
            cards = json.load(f)
        return cards
    else:
        return 0


def save_cards(setid, cards):
    if not path.exists('cache/'):
        os.mkdir('cache/')
    if not path.exists('cache/cards/'):
        os.mkdir('cache/cards/')
    with open('cache/cards/' + str(setid) + '.json', 'w') as f:
        json.dump(cards, f)


def search_db(query):
    global SETDB
    filtered = list(filter(lambda series: query.lower() in series['name'].lower() or query.lower() in series['name_slug'].lower(), SETDB))
    filtered.reverse()
    return filtered


def process_set_results(results):
    rows = []
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    for item in results:
        if item['edition_size'] == 'unlimited':
            char = '∞'
        else:
            char = 'LE'
        name = item['name']

        rows.append([emoji_pattern.sub(r'', name), item['creator']['name'], char, item['id']])
    return rows


def process_cards(results):
    rows = []
    for item in results:
        rows.append([item['rarity'], item['name'], item['setName'], item['id']])
    return rows


def card_url(setid):
    return "https://www.neonmob.com/api/sets/" + str(setid) + "/piece-names"


def set_url(setid):
    return "https://www.neonmob.com/api/setts/" + str(setid) + "/"


def get_cards(setid, force=False):
    cards = load_cards(setid)
    if cards != 0 and not force:
        print("Card found in cache")
        return cards

    set_data = get_json(set_url(setid))
    set_name = set_data['name']

    cards = []
    set_card_data = get_json(card_url(setid))
    for card in set_card_data:
        cards.append({'name': card['name'],
                      'rarity': card['rarity']['name'],
                      'id': card['id'],
                      'setName': set_name})
    save_cards(setid, cards)
    return cards


def load_cache():
    global SCACHE, OCACHE
    if not path.exists('cache/'):
        os.mkdir('cache/')
    if not path.exists('cache/scache.json'):
        save_cache()
    if not path.exists('cache/ocache.json'):
        save_cache()
    with open('cache/scache.json', 'r') as f:
        SCACHE = json.load(f)
    with open('cache/ocache.json', 'r') as f:
        OCACHE = json.load(f)


def save_cache():
    global SCACHE, OCACHE
    with open('cache/scache.json', 'w') as f:
        json.dump(SCACHE, f)
    with open('cache/ocache.json', 'w') as f:
        json.dump(OCACHE, f)


def purge_cache():
    global SCACHE, OCACHE
    load_cache()
    current_millis = int(round(time.time() * 1000))
    for k in list(SCACHE.keys()):
        if current_millis - SCACHE[k]['time'] >= (KEEP_ALIVE_MINS * 60 * 1000):
            del SCACHE[k]
    for k in list(OCACHE.keys()):
        if current_millis - OCACHE[k]['time'] >= (KEEP_ALIVE_MINS * 60 * 1000):
            del OCACHE[k]
    save_cache()


def delete_cache():
    global SCACHE, OCACHE
    with open('cache/scache.json', 'w') as f:
        json.dump({}, f)
    with open('cache/ocache.json', 'w') as f:
        json.dump({}, f)
    SCACHE = {}
    OCACHE = {}


def parse_trader_grade(grade):
    grades = ['F', 'F+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
    return grades[int(grade)]


def get_seeker_url(cardid):
    return "https://www.neonmob.com/api/pieces/" + str(cardid) + "/needers/?completion=desc&grade=desc&wishlisted=desc"


def get_owner_url(cardid):
    return "https://www.neonmob.com/api/pieces/" + str(cardid) + "/owners/?completion=asc&grade=desc&owned=desc"


def get_prints_url(user_id, card_id):
    return "https://www.neonmob.com/api/users/" + str(user_id) + "/piece/" + str(card_id) + "/detail/"


def get_seekers(window, card, force=False):
    global SCACHE, SEARCHING

    purge_cache()

    if card['id'] == -1:
        print("Couldn't find card " + card['name'] + " in set " + card['setName'])
        return []

    current_millis = int(round(time.time() * 1000))
    if str(card['id']) in SCACHE.keys() and not force:
        print("Card is in cache")
        if current_millis - SCACHE[str(card['id'])]['time'] < (KEEP_ALIVE_MINS * 60 * 1000):
            print("Time is under 10 minutes")
            cached_seekers = SCACHE[str(card['id'])]['seekers'].copy()
            for seeker in cached_seekers:
                wants = []
                for wants_card in seeker['wants']:
                    if wants_card['card_id'] == card['id']:
                        wants.append(wants_card)
                seeker['wants'] = wants
            # TODO: Filter cached results to only card the search is looking for
            return cached_seekers

    seekers = []
    seeker_data = get_json(get_seeker_url(card['id']))
    total = seeker_data['count']
    next_url = seeker_data['next']
    i = 0

    while next_url:
        next_url = seeker_data['next']
        for seeker in seeker_data['results']:
            seekers.append({'id': seeker['id'],
                            'name': seeker['name'],
                            'trader_score': seeker['trader_score'],
                            'wants': [
                                {
                                    'card_id': card['id'],
                                    'card_name': card['name'],
                                    'set_name': card['setName'],
                                    'rarity': card['rarity'],
                                    'wishlisted': seeker['wishlisted'],
                                    'total_specials': seeker['special_piece_count'],
                                    'specials': seeker['owned_special_piece_count'],
                                    'percentage': seeker['owned_percentage']
                                }
                            ],
                            'owns': []
                            })
            i += 1
            window.write_event_value('-PROGRESS-UPDATE-', ("Fetching seekers...", i, total, "Getting seekers of " + card['name'] + " [" + str(card['id']) + "]..."))
        if not next_url:
            break
        seeker_data = get_json("https://www.neonmob.com" + next_url)
    try:
        SCACHE.pop(str(card['id']))
    except KeyError:
        print("Card is not in cache")
    current_millis = int(round(time.time() * 1000))
    SCACHE.update({card['id']: {'time': current_millis, 'cardName': card['name'],
                                'setName': card['setName'], 'seekers': seekers}})
    save_cache()
    return seekers


def get_owners(window, card, force=False):
    global OCACHE, SEARCHING

    purge_cache()

    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []

    currentMillis = int(round(time.time() * 1000))
    if str(card['id']) in OCACHE.keys() and not force:
        print("Card is in cache")
        if currentMillis - OCACHE[str(card['id'])]['time'] < (KEEP_ALIVE_MINS * 60 * 1000):
            print("Time is under 10 minutes")
            cached_owners = OCACHE[str(card['id'])]['owners'].copy()
            for owner in cached_owners:
                owns = []
                for owned_card in owner['owns']:
                    if owned_card['card_id'] == card['id']:
                        owns.append(owned_card)
                owner['owns'] = owns
            # TODO: Filter cached results to only card the search is looking for
            return cached_owners

    owners = []
    owner_data = get_json(get_owner_url(card['id']))
    total = owner_data['count']
    next_url = owner_data['next']
    i = 0

    while next_url:
        next_url = owner_data['next']
        for owner in owner_data['results']:
            owners.append({'id': owner['id'],
                           'name': owner['name'],
                           'trader_score': owner['trader_score'],
                           'owns': [
                               {
                                   'card_id': card['id'],
                                   'card_name': card['name'],
                                   'set_name': card['setName'],
                                   'rarity': card['rarity'],
                                   'print_count': owner['print_count'],
                                   'total_specials': owner['special_piece_count'],
                                   'specials': owner['owned_special_piece_count'],
                                   'percentage': owner['owned_percentage']
                               }
                           ],
                           'wants': []
                           })
            i += 1
            window.write_event_value('-PROGRESS-UPDATE-', ("Fetching owners...", i, total, "Getting owners of " + card['name'] + " [" + str(card['id']) + "]..."))
        if not next_url:
            break
        owner_data = get_json("https://www.neonmob.com" + next_url)
    try:
        OCACHE.pop(str(card['id']))
    except KeyError:
        print("Card is not in cache")
    current_millis = int(round(time.time() * 1000))
    OCACHE.update({card['id']: {'time': current_millis, 'cardName': card['name'], 'setName': card['setName'], 'owners': owners}})
    save_cache()
    return owners


def combine_people(nestedlist1, nestedlist2):
    """Combines all people (dictionaries) from two lists, merging data along the way

    For example, if a person is found once in both given lists, the cards they own and need will be combined into one person object and included in the result
    :param List[List[Dict[str, Union[int, str, float, List[Dict[str, Union[int, str]]]]]]] nestedlist1: The first list of raw people data
    :param List[List[Dict[str, Union[int, str, float, List[Dict[str, Union[int, str]]]]]]] nestedlist2: The second list of raw people data
    :return: A list of unique people whose attributes have been combined
    :rtype: List[Dict[str, Union[int, str, float, List[Dict[str, Union[int, str]]]]]]
    """
    master = []
    allids = []
    list1 = []
    for larg in nestedlist1:
        list1.extend(larg)
    for larg in nestedlist2:
        list1.extend(larg)

    for person in list1:
        if person['id'] not in allids:
            master.append(person)
            allids.append(person['id'])
        else:
            currentindex = [i for i, t in enumerate(master) if t['id'] == person['id']][0]
            currentperson = master[currentindex]
            for i in range(len(person['owns'])):
                check = True
                for j in range(len(currentperson['owns'])):
                    if person['owns'][i]['card_name'] == currentperson['owns'][j]['card_id']:
                        check = False
                if check:
                    currentperson['owns'].append(person['owns'][i])

            for i in range(len(person['wants'])):
                check = True
                for j in range(len(currentperson['wants'])):
                    if person['wants'][i]['card_name'] == currentperson['wants'][j]['card_id']:
                        check = False
                if check:
                    currentperson['wants'].append(person['wants'][i])
    return master


def get_commons(people, owned, want, mode='and', checkprintcount=False):
    """Finds users who have and want specific cards

    :param List[Dict[str, Union[int, str, float, List[Dict[str, Union[int, str]]]]]] people: A list of people to search through
    :param List[int] owned: A list of user-owned card ids to check
    :param List[int] want: A list of user-wanted card ids to check
    :param str mode: 'and' will require all card conditions to be met, while 'or' requires at least one card condition on each side of the trade to be met
    :param bool checkprintcount: Whether or not to include users with single copies (False will search for singles, True will not)
    :return: A list of users who meet the conditions specified
    :rtype: List[Dict[str, Union[int, str, float, List[Dict[str, Union[int, str]]]]]]
    """
    master = []
    if mode == 'and':
        for person in people:
            mastercheck = True
            if len(person['owns']) == 0 or len(person['wants']) == 0:
                continue
            # print("Person does not have empty lists")
            for ownedid in owned:
                cardcheck = False
                for ownedcard in person['owns']:
                    if checkprintcount and ownedcard['print_count'] < 2:
                        break
                    elif ownedid == ownedcard['card_id']:
                        cardcheck = True
                        break
                if not cardcheck:
                    mastercheck = False
                    break
            for wantedid in want:
                cardcheck = False
                for wantedcard in person['wants']:
                    if wantedid == wantedcard['card_id']:
                        cardcheck = True
                        break
                if not cardcheck:
                    mastercheck = False
                    break
            if mastercheck:
                master.append(person)
    elif mode == 'or':
        for person in people:
            mastercheck = False
            printcheck = True
            if len(person['owns']) == 0 or len(person['wants']) == 0:
                continue
            for ownedid in owned:
                cardcheck = False
                for ownedcard in person['owns']:
                    if checkprintcount and ownedcard['print_count'] >= 2:
                        printcheck = False
                    if ownedid == ownedcard['card_id']:
                        cardcheck = True
                        break
                if cardcheck:
                    mastercheck = True
            for wantedid in want:
                cardcheck = False
                for wantedcard in person['wants']:
                    if wantedid == wantedcard['card_id']:
                        cardcheck = True
                        break
                if cardcheck:
                    mastercheck = True
            if mastercheck and not printcheck:
                master.append(person)
    return master


defaultsets = [['', '', '', '']]
defaultcards = [['', '', '']]
defaultcards2 = [['', '', '', '']]
defaultpeople = [['', '', '', '']]


def make_mainwindow():
    """Builds the main window where the user creates a search query

    :return: Built window (finalized)
    :rtype: PySimpleGUI.Window
    """
    table1 = [[sg.Table(defaultsets, num_rows=10, key='-TABLE1-', headings=['Rarity', 'Card Name', 'Set Name', 'id'],
                        col_widths=[10, 30, 30, 9], auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, False])]]
    table2 = [[sg.Table(defaultsets, num_rows=10, key='-TABLE2-', headings=['Rarity', 'Card Name', 'Set Name', 'id'],
                        col_widths=[10, 30, 30, 9], auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, False])]]

    column1 = [[sg.Button('+', key='-OTHERADD-')],
               [sg.Button('-', key='-OTHERREMOVE-')],
               [sg.Button('C', key='-OTHERCLEAR-')]]
    column2 = [[sg.Button('+', key='-YOUADD-')],
               [sg.Button('-', key='-YOUREMOVE-')],
               [sg.Button('C', key='-YOUCLEAR-')]]

    frame1 = [[sg.Column(table1), sg.Column(column1)]]
    frame2 = [[sg.Column(table2), sg.Column(column2)]]

    if sys.platform == 'darwin':
        menu = sg.Menu([['&File', ['Settings', '---', 'Update Database', 'Delete Cache', '---', 'E&xit']]])
    else:
        menu = sg.Menu([['&File', ['Settings', '---', 'Update Database', 'Delete Cache', '---', 'E&xit']]],
                background_color='#FFFFFF', text_color='#000000')

    layout = [[menu],
              [sg.Frame(layout=frame1, title="Cards I'm seeking from someone else"), sg.Frame(layout=frame2, title="Cards I want to trade away")],
              [sg.Button('Search', key='-SEARCHBUTTON-'), sg.Checkbox('Force Refresh', default=False, key='-REFRESH-'),
               sg.Combo(['And', 'Or'], 'And', key='-MODE-', readonly=True), sg.Checkbox('2+ Prints', default=True, key='-PRINTS-')]]

    window = sg.Window('NeonMobMatcher v1.1.1', layout, finalize=True, resizable=True)
    # window.maximize()
    return window


def make_setwindow(recent, target):
    """Builds the set selection window

    :return: Built window (finalized)
    :rtype: PySimpleGUI.Window
    """
    # if not RECENT:
    #     loadRecent()
    if target == 0:
        target_text = "Another Person Has:"
    else:
        target_text = "You Have:"
    layout = [[sg.Input(size=(30, 1), enable_events=True, key='-INPUT-', tooltip='Search for a set by name', focus=True)],
              [sg.Table(recent, num_rows=15, key='-SETTABLE-', headings=['Set Name', 'Author', ' ', 'id'],
                        col_widths=[30, 20, 3, 8], auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, False], bind_return_key=True)],
              [sg.Button('OK'), sg.Button('Cancel')]]
    window = sg.Window('Set Selection | ' + target_text, layout, finalize=True)
    return window


def make_cardwindow(target):  # TODO: Maybe display set name? If so pass in here
    """Builds the card selection window

    :param int setid: The id of the set to show cards for
    :return: Built window (finalized)
    :rtype: PySimpleGUI.Window
    """
    if target == 0:
        target_text = "Another Person Has:"
    else:
        target_text = "You Have:"
    layout = [[sg.Text('Sorting: ', key='-CARDSORTTEXT-')],
              [sg.Table(defaultcards, num_rows=15, key='-CARDTABLE-',
                        headings=['Rarity', 'Card Name', 'Set Name', 'id'], col_widths=[10, 30, 30, 9],
                        auto_size_columns=False, justification='left', visible_column_map=[True, True, False, False],
                        select_mode=sg.TABLE_SELECT_MODE_EXTENDED, enable_click_events=True)],
              [sg.Button('OK'), sg.Button('Cancel'), sg.Button('Refresh'),
               sg.Combo(['Common', 'Uncommon', 'Rare', 'Very Rare', 'Extra Rare', 'Chase', 'Variant'], key='-RARITY-', readonly=True),
               sg.Button('Add All of Rarity')]]
    window = sg.Window('Card Selection | ' + target_text, layout, finalize=True)
    # new_rows = processCards(GetCards(setid))
    # window['-CARDTABLE-'].update(new_rows)
    return window


def make_resultwindow(series):
    """Builds the search results window

    :param List[Dict[str, Union[int, str, float, List[Dict[str, Union[int, str]]]]]] results: A list of raw trade search results
    :return: Built window (finalized)
    :rtype: PySimpleGUI.Window
    """
    table1 = [[sg.Table(defaultcards2, num_rows=10, key='-OWNTABLE-',
                        headings=['Rarity', 'Card Name', 'Set Name', 'Prints', 'id'], col_widths=[10, 20, 20, 5, 9],
                        auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, True, False],
                        enable_events=True)]]

    table2 = [[sg.Table(defaultcards2, num_rows=10, key='-WANTTABLE-',
                        headings=['Rarity', 'Card Name', 'Set Name', 'Wishlisted', 'id'], col_widths=[10, 20, 20, 8, 9],
                        auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, True, False])]]

    frame1 = [[sg.Column(table1)]]
    frame2 = [[sg.Column(table2)]]

    #  0     1         2       3      4     5     6        7         8         9           10       11
    # id, have_raw, want_raw, Name, Grade, Have, Want, Wishlisted, Prints, Last Active, (Core %, Special %)
    # 9     30         30      20     5     5     5        10        10        15         6          8

    series_headings = [x for x in series]
    headings = ['id', 'have_raw', 'want_raw', 'Name', 'Grade', 'Have', 'Want', 'Wishlisted', 'Prints', 'Last Active']
    headings.extend(series_headings)

    series_widths = [18 for x in series]
    col_widths = [9, 30, 30, 20, 5, 5, 5, 8, 6, 10]
    col_widths.extend(series_widths)

    series_visible_columns = [True for x in series]
    visible_column_map = [False, False, False, True, True, True, True, True, True, True]
    visible_column_map.extend(series_visible_columns)

    layout = [[sg.Text('Sorting: ', key='-RESULTSSORTTEXT-'), sg.Button('Reset', key='-RESETSORT-')],
              [sg.Table(defaultpeople, num_rows=15, key='-PEOPLETABLE-',
                        headings=headings, col_widths=col_widths, auto_size_columns=False, justification='left',
                        visible_column_map=visible_column_map, enable_events=True, enable_click_events=True)],
              [sg.Frame(layout=frame1, title="___ Has:", key='-OTHERFRAME-'),
               sg.Frame(layout=frame2, title="You Have:")],
              [sg.Button('OK'), sg.Button('Open User Profile'), sg.Text('', key='-PRINTNUMS-')]]
    window = sg.Window('Results', layout, finalize=True)
    # new_rows = processResults(results)
    # window['-PEOPLETABLE-'].update(new_rows)
    return window


def update_set_search(window, query):
    new_values = search_db(query)  # TODO: Add limit on how many results can be returned
    new_rows = process_set_results(new_values)

    window.write_event_value('-UPDATE-SET-ROWS-', new_rows)


def update_card_selection(window, setid):
    new_rows = process_cards(get_cards(setid))
    window.write_event_value('-UPDATE-CARD-ROWS-', new_rows)


def sort_card_list(window, old_rows, sort_method, reverse):
    new_rows = []

    rarities = ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Extra Rare', 'Chase', 'Variant', 'Legendary']

    if sort_method == 'name':
        new_rows = sorted(old_rows, key=lambda rowx: rowx[1])  # Alphabetical normal
        if reverse:
            new_rows.reverse()

    elif sort_method == 'rarity':
        if reverse:
            rarities.reverse()
        old_rows = sorted(old_rows, key=lambda rowx: rowx[1])
        for rarity in rarities:
            for row in old_rows:
                if row[0] == rarity:
                    new_rows.append(row)
    window.write_event_value('-UPDATE-CARD-ROWS-', new_rows)


def sort_results(window, old_rows, sort_by_columns):
    # 0 = Name, 1 = Grade, 2 = Have, 3 = Want, 4 = Wishlisted, 5 = Prints, 6 = Last Active, 7+ = Series Completion

    #  0     1         2       3      4     5     6        7         8         9           10       11
    # id, have_raw, want_raw, Name, Grade, Have, Want, Wishlisted, Prints, Last Active, (Core %, Special %)

    original = old_rows.copy()

    grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F+', 'F']
    times = ['just now', 'min ago', 'hour ago', 'hours ago', 'day ago', 'days ago', 'month ago', 'months ago',
             'year ago', 'years ago']
    conversion = {'name': 3, 'grade': 4, 'have': 5, 'want': 6, 'wishlisted': 7, 'prints': 8, 'last_active': 9, 'completion': 10}
    visible_conversion = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7}

    sort_by_text = []
    for column in sort_by_columns:
        if column == 3:
            sort_by_text.append('name')
        elif column == 4:
            sort_by_text.append('grade')
        elif column == 5:
            sort_by_text.append('have')
        elif column == 6:
            sort_by_text.append('want')
        elif column == 7:
            sort_by_text.append('wishlisted')
        elif column == 8:
            sort_by_text.append('prints')
        elif column == 9:
            sort_by_text.append('last_active')
        elif column == 10:
            sort_by_text.append('completion')

    new_rows = []

    sort_order = RESULT_SORT_ORDER.copy()
    sort_order.reverse()

    display = []

    for method in sort_order:
        if method in sort_by_text:
            if conversion[method] == 3:
                original.sort(key=lambda x: x[conversion[method]].lower())
            elif conversion[method] == 4:
                original.sort(key=lambda x: grades.index(x[conversion[method]]))
            elif conversion[method] == 5:
                original.sort(key=lambda x: x[conversion[method]], reverse=True)
            elif conversion[method] == 6:
                original.sort(key=lambda x: x[conversion[method]], reverse=True)
            elif conversion[method] == 7:
                original.sort(key=lambda x: x[conversion[method]], reverse=True)
            elif conversion[method] == 8:
                original.sort(key=lambda x: x[conversion[method]])
            elif conversion[method] == 9:
                for result in original:
                    if result[conversion[method]] == 'just now':
                        result[conversion[method]] = '0 just now'
                original.sort(key=lambda x: int(x[conversion[method]].split(' ')[0]))
                original.sort(key=lambda x: times.index(' '.join(x[conversion[method]].split(' ')[1:])))
            elif conversion[method] == 10:
                original.sort(key=lambda x: int(x[conversion[method]].split('%')[0]), reverse=True)
            display.append(method)

    display.reverse()

    for result in original:
        if result[conversion['last_active']] == '0 just now':
            result[conversion['last_active']] = 'just now'

    window.write_event_value('-SET-RESULTS-', original)
    window.write_event_value('-SET-RESULT-SORT-TEXT-', display)


def perform_search(window, items1, items2, force_refresh, mode, print_count):
    owners = []
    for card in items1:
        carddict = {'name': card[1], 'rarity': card[0], 'id': card[3], 'setName': card[2]}
        newowners = get_owners(window, carddict, force=force_refresh)
        if newowners == -1:
            window.write_event_value('-SEARCH-CANCELED-', '')
            return
        else:
            owners.append(newowners)
    seekers = []
    for card in items2:
        carddict = {'name': card[1], 'rarity': card[0], 'id': card[3], 'setName': card[2]}
        newseekers = get_seekers(window, carddict, force=force_refresh)
        if newseekers == -1:
            window.write_event_value('-SEARCH-CANCELED-', '')
        else:
            seekers.append(newseekers)
    combined = combine_people(owners, seekers)
    filtered = get_commons(combined, [x[3] for x in items1], [x[3] for x in items2], mode=mode, checkprintcount=print_count)
    window.write_event_value('-SEARCH-FINISHED-', filtered)

#  0     1         2       3      4     5     6        7         8         9           10       11
# id, have_raw, want_raw, Name, Grade, Have, Want, Wishlisted, Prints, Last Active, (Core %, Special %)


def process_results(window, results, series):
    for person in results:
        num_wishlisted = 0
        num_two_prints = 0
        for card in person['wants']:
            if card['wishlisted']:
                num_wishlisted += 1
        for card in person['owns']:
            if card['print_count'] >= 2:
                num_two_prints += 1

        user_id = person['id']
        page = 1
        last_active = ''
        while not last_active:
            activity_url = "https://napi.neonmob.com/activityfeed/user/" + str(user_id) + "/?amount=20&page=" + str(page)
            activity_data = get_json(activity_url)
            for activity in activity_data:
                if activity['type'] == 'pack-opened':
                    last_active = activity['created']
                    break
            page += 1
            if page == 101:
                break

        percentages = []
        processed = []

        for e in series:
            if e in processed:
                continue
            for card in person['wants']:
                if card['set_name'] == e and e not in processed:
                    specials = card['total_specials']
                    if specials == 0:
                        special_percent = "--"
                    else:
                        special_percent = int((card['specials'] / card['total_specials']) * 100)
                    percentages.append(str(card['percentage']) + '% (' + str(special_percent) + "%)")
                    processed.append(e)
            if e in processed:
                continue
            for card in person['owns']:
                if card['set_name'] == e and e not in processed:
                    specials = card['total_specials']
                    if specials == 0:
                        special_percent = "--"
                    else:
                        special_percent = int((card['specials'] / card['total_specials']) * 100)
                    percentages.append(str(card['percentage']) + '% (' + str(special_percent) + "%)")
                    processed.append(e)

        args = [person['id'], person['owns'], person['wants'], person['name'], parse_trader_grade(person['trader_score']), len(person['owns']), len(person['wants']), str(num_wishlisted) + '/' + str(len(person['wants'])), str(num_two_prints) + '/' + str(len(person['owns'])), last_active]
        args.extend(percentages)

        window.write_event_value('-ADD-RESULT-ROW-', args)
        # window.write_event_value('-ADD-RESULT-ROW-', [person['name'], parse_trader_grade(person['trader_score']), len(person['owns']), len(person['wants']), person['id'], person['owns'], person['wants']])


def get_print_numbers(window, user_id, card_id):
    prints_data = get_json(get_prints_url(user_id, card_id))
    prints = []
    for copy in prints_data['refs'][prints_data['payload'][1]]['prints']:
        prints.append(copy['print_num'])
    window.write_event_value('-UPDATE-PRINTS-', 'Print Numbers: ' + ', '.join(str(i) for i in prints))


SCACHE = {}
OCACHE = {}
RECENT = []
SETDB = []
TARGET = 0
SEARCHING = False
ITEMS1 = []
ITEMS2 = []
MAX_RECENT = 30
KEEP_ALIVE_MINS = 10
RESULT_SORT_ORDER = ['grade', 'last_active', 'completion', 'wishlisted', 'prints', 'have', 'want', 'name']  # Beginning has higher precedence than end
# TODO: Add sort order as an option


def main():
    global SCACHE, OCACHE, RECENT, SETDB, TARGET, SEARCHING, ITEMS1, ITEMS2, MAX_RECENT
    LASTSEARCH = ""
    RESULT_ROWS = []
    cardlist_reverse = [None, None]
    series = ()
    sort_results_by = []
    db_attempt_update(show_status=False)  # TODO: Make a thread? (tried and not very good)
    SETDB = load_set_db()
    # TODO: Load db after attempting to update
    window1, window2, window3, window4 = make_mainwindow(), None, None, None
    while True:
        window, event, values = sg.read_all_windows()
        print(event, values)

        if event == '__TIMEOUT__':
            continue

        # Exit events
        if event in (sg.WIN_CLOSED, 'Exit'):
            if window == window1:
                break
            elif window == window2:
                window2.close()
                window2 = None
            elif window == window3:
                window3.close()
                window3 = None
            elif window == window4:
                window4.close()
                window4 = None

        # Window-specific events
        if window == window1:
            if event == 'Update Database' and not SEARCHING:
                db_attempt_update()

            if event == '-OTHERADD-' and not SEARCHING:
                if window2 is not None:
                    window2.ding()
                    window2.bring_to_front()
                elif window3 is not None:
                    window3.ding()
                    window3.bring_to_front()
                else:
                    TARGET = 0
                    window2 = make_setwindow(RECENT, TARGET)
                    window = window2
                    window.write_event_value('-STARTTHREAD-', (load_recent, window))
                continue
            elif event == '-OTHERREMOVE-' and not SEARCHING:
                try:
                    ITEMS1.pop(values['-TABLE1-'][0])
                except IndexError:
                    pass
                window1['-TABLE1-'].update(ITEMS1)
            elif event == '-OTHERCLEAR-' and not SEARCHING:
                if sg.popup_yes_no("Really clear?") == 'Yes':
                    ITEMS1.clear()
                    window1['-TABLE1-'].update(ITEMS1)

            if event == '-YOUADD-' and not SEARCHING:
                if window2 is not None:
                    window2.ding()
                    window2.bring_to_front()
                elif window3 is not None:
                    window3.ding()
                    window3.bring_to_front()
                else:
                    TARGET = 1
                    window2 = make_setwindow(RECENT, TARGET)
                    window = window2
                    window.write_event_value('-STARTTHREAD-', (load_recent, window))
                continue
            elif event == '-YOUREMOVE-' and not SEARCHING:
                try:
                    ITEMS2.pop(values['-TABLE2-'][0])
                except IndexError:
                    pass
                window1['-TABLE2-'].update(ITEMS2)
            elif event == '-YOUCLEAR-' and not SEARCHING:
                if sg.popup_yes_no("Really clear?") == 'Yes':
                    ITEMS2.clear()
                    window1['-TABLE2-'].update(ITEMS2)

            if event == '-SEARCHBUTTON-':
                if not SEARCHING:
                    SEARCHING = True
                    window['-SEARCHBUTTON-'].update(disabled=True)
                    window['-REFRESH-'].update(disabled=True)
                    window['-MODE-'].update(disabled=True)
                    window['-PRINTS-'].update(disabled=True)
                    if window4 is not None:  # If results from a previous search are still on the screen, kill that window to begin the next search
                        window4.close()
                        window4 = None
                    if window3 is not None:  # If the user is still searching through cards, close that window to begin the search
                        window3.close()
                        window3 = None
                    if window2 is not None:  # If the user is still searching through sets, close that window to begin the search
                        window2.close()
                        window2 = None
                    # if settingswindow is not None:  # If the user is changing settings, close that window to begin the search
                    #     settingswindow.close()
                    #     settingswindow = None
                    if len(ITEMS1) == 0 or len(ITEMS2) == 0:
                        sg.popup_error("Please add items to both lists")
                    else:
                        window.write_event_value('-STARTTHREAD-', (perform_search, window, ITEMS1, ITEMS2, values['-REFRESH-'], values['-MODE-'].lower(), values['-PRINTS-']))
                    continue

            if event == 'Delete Cache':
                if sg.popup_yes_no("Are you sure you want to delete the cache? Loading times will be significantly impacted."):
                    delete_cache()
                    sg.popup("Cache successfully deleted!")

        if window == window2:
            if event == 'Cancel':
                window2.close()
                window2 = None
                continue
            if values['-INPUT-'] == '':
                LASTSEARCH = values['-INPUT-']
                window['-SETTABLE-'].update(RECENT)
            elif values['-INPUT-'] != LASTSEARCH:
                window['-SETTABLE-'].update([['Loading...', '', '', '']])
                LASTSEARCH = values['-INPUT-']
                window.write_event_value('-STARTTHREAD-', (update_set_search, window, values['-INPUT-']))

            if event == 'OK' or event == '-SETTABLE-' and len(values['-SETTABLE-']):
                selected = window['-SETTABLE-'].get()[values['-SETTABLE-'][0]]
                if selected in RECENT:
                    RECENT.remove(selected)
                RECENT.insert(0, selected)
                save_recent()
                SETID = selected[3]
                window3 = make_cardwindow(TARGET)
                cardlist_reverse = [None, None]
                window2.close()
                window2 = None
                window = window3
                window['-CARDTABLE-'].update([['Loading...', '']])
                window.write_event_value('-STARTTHREAD-', (update_card_selection, window, SETID))
                continue

        if window == window3:
            if event == 'Cancel':
                window3.close()
                window3 = None
                continue
            if event == 'Refresh':
                # TODO: Reset card sorting
                window['-CARDTABLE-'].update([['Loading...', '']])
                window.write_event_value('-STARTTHREAD-', (update_card_selection, window, SETID))
            elif event[0] == '-CARDTABLE-' and event[2] == (-1, 0):
                print('Sort By Rarity')
                print('Before: ' + str(cardlist_reverse))
                if cardlist_reverse[0] is None:
                    cardlist_reverse[0] = False
                else:
                    cardlist_reverse[0] = not cardlist_reverse[0]
                cardlist_reverse[1] = None
                print('After: ' + str(cardlist_reverse))
                window['-CARDSORTTEXT-'].update(value='Sorting: Rarity' + (' (asc)' if cardlist_reverse[0] else ' (desc)'))
                window.write_event_value('-STARTTHREAD-', (sort_card_list, window, window['-CARDTABLE-'].get(), 'rarity', cardlist_reverse[0]))
                window['-CARDTABLE-'].update([['Sorting...', '']])
            elif event[0] == '-CARDTABLE-' and event[2] == (-1, 1):
                print('Sort By Name')
                print('Before: ' + str(cardlist_reverse))
                if cardlist_reverse[1] is None:
                    cardlist_reverse[1] = False
                else:
                    cardlist_reverse[1] = not cardlist_reverse[1]
                cardlist_reverse[0] = None
                print('After: ' + str(cardlist_reverse))
                window['-CARDSORTTEXT-'].update(value='Sorting: Name' + (' (asc)' if cardlist_reverse[1] else ' (desc)'))
                window.write_event_value('-STARTTHREAD-', (sort_card_list, window, window['-CARDTABLE-'].get(), 'name', cardlist_reverse[1]))
                window['-CARDTABLE-'].update([['Sorting...', '']])
            elif event == 'OK' and len(values['-CARDTABLE-']):
                indexes = values['-CARDTABLE-']
                items = window['-CARDTABLE-'].get()
                selected = []
                for index in indexes:
                    selected.append(items[index])
                if TARGET == 0:
                    ITEMS1.extend(selected)
                    window1['-TABLE1-'].update(ITEMS1)
                else:
                    ITEMS2.extend(selected)
                    window1['-TABLE2-'].update(ITEMS2)
                window3.close()
                window3 = None
                continue
            elif event == 'Add All of Rarity' and values['-RARITY-'] != '':
                current_rows = window['-CARDTABLE-'].get()
                rarity_cards = []
                for row in current_rows:
                    if row[0] == values['-RARITY-']:
                        rarity_cards.append(row)
                if TARGET == 0:
                    ITEMS1.extend(rarity_cards)
                    window1['-TABLE1-'].update(ITEMS1)
                else:
                    ITEMS2.extend(rarity_cards)
                    window1['-TABLE2-'].update(ITEMS2)
                window3.close()
                window3 = None
                continue

        if window == window4:
            #  0      1      2     3    4      5        6
            # Name, Grade, Have, Want, id, have_raw, want_raw

            #  0     1         2       3      4     5     6        7         8         9           10       11
            # id, have_raw, want_raw, Name, Grade, Have, Want, Wishlisted, Prints, Last Active, (Core %, Special %)

            if event == 'OK':
                window4.close()
                window4 = None
                continue
            if event[0] == '-PEOPLETABLE-' and event[2][0] == -1:
                # 0 = Name, 1 = Grade, 2 = Have, 3 = Want, 4 = Wishlisted, 5 = Prints, 6 = Last Active, 7+ = Series Completion

                visible_column = event[2][1]
                if visible_column > 7:
                    visible_column = 7
                if visible_column in sort_results_by:
                    sort_results_by.remove(visible_column)
                else:
                    sort_results_by.append(visible_column)

                visible_translation = {0: 3, 1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10}  # visible: raw
                # for count, i_set in enumerate(series):
                #     visible_translation[7 + count] = 10 + count

                raw_columns = []
                for column in sort_results_by:
                    raw_columns.append(visible_translation[column])

                sort_results(window, RESULT_ROWS, raw_columns)
                pass
            if event == '-RESETSORT-':
                window['-PEOPLETABLE-'].update(RESULT_ROWS)
                window['-RESULTSSORTTEXT-'].update('Sorting: ')
                sort_results_by = []
            if event == '-PEOPLETABLE-' and len(values['-PEOPLETABLE-']):
                people = window['-PEOPLETABLE-'].get()
                index = values['-PEOPLETABLE-'][0]
                person = people[index]
                owned = []
                # noinspection PyTypeChecker
                for ownedcard in person[1]:
                    ownedcarddict = dict(ownedcard)
                    owned.append(
                        [ownedcarddict['rarity'], ownedcarddict['card_name'], ownedcarddict['set_name'], ownedcarddict['print_count'],
                         ownedcarddict['card_id']])
                wanted = []
                # noinspection PyTypeChecker
                for wantedcard in person[2]:
                    wantedcarddict = dict(wantedcard)
                    wanted.append(
                        [wantedcarddict['rarity'], wantedcarddict['card_name'], wantedcarddict['set_name'],
                         'Yes' if wantedcarddict['wishlisted'] else 'No',
                         wantedcarddict['card_id']])
                window['-OWNTABLE-'].update(owned)
                window['-WANTTABLE-'].update(wanted)
                # noinspection PyTypeChecker
                window['-OTHERFRAME-'].update(value=person[3] + " Has:")
                window['-PRINTNUMS-'].update(value='')
            if event == '-OWNTABLE-' and len(values['-OWNTABLE-']) and len(values['-PEOPLETABLE-']):
                window['-PRINTNUMS-'].update(value='Loading print numbers...')
                card_index = values['-OWNTABLE-'][0]
                people = window['-PEOPLETABLE-'].get()
                person_index = values['-PEOPLETABLE-'][0]
                person = people[person_index]
                user_id = person[0]
                card_id = window['-OWNTABLE-'].get()[card_index][4]
                window.write_event_value('-STARTTHREAD-', (get_print_numbers, window, user_id, card_id))
            if event == 'Open User Profile' and len(values['-PEOPLETABLE-']):
                index = values['-PEOPLETABLE-'][0]
                webbrowser.open_new_tab("https://www.neonmob.com/user/" + str(window['-PEOPLETABLE-'].get()[index][0]))

        # Async events
        if event == '-FOO-':
            pass
        if event == '-UPDATE-SET-ROWS-' and window2:
            window['-SETTABLE-'].update(values['-UPDATE-SET-ROWS-'])
        if event == '-UPDATE-CARD-ROWS-' and window3:
            window['-CARDTABLE-'].update(values['-UPDATE-CARD-ROWS-'])
        if event == '-RECENT-LOADED-' and window2:
            RECENT = values['-RECENT-LOADED-']
            if not window['-SETTABLE-'].get():
                window['-SETTABLE-'].update(RECENT)
        if event == '-SEARCH-CANCELED-':
            sg.popup("Search was canceled.", non_blocking=True)
        if event == '-SEARCH-FINISHED-':
            RESULTS = []
            RESULTS = values['-SEARCH-FINISHED-']
            SEARCHING = False
            window['-SEARCHBUTTON-'].update(disabled=False)
            window['-REFRESH-'].update(disabled=False)
            window['-MODE-'].update(disabled=False)
            window['-PRINTS-'].update(disabled=False)

            series = ()
            for item in ITEMS1:
                if not item[2] in series:
                    series += (item[2],)
            for item in ITEMS2:
                if not item[2] in series:
                    series += (item[2],)

            print(series)

            window4 = make_resultwindow(series)
            window = window4
            RESULT_ROWS = []
            window.write_event_value('-STARTTHREAD-', (process_results, window, RESULTS, series))
        if event == '-ADD-RESULT-ROW-':
            RESULT_ROWS.append(values['-ADD-RESULT-ROW-'])
            window['-PEOPLETABLE-'].update(RESULT_ROWS)
        if event == '-SET-RESULTS-':
            window['-PEOPLETABLE-'].update(values['-SET-RESULTS-'])
        if event == '-SET-RESULT-SORT-TEXT-':
            window['-RESULTSSORTTEXT-'].update('Sorting: ' + (', '.join(values['-SET-RESULT-SORT-TEXT-'])))
        if event == '-PROGRESS-UPDATE-':
            sg.one_line_progress_meter(values['-PROGRESS-UPDATE-'][0], values['-PROGRESS-UPDATE-'][1], values['-PROGRESS-UPDATE-'][2], values['-PROGRESS-UPDATE-'][3],
                                       orientation='h', key='-SEARCHBAR-', no_button=True)
        if event == '-UPDATE-PRINTS-':
            window['-PRINTNUMS-'].update(value=values['-UPDATE-PRINTS-'])

        # Starts a thread
        if event == '-STARTTHREAD-':
            # Function is found paired with -STARTTHREAD- event
            # args must contain a callback window to pass other events to
            thread_args = values['-STARTTHREAD-']
            threading.Thread(target=thread_args[0], args=thread_args[1:], daemon=True).start()

    window1.close()
    if window2 is not None:
        window2.close()
    if window3 is not None:
        window3.close()
    if window4 is not None:
        window4.close()


if __name__ == '__main__':
    main()
