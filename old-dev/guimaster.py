#!/usr/bin/python3

# ****************************************************************************
# NeonMob Trade Matcher Tool
# Version: 1.0.0
# ****************************************************************************
# Copyright (c) 2021 Joel Keaton
# All rights reserved.
# ****************************************************************************


# Builtins
import hashlib
import os
import sys
import traceback
import json
from json import JSONDecodeError
from os import path
import time
import webbrowser
import re

# pip packages
import PySimpleGUI as sg
import requests

sg.theme('DarkGrey9')

# Global variables
setdbpath = "db.json"
SETDB = []
TARGET = 0
AUTOUPDATE = True

recentpath = "recent.json"
RECENT = []
MAXRECENT = 30

SCACHE = {}
OCACHE = {}

keepalivemins = 10


# GENERAL I/O SECTION


# Database handling


def httperror(e):
    """Handles an HTTP Exception with PySimpleGUI

    :param Exception e: The exception to display
    """
    tb = traceback.format_exc()
    sg.Print(f'An HTTP exception occurred. Here is the info:', e, tb)
    sg.popup_error(f'AN HTTP EXCEPTION OCCURRED! Exiting...', e, tb)


def generalconnerror(e):
    """Handles a general connection error/exception with PySimpleGUI

    :param Exception e: The exception to display
    """
    tb = traceback.format_exc()
    sg.Print(f'An exception occurred. Here is the info:', e, tb)
    sg.popup_error(f'AN EXCEPTION OCCURRED! Exiting...', e, tb)


