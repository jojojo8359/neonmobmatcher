import traceback

import PySimpleGUI as sg
import requests
import json
import hashlib
import sys


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
        sys.exit(1)
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


def updatedb():
    if not verify(fetchmd5()):
        # print("Database is not up to date, downloading newest version...")
        result = sg.popup_yes_no('Database is not up to date. Download latest version?')
        if result == 'Yes':
            downloaddb()
            if not verify(fetchmd5()):
                # print("Database is still not up to date, please update manually. https://github.com/jojojo8359/neonmob-set-db/blob/main/all-sets.json")
                sg.popup_error('Database is still not up to date, please update manually. https://github.com/jojojo8359/neonmob-set-db/blob/main/all-sets.json')
            else:
                # print("Database has been sucessfully updated.")
                sg.popup_ok('Database has been sucessfully updated.')
    else:
        # print("Database is up to date.")
        sg.popup_ok('Database is up to date.')


sg.theme('DarkGrey9')
updatedb()
layout = [[sg.Text('Just a normal window')]]

window = sg.Window('Table Test', layout)

while True:
    event, values = window.read()
    print(event, values)
    if event in (sg.WIN_CLOSED, 'Exit'):
        break

window.close()