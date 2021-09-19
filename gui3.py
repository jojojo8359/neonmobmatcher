import PySimpleGUI as sg

sg.theme('DarkGrey9')

data = [['foo', 'bar']]

layout = [[sg.Table(expand_x=True,
                    auto_size_columns=True,
                    num_rows=10,
                    justification='left',
                    key='-TABLE-',
                    row_height=35,
                    values=data,
                    headings=['Name', 'Author'])],
          [sg.Button('Stuff'), sg.Button('Select'), sg.Button('Exit')]]

window = sg.Window('Table Test', layout)

while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'Stuff':
        data.append(['asdf', 'Joel'])
        window['-TABLE-'].update(values=data)
    elif event == 'Select':
        print(data[values['-TABLE-'][0]])


window.close()