def fetchdb():
    """Gets the raw, most current set database file from GitHub (with connection exception handling)

    :return: The raw database list
    :rtype:  List[Dict[str, Union[int, str, Dict[str, str]]]]
    """
    try:
        r = requests.request('GET', 'https://raw.githubusercontent.com/jojojo8359/neonmob-set-db/main/all-sets.json')
        r.raise_for_status()
        db = r.json()
        return db
    except requests.ConnectionError:
        sg.popup_error('Connection error occurred! Exiting...')
        sys.exit(1)  # TODO: Rewrite error handling
    except requests.exceptions.HTTPError as e:
        httperror(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        generalconnerror(e)
        sys.exit(1)


def downloaddb():
    """Downloads and saves the latest set database in JSON form

    """
    db = fetchdb()
    with open(setdbpath, 'w') as f:
        json.dump(db, f)


def fetchmd5():
    """Gets the raw, most current md5 hash of the set database from GitHub (with connection exception handling)

    :return: The pure md5 hash of the database file
    :rtype:  str
    """
    try:
        r = requests.request('GET', 'https://raw.githubusercontent.com/jojojo8359/neonmob-set-db/main/all-sets.md5')
        r.raise_for_status()
        md5 = r.text
        return md5.split('  ')[0]
    except requests.ConnectionError:
        sg.popup_error('Connection error occurred! Exiting...')
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        httperror(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        generalconnerror(e)
        sys.exit(1)


def verify(truemd5):
    """Verifies a local set database file with a known md5 hash stored on GitHub

    :param str truemd5: The known md5 hash from GitHub
    :return: Whether or not the local hash matches the known hash
    :rtype:  bool
    """
    try:
        with open(setdbpath, 'rb') as f:
            data = f.read()
            returnedmd5 = hashlib.md5(data).hexdigest()
    except OSError:
        with open(setdbpath, 'w') as f:
            f.write("[]")
        return False
    return truemd5 == returnedmd5


def updatedb(beannoying=True):
    """Handles updating the set database with PySimpleGUI interactions

    :param bool beannoying: Whether or not to show a popup if the database is up to date
    """
    if not verify(fetchmd5()):
        result = sg.popup_yes_no('Database is not up to date. Download latest version?')
        if result == 'Yes':
            downloaddb()
            if not verify(fetchmd5()):
                sg.popup_error('Database is still not up to date, please update manually. https://github.com/jojojo8359/neonmob-set-db/blob/main/all-sets.json')
            else:
                sg.popup_ok('Database has been sucessfully updated.')
    else:
        if beannoying:
            sg.popup_ok('Database is up to date.')


def loadSetDB():
    """Loads the set database from a file and saves it into SETDB (global variable)

    """
    global SETDB
    try:
        with open(setdbpath, 'r') as f:
            SETDB = json.load(f)
    except OSError:
        with open(setdbpath, 'w') as f:
            f.write("[]")
        SETDB = []


def searchDB(query):
    """Given a query, searches the loaded set database for instances in the name of sets

    If the set database has not yet been loaded, this function will load the database
    :param str query: The substring query to search the database for
    :return: The list of matching results from the database
    :rtype: List[Dict[Union[str, int], Union[int, str, Dict[str, str]]]]
    """
    global SETDB
    if not SETDB:
        loadSetDB()
    filtered = list(filter(lambda series: query.lower() in series['name'].lower() or query.lower() in series['name_slug'].lower(), SETDB))
    # filtered = list(filter(lambda series: query.lower() in series['creator']['username'].lower() or query.lower() in series['creator']['name'].lower(), SETDB))
    # Use the above to search through creator names/usernames or just `series['id']` for set ids
    filtered.reverse()
    return filtered


# Settings handling


def loadSettings():
    """Loads custom user settings from a file, then updates global variables

    If no settings are saved, the default settings saved in this file are written into the settings file
    """
    global setdbpath, MAXRECENT, keepalivemins, AUTOUPDATE
    new = False
    try:
        with open('../settings.json', 'r') as f:
            saved = json.load(f)
            if saved != {}:
                setdbpath = saved['setdbpath']
                MAXRECENT = saved['maxrecent']
                keepalivemins = saved['keepalivemins']
                AUTOUPDATE = saved['autoupdate']
            else:
                new = True
    except OSError:
        saveSettings()
    except JSONDecodeError:
        saveSettings()
    if new:
        saveSettings()


def saveSettings():
    """Saves custom user settings to a file by reading global variables

    """
    global setdbpath, MAXRECENT, keepalivemins, AUTOUPDATE
    with open('../settings.json', 'w') as f:
        json.dump({'setdbpath': setdbpath, 'maxrecent': MAXRECENT, 'keepalivemins': keepalivemins, 'autoupdate': AUTOUPDATE}, f)


# History/Recent Handling


def loadRecent():
    """Loads the most recent sets that were searched for from a file and saves them into RECENT (global variable)

    """
    global RECENT, recentpath
    try:
        with open(recentpath, 'r') as f:
            RECENT = json.load(f)
    except OSError:
        saveRecent()
    except JSONDecodeError:
        saveRecent()


def saveRecent():
    """Saves the MAXRECENT most recent sets after truncating to a file

    """
    global RECENT, MAXRECENT, recentpath
    del RECENT[MAXRECENT:]
    with open(recentpath, 'w') as f:
        json.dump(RECENT, f)


# Cache Handling


def loadCards(setid):
    """Loads cached card list for a specified series

    :param int setid: The id of the set to load cards for
    :return: A list of cards in the set or int 0 if the proper file was not found
    :rtype: Union[List[Dict[str, Union[str, int]]], int]
    """
    if path.exists('cache/cards/' + str(setid) + '.json'):
        with open('cache/cards/' + str(setid) + '.json', 'r') as f:
            cards = json.load(f)
        return cards
    else:
        return 0


def saveCards(setid, cards):
    """Saves the card list for a specified series in cache

    :param int setid: The is of the set to save cards of
    :param List[Dict[str, Union[str, int]]] cards: A list of cards in the set
    """
    if not path.exists('../cache/'):
        os.mkdir('../cache/')
    if not path.exists('../cache/cards/'):
        os.mkdir('../cache/cards/')
    with open('cache/cards/' + str(setid) + '.json', 'w') as f:
        json.dump(cards, f)


def loadCache():
    """Loads the saved seeker and owner cache from their respective files

    """
    global SCACHE, OCACHE
    if not path.exists('../cache/'):
        os.mkdir('../cache/')
    if not path.exists('../cache/scache.json'):
        saveCache()
    if not path.exists('../cache/ocache.json'):
        saveCache()
    with open('../cache/scache.json', 'r') as f:
        SCACHE = json.load(f)
    with open('../cache/ocache.json', 'r') as f:
        OCACHE = json.load(f)


def saveCache():
    """Save seeker and owner caches to their respective files

    """
    global SCACHE, OCACHE
    with open('../cache/scache.json', 'w') as f:
        json.dump(SCACHE, f)
    with open('../cache/ocache.json', 'w') as f:
        json.dump(OCACHE, f)


def purgeCache():
    """Remove any entries from seeker and owner caches that have "expired" (based on the time limit)

    """
    global SCACHE, OCACHE
    loadCache()
    currentMillis = int(round(time.time() * 1000))
    for k in list(SCACHE.keys()):
        if currentMillis - SCACHE[k]['time'] >= (keepalivemins * 60 * 1000):
            del SCACHE[k]
    for k in list(OCACHE.keys()):
        if currentMillis - OCACHE[k]['time'] >= (keepalivemins * 60 * 1000):
            del OCACHE[k]
    saveCache()


def deleteCache():
    """Remove all entries from seeker and owner caches

    """
    with open('../cache/scache.json', 'w') as f:
        json.dump({}, f)
    with open('../cache/ocache.json', 'w') as f:
        json.dump({}, f)


# MAIN API/NETWORKING SECTION


def GetCards(setid, force=False):
    """Fetches a list of cards for any given series

    :param int setid: The series id to get cards from
    :param bool force: Whether or not to disregard cards stored in cache
    :return: A list of cards in the given set
    :rtype: List[Dict[str, Union[str, int]]]
    """
    cards = loadCards(setid)
    if cards != 0 and not force:
        print("Card found in cache")
        return cards

    set_url = "https://www.neonmob.com/api/setts/" + str(setid) + "/"
    data = requests.request('GET', set_url).json()
    set_name = data['name']
    # total = 0
    # for cat in range(len(data['core_stats'])):
    #     total += data['core_stats'][cat]['total']
    # for cat in range(len(data['special_stats'])):
    #     total += data['special_stats'][cat]['total']

    # print("\nGetting cards from series \"" + set_name + "\"...")
    cards = []
    raw = requests.request('GET', "https://www.neonmob.com/api/sets/" + str(setid) + "/piece-names")
    data = raw.json()
    for card in data:
        cards.append({'name': card['name'],
                      'rarity': card['rarity']['name'],
                      'id': card['id'],
                      'setName': set_name})
    saveCards(setid, cards)
    return cards


def GetSeekers(card, force=False):
    """Fetches a list of seekers for any given card

    :param Dict[str, Union[str, int]] card: The card to search for seekers of
    :param bool force: Whether or not to disregard non-expired users in the cache
    :return: A list of seekers of the specified card
    :rtype: List[Dict[str, Union[int, float, str, List[Dict[str, Union[str, int]]]]]
    """
    global SCACHE, SEARCHING

    purgeCache()

    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []

    currentMillis = int(round(time.time() * 1000))
    if str(card['id']) in SCACHE.keys() and not force:
        print("Card is in cache")
        if currentMillis - SCACHE[str(card['id'])]['time'] < (keepalivemins * 60 * 1000):
            print("Time is under 10 minutes")
            return SCACHE[str(card['id'])]['seekers']

    # print("\nGetting seekers of " + card['name'] + " [" + str(card['id']) + "]...")
    seekers = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/needers/?completion=desc&grade=desc&wishlisted=desc").json()
    total = data['count']
    i = 0
    canceled = False

    while True:
        if canceled:
            break
        nxt = data['next']
        for seeker in data['results']:
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
            if not sg.one_line_progress_meter("Fetching seekers...", i, total, "Getting seekers of " + card['name'] + " [" + str(card['id']) + "]...", orientation='h', key='-SEEKERBAR-'):
                canceled = True
                break
        if not nxt:
            break
        data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    if len(seekers) != total:
        SEARCHING = False
        return -1
    try:
        SCACHE.pop(str(card['id']))
    except KeyError:
        print("Card is not in cache")
    currentMillis = int(round(time.time() * 1000))
    SCACHE.update({card['id']: {'time': currentMillis, 'cardName': card['name'], 'setName': card['setName'], 'seekers': seekers}})
    saveCache()
    return seekers


def GetOwners(card, force=False):
    """Fetches a list of owners for any given card

    :param Dict[str, Union[str, int]] card: The card to search for owners of
    :param bool force: Whether or not to disregard non-expired users in the cache
    :return: A list of owners of the specified card
    :rtype: List[Dict[str, Union[int, float, str, List[Dict[str, Union[str, int]]]]]
    """
    global OCACHE, SEARCHING

    purgeCache()

    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []

    currentMillis = int(round(time.time() * 1000))
    if str(card['id']) in OCACHE.keys() and not force:
        print("Card is in cache")
        if currentMillis - OCACHE[str(card['id'])]['time'] < (keepalivemins * 60 * 1000):
            print("Time is under 10 minutes")
            return OCACHE[str(card['id'])]['owners']

    # print("\nGetting owners of " + card['name'] + " [" + str(card['id']) + "]...")
    owners = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/owners/?completion=asc&grade=desc&owned=desc").json()
    total = data['count']
    i = 0
    canceled = False

    while True:
        if canceled:
            break
        nxt = data['next']
        for owner in data['results']:
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
            if not sg.one_line_progress_meter('Fetching owners...', i, total, "Getting owners of " + card['name'] + " [" + str(card['id']) + "]...", orientation='h', key='-OWNERBAR-'):
                canceled = True
                break
        if not nxt:
            break
        data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    if len(owners) != total:
        SEARCHING = False
        return -1
    try:
        OCACHE.pop(str(card['id']))
    except KeyError:
        print("Card is not in cache")
    currentMillis = int(round(time.time() * 1000))
    OCACHE.update({card['id']: {'time': currentMillis, 'cardName': card['name'], 'setName': card['setName'], 'owners': owners}})
    saveCache()
    return owners


# DATA PROCESSING SECTION


def processSets(results):
    """Process set results to be displayed in the set selection window

    :param List[Dict[str, Union[int, str, Dict[str, str]]]] results: A list of raw set results
    :return: A list of processed results in table form
    :rtype: List[Union[str, int]]
    """
    rows = []
    for item in results:
        if item['edition_size'] == 'unlimited':
            char = '∞'
        else:
            char = 'LE'
        name = item['name']
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)

        rows.append([emoji_pattern.sub(r'', name), item['creator']['name'], char, item['id']])
    return rows


def processCards(results):
    """Process card results to be displayed in the card selection window

    :param List[Dict[str, Union[str, int]]] results: A list of raw card results
    :return: A list of processed results in table form
    :rtype: List[List[Union[str, int]]]
    """
    rows = []
    for item in results:
        rows.append([item['rarity'], item['name'], item['setName'], item['id']])
    return rows


def processResults(results):
    """Process trade search results to be displayed in the results window

    :param List[Dict[str, Union[int, str, float, List[Dict[str, Union[str, int]]]]]] results: A list of raw trade search results
    :return: A list of processed results in table form
    :rtype: List[List[Union[str, int]]]
    """
    rows = []
    for person in results:
        rows.append([person['name'], parseTraderGrade(person['trader_score']),
                     len(person['owns']), len(person['wants']), person['id']])
    return rows


def parseTraderGrade(grade):
    """Converts a decimal trader grade into a text representation (defined by NeonMob)

    :param float grade: The decimal trader grade to convert
    :return: The text representation of the given trader grade
    :rtype: str
    """
    grades = ['F', 'F+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
    return grades[int(grade)]


def combinePeople(nestedlist1, nestedlist2):
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


def getCommons(people, owned, want, mode='and', checkprintcount=False):
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


# GUI SECTION


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
        menu = sg.Menu([['&File', ['Settings', '---', 'Update Database', 'Purge Cache', '---', 'E&xit']]])
    else:
        menu = sg.Menu([['&File', ['Settings', '---', 'Update Database', 'Purge Cache', '---', 'E&xit']]],
                background_color='#FFFFFF', text_color='#000000')

    layout = [[menu],
              [sg.Frame(layout=frame1, title="Cards I'm seeking from someone else"), sg.Frame(layout=frame2, title="Cards I want to trade away")],
              [sg.Button('Search', key='-SEARCHBUTTON-'), sg.Checkbox('Force Refresh', default=False, key='-REFRESH-'),
               sg.Combo(['And', 'Or'], 'And', key='-MODE-', readonly=True), sg.Checkbox('2+ Prints', default=True, key='-PRINTS-')]]

    window = sg.Window('NeonMobMatcher v1.0.0', layout, finalize=True, resizable=True)
    # window.maximize()
    return window


def make_setwindow():
    """Builds the set selection window

    :return: Built window (finalized)
    :rtype: PySimpleGUI.Window
    """
    global RECENT, TARGET
    if not RECENT:
        loadRecent()
    if TARGET == 0:
        target_text = "Another Person Has:"
    else:
        target_text = "You Have:"
    layout = [[sg.Input(size=(30, 1), enable_events=True, key='-INPUT-', tooltip='Search for a set by name', focus=True)],
              [sg.Table(RECENT, num_rows=15, key='-SETTABLE-', headings=['Set Name', 'Author', ' ', 'id'],
                        col_widths=[30, 20, 3, 8], auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, False], bind_return_key=True)],
              [sg.Button('OK'), sg.Button('Cancel')]]
    window = sg.Window('Set Selection | ' + target_text, layout, finalize=True)
    return window


def make_cardwindow(setid):
    """Builds the card selection window

    :param int setid: The id of the set to show cards for
    :return: Built window (finalized)
    :rtype: PySimpleGUI.Window
    """
    global TARGET
    if TARGET == 0:
        target_text = "Another Person Has:"
    else:
        target_text = "You Have:"
    layout = [[sg.Table(defaultcards, num_rows=15, key='-CARDTABLE-',
                        headings=['Rarity', 'Card Name', 'Set Name', 'id'], col_widths=[10, 30, 30, 9],
                        auto_size_columns=False, justification='left', visible_column_map=[True, True, False, False],
                        right_click_menu=['&Right', ['Sort By Rarity', 'Sort By Name']], select_mode=sg.TABLE_SELECT_MODE_EXTENDED)],
              [sg.Button('OK'), sg.Button('Cancel'), sg.Button('Refresh'),
               sg.Combo(['Common', 'Uncommon', 'Rare', 'Very Rare', 'Extra Rare', 'Chase', 'Variant'], key='-RARITY-', readonly=True),
               sg.Button('Add All of Rarity')]]
    window = sg.Window('Card Selection | ' + target_text, layout, finalize=True)
    new_rows = processCards(GetCards(setid))
    window['-CARDTABLE-'].update(new_rows)
    return window


def make_resultwindow(results):
    """Builds the search results window

    :param List[Dict[str, Union[int, str, float, List[Dict[str, Union[int, str]]]]]] results: A list of raw trade search results
    :return: Built window (finalized)
    :rtype: PySimpleGUI.Window
    """
    table1 = [[sg.Table(defaultcards2, num_rows=10, key='-OWNTABLE-',
                        headings=['Rarity', 'Card Name', 'Set Name', 'Prints', 'id'], col_widths=[10, 20, 20, 5, 9],
                        auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, True, False],
                        right_click_menu=['&Right', ['Option 1', 'Option 2']], enable_events=True)]]

    table2 = [[sg.Table(defaultcards2, num_rows=10, key='-WANTTABLE-',
                        headings=['Rarity', 'Card Name', 'Set Name', 'Wishlisted', 'id'], col_widths=[10, 20, 20, 8, 9],
                        auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, True, False],
                        right_click_menu=['&Right', ['Option 1', 'Option 2']])]]

    frame1 = [[sg.Column(table1)]]
    frame2 = [[sg.Column(table2)]]

    layout = [[sg.Table(defaultpeople, num_rows=15, key='-PEOPLETABLE-',
                        headings=['Name', 'Grade', 'Have', 'Want', 'id'], col_widths=[20, 5, 5, 5, 9],
                        auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, True, False],
                        right_click_menu=['&Right', ['Option 1', 'Option 2']], enable_events=True)],
              [sg.Frame(layout=frame1, title="___ Has:", key='-OTHERFRAME-'),
               sg.Frame(layout=frame2, title="You Have:")],
              [sg.Button('OK'), sg.Button('Open User Profile'), sg.Text('', key='-PRINTNUMS-')]]
    window = sg.Window('Results', layout, finalize=True)
    new_rows = processResults(results)
    window['-PEOPLETABLE-'].update(new_rows)
    return window


