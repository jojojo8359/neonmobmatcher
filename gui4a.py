import random
import PySimpleGUI as sg

sg.theme('DarkGrey9')

default = [['', '', '', '']]

table1 = [[sg.Table(default, num_rows=5, key='-TABLE1-', headings=['Set Name', 'Author', ' ', 'id'], col_widths=[30, 20, 3, 8], auto_size_columns=False, justification='left', visible_column_map=[True, True, True, False])]]
table2 = [[sg.Table(default, num_rows=5, key='-TABLE2-', headings=['Set Name', 'Author', ' ', 'id'], col_widths=[30, 20, 3, 8], auto_size_columns=False, justification='left', visible_column_map=[True, True, True, False])]]

column1 = [[sg.Button('+', key='-OTHERADD-')],
           [sg.Button('-', key='-OTHERREMOVE-')]]
column2 = [[sg.Button('+', key='-YOUADD-')],
           [sg.Button('-', key='-YOUREMOVE-')]]

frame1 = [[sg.Column(table1), sg.Column(column1)]]
frame2 = [[sg.Column(table2), sg.Column(column2)]]

layout = [[sg.Frame(layout=frame1, title="Other Person's Cards"), sg.Frame(layout=frame2, title="Your Cards")],
          [sg.Button('Exit')]]

window = sg.Window('Table Test', layout)

items1 = []
items2 = []

while True:
    event, values = window.read()
    print(event, values)

    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == '-OTHERADD-':
        items1.append([[random.randint(0, 10)], [random.randint(0, 10)], [random.randint(0, 10)], [random.randint(0, 10)]])
        window['-TABLE1-'].update(items1)
    elif event == '-OTHERREMOVE-':
        try:
            items1.pop(values['-TABLE1-'][0])
        except IndexError:
            pass
        window['-TABLE1-'].update(items1)

    elif event == '-YOUADD-':
        items2.append([[random.randint(0, 10)], [random.randint(0, 10)], [random.randint(0, 10)], [random.randint(0, 10)]])
        window['-TABLE2-'].update(items2)

    elif event == '-YOUREMOVE-':
        try:
            items2.pop(values['-TABLE2-'][0])
        except IndexError:
            pass
        window['-TABLE2-'].update(items2)

    print(items1)
    print(items2)

window.close()
