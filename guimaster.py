import hashlib
import random
import sys
import traceback

import PySimpleGUI as sg
import json
import requests
from os import path
import time
import webbrowser

sg.theme('DarkGrey9')

setdbpath = "db.json"
SETDB = {}
TARGET = 0
AUTOUPDATE = True

recentpath = "recent.json"
RECENT = []
MAXRECENT = 30

SCACHE = {}
OCACHE = {}

keepalivemins = 10


def httperror(e):
    tb = traceback.format_exc()
    sg.Print(f'An HTTP exception occurred. Here is the info:', e, tb)
    sg.popup_error(f'AN HTTP EXCEPTION OCCURRED! Exiting...', e, tb)


def generalconnerror(e):
    tb = traceback.format_exc()
    sg.Print(f'An exception occurred. Here is the info:', e, tb)
    sg.popup_error(f'AN EXCEPTION OCCURRED! Exiting...', e, tb)


def fetchdb():
    try:
        r = requests.request('GET', 'https://raw.githubusercontent.com/jojojo8359/neonmob-set-db/main/all-sets.json')
        r.raise_for_status()
        db = r.json()
        return db
    except requests.ConnectionError as e:
        sg.popup_error('Connection error occurred! Exiting...')
        sys.exit(1)  # TODO: Rewrite error handling
    except requests.exceptions.HTTPError as e:
        httperror(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        generalconnerror(e)
        sys.exit(1)


def downloaddb():
    db = fetchdb()
    with open('db.json', 'w') as f:
        json.dump(db, f)


def fetchmd5():
    try:
        r = requests.request('GET', 'https://raw.githubusercontent.com/jojojo8359/neonmob-set-db/main/all-sets.md5')
        r.raise_for_status()
        md5 = r.text
        return md5.split('  ')[0]
    except requests.ConnectionError as e:
        sg.popup_error('Connection error occurred! Exiting...')
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        httperror(e)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        generalconnerror(e)
        sys.exit(1)


def verify(truemd5):
    filename = 'db.json'
    with open(filename, 'rb') as f:
        data = f.read()
        returnedmd5 = hashlib.md5(data).hexdigest()
    return truemd5 == returnedmd5


def updatedb(beannoying=True):
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


def loadSettings():
    global setdbpath, MAXRECENT, keepalivemins, AUTOUPDATE
    new = False
    with open('settings.json', 'r') as f:
        saved = json.load(f)
        if saved != {}:
            setdbpath = saved['setdbpath']
            MAXRECENT = saved['maxrecent']
            keepalivemins = saved['keepalivemins']
            AUTOUPDATE = saved['autoupdate']
        else:
            new = True
    if new:
        saveSettings()


def saveSettings():
    global setdbpath, MAXRECENT, keepalivemins, AUTOUPDATE
    with open('settings.json', 'w') as f:
        json.dump({'setdbpath': setdbpath, 'maxrecent': MAXRECENT, 'keepalivemins': keepalivemins, 'autoupdate': AUTOUPDATE}, f)


def loadRecent():
    global RECENT
    with open(recentpath, 'r') as f:
        RECENT = json.load(f)


def saveRecent():
    global RECENT
    del RECENT[MAXRECENT:]
    with open(recentpath, 'w') as f:
        json.dump(RECENT, f)


def loadSetDB():
    global SETDB
    with open(setdbpath, 'r') as f:
        SETDB = json.load(f)


def searchDB(query):
    global SETDB
    if SETDB == {}:
        loadSetDB()
    filtered = list(filter(lambda series: query.lower() in series['name'].lower() or query.lower() in series['name_slug'].lower(), SETDB))
    # filtered = list(filter(lambda series: query.lower() in series['creator']['username'].lower() or query.lower() in series['creator']['name'].lower(), SETDB))
    filtered.reverse()
    return filtered


def loadCards(setid):
    if path.exists('cache/cards/' + str(setid) + '.json'):
        with open('cache/cards/' + str(setid) + '.json', 'r') as f:
            cards = json.load(f)
        return cards
    else:
        return 0


def saveCards(setid, cards):
    with open('cache/cards/' + str(setid) + '.json', 'w') as f:
        json.dump(cards, f)


def loadCache():
    global SCACHE, OCACHE
    with open('cache/scache.json', 'r') as f:
        SCACHE = json.load(f)
    with open('cache/ocache.json', 'r') as f:
        OCACHE = json.load(f)


def purgeCache():
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
    with open('cache/scache.json', 'w') as f:
        json.dump({}, f)
    with open('cache/ocache.json', 'w') as f:
        json.dump({}, f)


def saveCache():
    global SCACHE, OCACHE
    with open('cache/scache.json', 'w') as f:
        json.dump(SCACHE, f)
    with open('cache/ocache.json', 'w') as f:
        json.dump(OCACHE, f)


def GetCards(setid, force=False):
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
    global SCACHE

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

    print("\nGetting seekers of " + card['name'] + " [" + str(card['id']) + "]...")
    seekers = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/needers/?completion=desc&grade=desc&wishlist=desc").json()
    total = data['count']
    i = 0

    while True:
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
            sg.one_line_progress_meter("Fetching seekers...", i, total, "Getting seekers of " + card['name'] + " [" + str(card['id']) + "]...", orientation='h')
        if not nxt:
            break
        data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    try:
        SCACHE.pop(str(card['id']))
    except KeyError:
        print("Card is not in cache")
    currentMillis = int(round(time.time() * 1000))
    SCACHE.update({card['id']: {'time': currentMillis, 'cardName': card['name'], 'setName': card['setName'], 'seekers': seekers}})
    saveCache()
    return seekers


def GetOwners(card, force=False):
    global OCACHE

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

    print("\nGetting owners of " + card['name'] + " [" + str(card['id']) + "]...")
    owners = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/owners/?completion=asc&grade=desc&owned=desc").json()
    total = data['count']
    i = 0

    while True:
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
            sg.one_line_progress_meter('Fetching owners...', i, total, "Getting owners of " + card['name'] + " [" + str(card['id']) + "]...", orientation='h')
        if not nxt:
            break
        data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    try:
        OCACHE.pop(str(card['id']))
    except KeyError:
        print("Card is not in cache")
    currentMillis = int(round(time.time() * 1000))
    OCACHE.update({card['id']: {'time': currentMillis, 'cardName': card['name'], 'setName': card['setName'], 'owners': owners}})
    saveCache()
    return owners


def processSets(results):
    rows = []
    for item in results:
        if item['edition_size'] == 'unlimited':
            char = '∞'
        else:
            char = 'LE'
        rows.append([item['name'], item['creator']['name'], char, item['id']])
    return rows


def processCards(results):
    rows = []
    for item in results:
        rows.append([item['rarity'], item['name'], item['setName'], item['id']])
    return rows


def parseTraderGrade(grade):
    grades = ['F', 'F+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
    return grades[int(grade)]


def processResults(results):
    rows = []
    for person in results:
        rows.append([person['name'], parseTraderGrade(person['trader_score']),
                     len(person['owns']), len(person['wants']), person['id']])
    return rows


def combinePeople(nestedlist1, nestedlist2):
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
    """
    people: list of people to search through
    owned: list of card ids to check
    want: list of card ids to check
    mode: 'and' or 'or'
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
            printcheck = False
            if len(person['owns']) == 0 or len(person['wants']) == 0:
                continue
            for ownedid in owned:
                cardcheck = False
                for ownedcard in person['owns']:
                    if checkprintcount and ownedcard['print_count'] < 2:
                        printcheck = True
                        break
                    elif ownedid == ownedcard['card_id']:
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
    # col_widths=[10, 30, 30, 9]
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

    layout = [[sg.Menu([['&File', ['Settings', '---', 'Update Database', 'Purge Cache', '---', 'E&xit']]], background_color='#FFFFFF', text_color='#000000')],
              [sg.Frame(layout=frame1, title="Other Person's Cards"), sg.Frame(layout=frame2, title="Your Cards")],
              [sg.Button('Search'), sg.Checkbox('Force Refresh', default=False, key='-REFRESH-'),
               sg.Combo(['And', 'Or'], 'And', key='-MODE-', readonly=True), sg.Checkbox('> 2 Prints', default=True, key='-PRINTS-')]]

    window = sg.Window('Table Test', layout, finalize=True)
    return window


def make_setwindow():
    global RECENT
    if not RECENT:
        loadRecent()
    layout = [[sg.Input(size=(30, 1), enable_events=True, key='-INPUT-', tooltip='Search for a set by name', focus=True)],
              [sg.Table(RECENT, num_rows=15, key='-SETTABLE-', headings=['Set Name', 'Author', ' ', 'id'],
                        col_widths=[30, 20, 3, 8], auto_size_columns=False, justification='left',
                        visible_column_map=[True, True, True, False], bind_return_key=True)],
              [sg.Button('OK'), sg.Button('Exit')]]
    window = sg.Window('Listbox with Search', layout, finalize=True)
    return window


def make_cardwindow(setid):
    layout = [[sg.Table(defaultcards, num_rows=15, key='-CARDTABLE-',
                        headings=['Rarity', 'Card Name', 'Set Name', 'id'], col_widths=[10, 30, 30, 9],
                        auto_size_columns=False, justification='left', visible_column_map=[True, True, False, False],
                        right_click_menu=['&Right', ['Sort By Rarity', 'Sort By Name']], select_mode=sg.TABLE_SELECT_MODE_EXTENDED)],
              [sg.Button('OK'), sg.Button('Exit'), sg.Button('Refresh'),
               sg.Combo(['Common', 'Uncommon', 'Rare', 'Very Rare', 'Extra Rare', 'Chase', 'Variant'], key='-RARITY-', readonly=True),
               sg.Button('Add All of Rarity')]]
    window = sg.Window('Card Selection', layout, finalize=True)
    new_rows = processCards(GetCards(setid))
    window['-CARDTABLE-'].update(new_rows)
    return window


def make_resultwindow(results):
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


def main():
    global TARGET, SETID, RESULTS, RECENT, setdbpath, MAXRECENT, keepalivemins, AUTOUPDATE
    loadSettings()
    window1, window2, window3, window4, settingswindow = make_mainwindow(), None, None, None, None
    updatedb(beannoying=False)
    while True:
        window, event, values = sg.read_all_windows()
        print(event, values)

        if window == window1 and event in (sg.WIN_CLOSED, 'Exit'):
            break

        # Main window

        if event == 'Settings':
            settingswindow = make_settingswindow()
            continue
        elif event == 'Update Database':
            updatedb()
        elif event == 'Purge Cache':
            if sg.popup_yes_no("Are you sure you want to purge the cache? Loading times will be significantly impacted.") == 'Yes':
                purgeCache()
                sg.popup("Cache successfully purged!")

        if event == 'Search':
            print(items1)
            print(items2)
            if len(items1) == 0 or len(items2) == 0:
                sg.popup_error("Please add items to both lists")
            else:
                owners = []
                for card in items1:
                    carddict = {'name': card[1], 'rarity': card[0], 'id': card[3], 'setName': card[2]}
                    newowners = GetOwners(carddict, force=values['-REFRESH-'])
                    owners.append(newowners)
                seekers = []
                for card in items2:
                    carddict = {'name': card[1], 'rarity': card[0], 'id': card[3], 'setName': card[2]}
                    newseekers = GetSeekers(carddict, force=values['-REFRESH-'])
                    seekers.append(newseekers)
                combined = combinePeople(owners, seekers)
                filtered = getCommons(combined, [x[3] for x in items1], [x[3] for x in items2], mode=values['-MODE-'].lower(), checkprintcount=values['-PRINTS-'])
                RESULTS = filtered
                # print(filtered)
                window4 = make_resultwindow(RESULTS)
                continue

        # Left side (other person)

        if event == '-OTHERADD-' and not window2:
            TARGET = 0
            window2 = make_setwindow()
            continue
        elif event == '-OTHERREMOVE-':
            try:
                items1.pop(values['-TABLE1-'][0])
            except IndexError:
                pass
            window1['-TABLE1-'].update(items1)
        elif event == '-OTHERCLEAR-':
            if sg.popup_yes_no("Really clear?") == 'Yes':
                items1.clear()
                window1['-TABLE1-'].update(items1)

        # Right side (you)

        elif event == '-YOUADD-' and not window2:
            TARGET = 1
            window2 = make_setwindow()
            continue
        elif event == '-YOUREMOVE-':
            try:
                items2.pop(values['-TABLE2-'][0])
            except IndexError:
                pass
            window1['-TABLE2-'].update(items2)
        elif event == '-YOUCLEAR-':
            if sg.popup_yes_no("Really clear?") == 'Yes':
                items2.clear()
                window1['-TABLE1-'].update(items2)

        # Set window

        if window == window2 and event in (sg.WIN_CLOSED, 'Exit'):
            window2.close()
            window2 = None
            continue

        if window == window2 and values['-INPUT-'] != '':
            search = values['-INPUT-']
            new_values = searchDB(search)
            new_rows = processSets(new_values)
            window['-SETTABLE-'].update(new_rows)
        elif window == window2:
            if not RECENT:
                loadRecent()
            window['-SETTABLE-'].update(RECENT)

        if window == window2 and (event == 'OK' or event == '-SETTABLE-') and len(values['-SETTABLE-']):
            # print(window['-SETTABLE-'].get())
            selected = window['-SETTABLE-'].get()[values['-SETTABLE-'][0]]
            if selected in RECENT:
                RECENT.remove(selected)
            RECENT.insert(0, selected)
            saveRecent()
            SETID = selected[3]
            # sg.popup('Selected:', selected[0] + ' by ' + selected[1] + ' (' + str(selected[3]) + ')')
            window3 = make_cardwindow(SETID)
            window2.close()
            window2 = None
            continue

        # Card window

        if window == window3 and event in (sg.WIN_CLOSED, 'Exit'):
            window3.close()
            window3 = None
            continue

        if window == window3 and event == 'Add All of Rarity' and values['-RARITY-'] != '':
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
        elif window == window3 and event == 'OK' and len(values['-CARDTABLE-']):
            indexes = values['-CARDTABLE-']
            items = window['-CARDTABLE-'].get()
            selected = []
            for index in indexes:
                selected.append(items[index])
            if TARGET == 0:
                items1.extend(selected)
                window1['-TABLE1-'].update(items1)
                # window1['-TABLE1-'].expand(expand_x=True, expand_row=True)
            else:
                items2.extend(selected)
                window1['-TABLE2-'].update(items2)
            window3.close()
            window3 = None
            continue
        elif window == window3 and event == 'Refresh':
            new_rows = processCards(GetCards(SETID, force=True))
            window['-CARDTABLE-'].update(new_rows)
        elif window == window3 and event == 'Sort By Rarity':
            current_rows = window['-CARDTABLE-'].get()
            new_rows = []
            for rarity in ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Extra Rare', 'Chase', 'Variant']:
                for row in current_rows:
                    if row[0] == rarity:
                        new_rows.append(row)
            window['-CARDTABLE-'].update(new_rows)
        elif window == window3 and event == 'Sort By Name':
            current_rows = window['-CARDTABLE-'].get()
            new_rows = sorted(current_rows, key=lambda card: card[1])
            window['-CARDTABLE-'].update(new_rows)

        # Result window

        if window == window4 and event in ('OK', sg.WIN_CLOSED):
            window4.close()
            window4 = None
            continue
        if window == window4 and event == '-PEOPLETABLE-' and len(values['-PEOPLETABLE-']):
            index = values['-PEOPLETABLE-'][0]
            owned = []
            for ownedcard in RESULTS[index]['owns']:
                owned.append(
                    [ownedcard['rarity'], ownedcard['card_name'], ownedcard['set_name'], ownedcard['print_count'],
                     ownedcard['card_id']])
            wanted = []
            for wantedcard in RESULTS[index]['wants']:
                wanted.append(
                    [wantedcard['rarity'], wantedcard['card_name'], wantedcard['set_name'], 'Yes' if wantedcard['wishlisted'] else 'No',
                     wantedcard['card_id']])
            window['-OWNTABLE-'].update(owned)
            window['-WANTTABLE-'].update(wanted)
            window['-OTHERFRAME-'].update(value=RESULTS[index]['name'] + " Has:")
            window['-PRINTNUMS-'].update(value='')
        elif event == '-OWNTABLE-' and len(values['-OWNTABLE-']) and len(values['-PEOPLETABLE-']):
            cardindex = values['-OWNTABLE-'][0]
            personindex = values['-PEOPLETABLE-'][0]
            userid = RESULTS[personindex]['id']
            cardid = window['-OWNTABLE-'].get()[cardindex][4]
            data = requests.request('GET', 'https://www.neonmob.com/api/users/' + str(userid) + '/piece/' + str(cardid) + '/detail/').json()
            # print(data['refs'][data['payload'][1]]['prints'])
            prints = []
            for copy in data['refs'][data['payload'][1]]['prints']:
                prints.append(copy['print_num'])
            window['-PRINTNUMS-'].update(value='Print Numbers: ' + ', '.join(str(i) for i in prints))
        if window == window4 and event == 'Open User Profile' and len(values['-PEOPLETABLE-']):
            index = values['-PEOPLETABLE-'][0]
            webbrowser.open_new_tab('https://www.neonmob.com/user/' + str(RESULTS[index]['id']))

        # Settings window

        if window == settingswindow and event == 'OK':
            setdbpath = values['-SETDBPATH-']
            AUTOUPDATE = values['-AUTOUPDATE-']
            keepalivemins = values['-KEEPALIVE-']
            MAXRECENT = values['-MAXRECENT-']
            saveSettings()
            sg.popup("Settings saved!")
            settingswindow.close()
            settingswindow = None
            continue
        elif window == settingswindow and event in ('Cancel', sg.WIN_CLOSED):
            settingswindow.close()
            settingswindow = None
            continue

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
