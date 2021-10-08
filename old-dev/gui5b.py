import PySimpleGUI as sg
import json

sg.theme('DarkGrey9')

setdbpath = "db.json"
SETDB = {}


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
    rows = []
    for item in results:
        if item['edition_size'] == 'unlimited':
            char = '∞'
        else:
            char = 'LE'
        rows.append([item['name'], item['creator']['name'], char, item['id']])
    return rows


default = [['', '', '', '']]

layout = [[sg.Input(size=(30, 1), enable_events=True, key='-INPUT-', tooltip='Search for a set by name', focus=True)],
          [sg.Table(default, num_rows=15, key='-TABLE-', headings=['Set Name', 'Author', ' ', 'id'], col_widths=[30, 20, 3, 8], auto_size_columns=False, justification='left', visible_column_map=[True, True, True, False])],
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
        new_rows = processResults(new_values)
        window['-TABLE-'].update(new_rows)
    else:
        window['-TABLE-'].update(default)

    if event == 'OK' and len(values['-TABLE-']):
        print(window['-TABLE-'].get())
        selected = window['-TABLE-'].get()[values['-TABLE-'][0]]
        sg.popup('Selected:', selected[0] + ' by ' + selected[1] + ' (' + str(selected[3]) + ')')

window.close()
