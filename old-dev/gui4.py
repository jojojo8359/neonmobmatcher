import random
import PySimpleGUI as sg

sg.theme('DarkGrey9')

list1 = [[sg.Listbox(values=[], size=(30,5), key='-LIST1-', select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, font='Any 12', enable_events=True)]]
list2 = [[sg.Listbox(values=[], size=(30,5), key='-LIST2-', select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, font='Any 12', enable_events=True)]]

column1 = [[sg.Button('+', key='-OTHERADD-')],
           [sg.Button('-', key='-OTHERREMOVE-')]]
column2 = [[sg.Button('+', key='-YOUADD-')],
           [sg.Button('-', key='-YOUREMOVE-')]]

frame1 = [[sg.Column(list1), sg.Column(column1)],
          [sg.Text('Value: ', key='-OTHERVALUETEXT-')],
          [sg.Text('Index: ', key='-OTHERINDEXTEXT-')]]
frame2 = [[sg.Column(list2), sg.Column(column2)],
          [sg.Text('Value: ', key='-YOUVALUETEXT-')],
          [sg.Text('Index: ', key='-YOUINDEXTEXT-')]]

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
        items1.append(random.randint(0, 10))
        window['-LIST1-'].update(items1)
        window['-OTHERVALUETEXT-'].update('Value: ')
        window['-OTHERINDEXTEXT-'].update('Index: ')
    elif event == '-OTHERREMOVE-':
        try:
            items1.pop(window['-LIST1-'].get_indexes()[0])
        except IndexError:
            pass
        window['-LIST1-'].update(items1)

        try:
            index = window['-LIST1-'].get_indexes()[0]
            window['-OTHERVALUETEXT-'].update('Value: ' + str(items1[index]))
            window['-OTHERINDEXTEXT-'].update('Index: ' + str(index))
        except IndexError:
            window['-OTHERVALUETEXT-'].update('Value: ')
            window['-OTHERINDEXTEXT-'].update('Index: ')

    elif event == '-YOUADD-':
        items2.append(random.randint(0, 10))
        window['-LIST2-'].update(items2)
        window['-YOUVALUETEXT-'].update('Value: ')
        window['-YOUINDEXTEXT-'].update('Index: ')
    elif event == '-YOUREMOVE-':
        try:
            items2.pop(window['-LIST2-'].get_indexes()[0])
        except IndexError:
            pass
        window['-LIST2-'].update(items2)

        try:
            index = window['-LIST2-'].get_indexes()[0]  # for some reason this works on linux but not on windows... ???
            window['-YOUVALUETEXT-'].update('Value: ' + str(items2[index]))
            window['-YOUINDEXTEXT-'].update('Index: ' + str(index))
        except IndexError:
            window['-YOUVALUETEXT-'].update('Value: ')
            window['-YOUINDEXTEXT-'].update('Index: ')

    elif event == '-LIST1-':
        index = window['-LIST1-'].get_indexes()[0]
        window['-OTHERVALUETEXT-'].update('Value: ' + str(items1[index]))
        window['-OTHERINDEXTEXT-'].update('Index: ' + str(index))
    elif event == '-LIST2-':
        index = window['-LIST2-'].get_indexes()[0]
        window['-YOUVALUETEXT-'].update('Value: ' + str(items2[index]))
        window['-YOUINDEXTEXT-'].update('Index: ' + str(index))
    print(items1)
    print(items2)

window.close()
