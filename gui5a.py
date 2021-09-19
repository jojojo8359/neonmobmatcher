import PySimpleGUI as sg
import json

sg.theme('DarkGrey9')

setdbpath = "db.json"
SETDB = {}
IDS = []
NAMES = []


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


def processResults(results):
    global IDS, NAMES
    IDS = []
    NAMES = []
    for item in results:
        IDS.append(item['id'])
        NAMES.append(item['name'])


default = []

layout = [[sg.Input(size=(30, 1), enable_events=True, key='-INPUT-', tooltip='Search for a set by name', focus=True)],
          [sg.Listbox(default, size=(30, 15), key='-LIST-')],
          [sg.Button('OK'), sg.Button('Exit')]]

window = sg.Window('Listbox with Search', layout)

while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if values['-INPUT-'] != '':
        search = values['-INPUT-']
        new_values = searchDB(search)
        processResults(new_values)
        window['-LIST-'].update(NAMES)
    else:
        window['-LIST-'].update(default)

    if event == 'OK' and len(values['-LIST-']):
        index = NAMES.index(values['-LIST-'][0])
        sg.popup('Selected ', IDS[index])
# 22471 The Cabcuas
# 5682 Learn Your ABC's
window.close()
