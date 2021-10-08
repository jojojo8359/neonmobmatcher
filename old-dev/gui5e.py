import PySimpleGUI as sg
import requests

sg.theme('DarkGrey9')

defaultcards = [['', '', '', '']]
defaultpeople = [['', '', '', '']]

table1 = [[sg.Table(defaultcards, num_rows=10, key='-OWNTABLE-',
                    headings=['Rarity', 'Card Name', 'Set Name', 'Prints', 'id'], col_widths=[10, 20, 20, 5, 9],
                    auto_size_columns=False, justification='left', visible_column_map=[True, True, True, True, False],
                    right_click_menu=['&Right', ['Option 1', 'Option 2']], enable_events=True)]]

table2 = [[sg.Table(defaultcards, num_rows=10, key='-WANTTABLE-',
                    headings=['Rarity', 'Card Name', 'Set Name', 'Wishlisted', 'id'], col_widths=[10, 20, 20, 8, 9],
                    auto_size_columns=False, justification='left', visible_column_map=[True, True, True, True, False],
                    right_click_menu=['&Right', ['Option 1', 'Option 2']])]]

frame1 = [[sg.Column(table1)]]
frame2 = [[sg.Column(table2)]]

layout = [[sg.Table(defaultpeople, num_rows=15, key='-PEOPLETABLE-',
                    headings=['Name', 'Grade', 'Have', 'Want', 'id'], col_widths=[20, 5, 5, 5, 9],
                    auto_size_columns=False, justification='left', visible_column_map=[True, True, True, True, False],
                    right_click_menu=['&Right', ['Option 1', 'Option 2']], enable_events=True)],
          [sg.Frame(layout=frame1, title="___ Has:", key='-OTHERFRAME-'), sg.Frame(layout=frame2, title="You Have:")],
          [sg.Button('OK'), sg.Button('Exit'), sg.Text('', key='-PRINTNUMS-')]]

window = sg.Window('Results', layout)


def parseTraderGrade(grade):
    grades = ['F', 'F+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
    return grades[int(grade)]


results = [
    {'id': 62508, 'name': 'Cate', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 4, 'total_specials': 6, 'specials': 1, 'percentage': 28}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 1, 'percentage': 28}]}, {'id': 204300, 'name': 'STARLOG', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 3, 'total_specials': 6, 'specials': 0, 'percentage': 25}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 0, 'percentage': 25}]}, {'id': 246612, 'name': 'Leah', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 3, 'total_specials': 6, 'specials': 1, 'percentage': 43}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 1, 'percentage': 43}]}, {'id': 225653, 'name': 'A Neon YardSale', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 2, 'total_specials': 6, 'specials': 1, 'percentage': 12}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 1, 'percentage': 12}]}, {'id': 113726, 'name': 'Randy Kelsey', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 2, 'total_specials': 6, 'specials': 2, 'percentage': 21}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 2, 'percentage': 21}]}, {'id': 243433, 'name': 'Texanspaniard', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 2, 'total_specials': 6, 'specials': 1, 'percentage': 21}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 1, 'percentage': 21}]}, {'id': 247717, 'name': 'Stormy Holton', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 2, 'total_specials': 6, 'specials': 1, 'percentage': 21}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 1, 'percentage': 21}]}, {'id': 233434, 'name': 'K Darby', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 2, 'total_specials': 6, 'specials': 2, 'percentage': 28}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 2, 'percentage': 28}]}, {'id': 250003, 'name': 'Panthyrr', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 2, 'total_specials': 6, 'specials': 2, 'percentage': 37}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 2, 'percentage': 37}]}, {'id': 249894, 'name': 'Aimee Cozza', 'trader_score': 13.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 2, 'total_specials': 6, 'specials': 1, 'percentage': 40}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 1, 'percentage': 40}]}, {'id': 97776, 'name': 'Rabrugger', 'trader_score': 12.0, 'owns': [{'card_id': 207486, 'card_name': 'Freedom', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'print_count': 2, 'total_specials': 6, 'specials': 0, 'percentage': 40}], 'wants': [{'card_id': 207487, 'card_name': 'Lying', 'set_name': 'Wicked Mind', 'rarity': 'Common', 'wishlisted': 0, 'total_specials': 6, 'specials': 0, 'percentage': 40}]}]

people = []

while True:
    event, values = window.read()
    print(event, values)

    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'OK':
        for person in results:
            people.append([person['name'], parseTraderGrade(person['trader_score']), len(person['owns']), len(person['wants']), person['id']])
        window['-PEOPLETABLE-'].update(people)
    elif event == '-PEOPLETABLE-' and len(values['-PEOPLETABLE-']):
        index = values['-PEOPLETABLE-'][0]
        owned = []
        for ownedcard in results[index]['owns']:
            owned.append([ownedcard['rarity'], ownedcard['card_name'], ownedcard['set_name'], ownedcard['print_count'], ownedcard['card_id']])
        wanted = []
        for wantedcard in results[index]['wants']:
            wanted.append([wantedcard['rarity'], wantedcard['card_name'], wantedcard['set_name'], wantedcard['wishlisted'], wantedcard['card_id']])
        window['-OWNTABLE-'].update(owned)
        window['-WANTTABLE-'].update(wanted)
        window['-OTHERFRAME-'].update(value=results[index]['name'] + " Has:")
        window['-PRINTNUMS-'].update(value='')
    elif event == '-OWNTABLE-' and len(values['-OWNTABLE-']) and len(values['-PEOPLETABLE-']):
        cardindex = values['-OWNTABLE-'][0]
        personindex = values['-PEOPLETABLE-'][0]
        userid = results[personindex]['id']
        cardid = window['-OWNTABLE-'].get()[cardindex][4]
        data = requests.request('GET', 'https://www.neonmob.com/api/users/' + str(userid) + '/piece/' + str(cardid) + '/detail/').json()
        print(data['refs'][data['payload'][1]]['prints'])
        prints = []
        for copy in data['refs'][data['payload'][1]]['prints']:
            prints.append(copy['print_num'])
        window['-PRINTNUMS-'].update(value='Print Numbers: ' + ', '.join(str(i) for i in prints))


window.close()
