import PySimpleGUI as sg
import json
from os import path
import requests

sg.theme('DarkGrey9')


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


def processCards(results):
    rows = []
    for item in results:
        rows.append([item['rarity'], item['name'], item['setName'], item['id']])
    return rows


defaultcards = [['', '', '']]

setid = int(sg.popup_get_text('Enter a series id'))

layout = [[sg.Table(defaultcards, num_rows=15, key='-CARDTABLE-', headings=['Rarity', 'Card Name', 'Set Name', 'id'], col_widths=[10, 30, 30, 9], auto_size_columns=False, justification='left', visible_column_map=[True, True, False, False], right_click_menu=['&Right', ['Sort By Rarity', 'Sort By Name']])],
          [sg.Button('OK'), sg.Button('Exit'), sg.Button('Refresh')]]

window = sg.Window('Card Selection', layout, finalize=True)

new_rows = processCards(GetCards(setid))
window['-CARDTABLE-'].update(new_rows)

while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    elif event == 'Refresh':
        new_rows = processCards(GetCards(setid, force=True))
        window['-CARDTABLE-'].update(new_rows)

    elif event == 'Sort By Rarity':
        current_rows = window['-CARDTABLE-'].get()
        new_rows = []
        for rarity in ['Common', 'Uncommon', 'Rare', 'Very Rare', 'Extra Rare', 'Chase', 'Variant']:
            for row in current_rows:
                if row[0] == rarity:
                    new_rows.append(row)
        window['-CARDTABLE-'].update(new_rows)
    elif event == 'Sort By Name':
        current_rows = window['-CARDTABLE-'].get()
        new_rows = sorted(current_rows, key=lambda card: card[1])
        window['-CARDTABLE-'].update(new_rows)

window.close()