def make_settingswindow():
    """Builds the settings window

    :return: Built window (finalized)
    :rtype: PySimpleGUI.Window
    """
    # Database
    # Cache
    # History

    column1 = sg.Column([[sg.Text('Set DB Path (must end in .json):'), sg.InputText(setdbpath, key='-SETDBPATH-')],
                         [sg.Checkbox('Auto-update DB on startup?', key='-AUTOUPDATE-', default=AUTOUPDATE)]])
    column2 = sg.Column([[sg.Text('Cache keep-alive time (minutes):'), sg.InputText(str(keepalivemins), key='-KEEPALIVE-')]])
    column3 = sg.Column([[sg.Text('Maximum recent sets to remember:'), sg.InputText(str(MAXRECENT), key='-MAXRECENT-')]])

    frame1 = [[column1]]
    frame2 = [[column2]]
    frame3 = [[column3]]

    layout = [[sg.Frame(layout=frame1, title='Database')],
              [sg.Frame(layout=frame2, title='Cache')],
              [sg.Frame(layout=frame3, title='History')],
              [sg.Button('OK'), sg.Button('Cancel')]]
    window = sg.Window('Settings', layout, finalize=True)
    return window


items1 = []
items2 = []
SETID = 0
RESULTS = []
SEARCHING = False


# MAIN EVENT LOOP


def main():
    global TARGET, SETID, RESULTS, RECENT, setdbpath, MAXRECENT, keepalivemins, AUTOUPDATE, SEARCHING
    loadSettings()
    window1, window2, window3, window4, settingswindow = make_mainwindow(), None, None, None, None
    updatedb(beannoying=False)  # Please don't be annoying on startup :)
    while True:
        window, event, values = sg.read_all_windows()
        print(event, values)

        if window == window1 and event in (sg.WIN_CLOSED, 'Exit'):  # Close the program if main window is closed or File -> Exit is selected
            break

        # Main window

        if event == 'Settings' and not SEARCHING:  # From File menu
            settingswindow = make_settingswindow()
            continue
        elif event == 'Update Database' and not SEARCHING:  # From File menu
            updatedb()
        elif event == 'Purge Cache' and not SEARCHING:  # From File menu
            if sg.popup_yes_no("Are you sure you want to purge the cache? Loading times will be significantly impacted.") == 'Yes':
                purgeCache()
                sg.popup("Cache successfully purged!")

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
                if settingswindow is not None:  # If the user is changing settings, close that window to begin the search
                    settingswindow.close()
                    settingswindow = None
                # print(items1)
                # print(items2)
                if len(items1) == 0 or len(items2) == 0:
                    sg.popup_error("Please add items to both lists")
                else:
                    canceled = False
                    owners = []
                    for card in items1:
                        carddict = {'name': card[1], 'rarity': card[0], 'id': card[3], 'setName': card[2]}
                        newowners = GetOwners(carddict, force=values['-REFRESH-'])
                        if newowners == -1:
                            canceled = True
                            break
                        else:
                            owners.append(newowners)
                    seekers = []
                    if not canceled:
                        for card in items2:
                            carddict = {'name': card[1], 'rarity': card[0], 'id': card[3], 'setName': card[2]}
                            newseekers = GetSeekers(carddict, force=values['-REFRESH-'])
                            if newseekers == -1:
                                canceled = True
                                break
                            else:
                                seekers.append(newseekers)
                    if canceled:
                        sg.popup("Search was canceled.")
                    else:
                        combined = combinePeople(owners, seekers)
                        filtered = getCommons(combined, [x[3] for x in items1], [x[3] for x in items2], mode=values['-MODE-'].lower(), checkprintcount=values['-PRINTS-'])
                        RESULTS = filtered
                        # print(filtered)
                        window4 = make_resultwindow(RESULTS)
                SEARCHING = False
                window['-SEARCHBUTTON-'].update(disabled=False)
                window['-REFRESH-'].update(disabled=False)
                window['-MODE-'].update(disabled=False)
                window['-PRINTS-'].update(disabled=False)
                continue

        # Left side (other person)

        if event == '-OTHERADD-' and not SEARCHING:  # Start searching for user-owned cards
            if window2 is not None:
                window2.ding()
                window2.bring_to_front()
            elif window3 is not None:
                window3.ding()
                window3.bring_to_front()
            else:
                TARGET = 0
                window2 = make_setwindow()
            continue
        elif event == '-OTHERREMOVE-' and not SEARCHING:  # Remove user-owned card from trade list
            try:
                items1.pop(values['-TABLE1-'][0])
            except IndexError:
                pass
            window1['-TABLE1-'].update(items1)
        elif event == '-OTHERCLEAR-' and not SEARCHING:  # Clear user-owned card list
            if sg.popup_yes_no("Really clear?") == 'Yes':
                items1.clear()
                window1['-TABLE1-'].update(items1)

        # Right side (you)

        elif event == '-YOUADD-' and not SEARCHING:  # Start searching for user-wanted cards
            if window2 is not None:
                window2.ding()
                window2.bring_to_front()
            elif window3 is not None:
                window3.ding()
                window3.bring_to_front()
            else:
                TARGET = 1
                window2 = make_setwindow()
            continue
        elif event == '-YOUREMOVE-' and not SEARCHING:  # Remove user-wanted cards from trade list
            try:
                items2.pop(values['-TABLE2-'][0])
            except IndexError:
                pass
            window1['-TABLE2-'].update(items2)
        elif event == '-YOUCLEAR-' and not SEARCHING:  # Clear user-wanted card list
            if sg.popup_yes_no("Really clear?") == 'Yes':
                items2.clear()
                window1['-TABLE2-'].update(items2)

        # Set window

        if window == window2 and event in (sg.WIN_CLOSED, 'Cancel'):  # Close the set selection window if it is closed or Exit is pressed
            window2.close()
            window2 = None
            continue

        if window == window2 and values['-INPUT-'] != '':  # Update search results when a character is typed in the search box
            search = values['-INPUT-']
            new_values = searchDB(search)
            new_rows = processSets(new_values)
            window['-SETTABLE-'].update(new_rows)
        elif window == window2:  # If nothing is in the search box, display recent sets
            if not RECENT:
                loadRecent()
            window['-SETTABLE-'].update(RECENT)

        if window == window2 and (event == 'OK' or event == '-SETTABLE-') and len(values['-SETTABLE-']):  # Move on to card selection if OK is pressed or a set is selected or double-clicked
            selected = window['-SETTABLE-'].get()[values['-SETTABLE-'][0]]
            if selected in RECENT:
                RECENT.remove(selected)
            RECENT.insert(0, selected)
            saveRecent()
            SETID = selected[3]
            window3 = make_cardwindow(SETID)
            window2.close()
            window2 = None
            continue

        # Card window

        if window == window3 and event in (sg.WIN_CLOSED, 'Cancel'):  # Close the card selection window if it is closed or Exit is pressed
            window3.close()
            window3 = None
            continue

        if window == window3 and event == 'Add All of Rarity' and values['-RARITY-'] != '':  # If 'Add All of Rarity' is pressed and a rarity is selected, add all cards of the selected rarity to the main window
            current_rows = window['-CARDTABLE-'].get()
            rarity_cards = []
            for row in current_rows:
                if row[0] == values['-RARITY-']:
                    rarity_cards.append(row)
            if TARGET == 0:
                items1.extend(rarity_cards)
                window1['-TABLE1-'].update(items1)
            else:
                items2.extend(rarity_cards)
                window1['-TABLE2-'].update(items2)
            window3.close()
            window3 = None
            continue
        elif window == window3 and event == 'OK' and len(values['-CARDTABLE-']):  # If OK is pressed and at least 1 card is selected, add the card(s) to the main window
            indexes = values['-CARDTABLE-']
            items = window['-CARDTABLE-'].get()
            selected = []
            for index in indexes:
                selected.append(items[index])
            if TARGET == 0:
                items1.extend(selected)
                window1['-TABLE1-'].update(items1)
            else:
                items2.extend(selected)
                window1['-TABLE2-'].update(items2)
            window3.close()
            window3 = None
            continue
        elif window == window3 and event == 'Refresh':  # Re-download card data and refresh the window when Refresh is pressed
            new_rows = processCards(GetCards(SETID, force=True))
            window['-CARDTABLE-'].update(new_rows)
        elif window == window3 and event == 'Sort By Rarity':  # Sorts the card list by rarity when the table is right-clicked
            current_rows = window['-CARDTABLE-'].get()
            new_rows = []
            for rarity in ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Extra Rare', 'Chase', 'Variant']:
                for row in current_rows:
                    if row[0] == rarity:
                        new_rows.append(row)
            window['-CARDTABLE-'].update(new_rows)
        elif window == window3 and event == 'Sort By Name':  # Sorts the card list by name when the table is right-clicked
            current_rows = window['-CARDTABLE-'].get()
            new_rows = sorted(current_rows, key=lambda rowx: rowx[1])
            window['-CARDTABLE-'].update(new_rows)

        # Result window

        if window == window4 and event in ('OK', sg.WIN_CLOSED):  # Close the result window if it is closed or OK is pressed
            window4.close()
            window4 = None
            continue
        if window == window4 and event == '-PEOPLETABLE-' and len(values['-PEOPLETABLE-']):  # Update the two bottom tables when a result from the top table is selected
            index = values['-PEOPLETABLE-'][0]
            owned = []
            # noinspection PyTypeChecker
            for ownedcard in RESULTS[index]['owns']:
                owned.append(
                    [ownedcard['rarity'], ownedcard['card_name'], ownedcard['set_name'], ownedcard['print_count'],
                     ownedcard['card_id']])
            wanted = []
            # noinspection PyTypeChecker
            for wantedcard in RESULTS[index]['wants']:
                wanted.append(
                    [wantedcard['rarity'], wantedcard['card_name'], wantedcard['set_name'], 'Yes' if wantedcard['wishlisted'] else 'No',
                     wantedcard['card_id']])
            window['-OWNTABLE-'].update(owned)
            window['-WANTTABLE-'].update(wanted)
            # noinspection PyTypeChecker
            window['-OTHERFRAME-'].update(value=RESULTS[index]['name'] + " Has:")
            window['-PRINTNUMS-'].update(value='')
        elif event == '-OWNTABLE-' and len(values['-OWNTABLE-']) and len(values['-PEOPLETABLE-']):  # Display print numbers when a card in the bottom left table is selected
            cardindex = values['-OWNTABLE-'][0]
            personindex = values['-PEOPLETABLE-'][0]
            # noinspection PyTypeChecker
            userid = RESULTS[personindex]['id']
            cardid = window['-OWNTABLE-'].get()[cardindex][4]
            data = requests.request('GET', 'https://www.neonmob.com/api/users/' + str(userid) + '/piece/' + str(cardid) + '/detail/').json()
            # print(data['refs'][data['payload'][1]]['prints'])
            prints = []
            for copy in data['refs'][data['payload'][1]]['prints']:
                prints.append(copy['print_num'])
            window['-PRINTNUMS-'].update(value='Print Numbers: ' + ', '.join(str(i) for i in prints))
        if window == window4 and event == 'Open User Profile' and len(values['-PEOPLETABLE-']):  # Open a user's profile when a user from the result list is selected and the button is pressed
            index = values['-PEOPLETABLE-'][0]
            # noinspection PyTypeChecker
            webbrowser.open_new_tab('https://www.neonmob.com/user/' + str(RESULTS[index]['id']))

        # Settings window

        if window == settingswindow and event == 'OK':  # Saves settings when OK is pressed
            setdbpath = values['-SETDBPATH-']
            AUTOUPDATE = bool(values['-AUTOUPDATE-'])
            keepalivemins = int(values['-KEEPALIVE-'])
            MAXRECENT = int(values['-MAXRECENT-'])
            saveSettings()
            sg.popup("Settings saved!")
            settingswindow.close()
            settingswindow = None
            continue
        elif window == settingswindow and event in ('Cancel', sg.WIN_CLOSED):  # Closes the settings window when it is closed or Cancel is pressed
            settingswindow.close()
            settingswindow = None
            continue

    # Make sure all other windows get closed when the program "shuts down" (breaks out of the main loop)
    window1.close()
    if window2 is not None:
        window2.close()
    if window3 is not None:
        window3.close()
    if window4 is not None:
        window4.close()
    if settingswindow is not None:
        settingswindow.close()


if __name__ == '__main__':
    main()
