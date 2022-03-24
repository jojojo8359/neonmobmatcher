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
    # if not RECENT:
    #     loadRecent()
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
    # new_rows = processCards(GetCards(setid))
    # window['-CARDTABLE-'].update(new_rows)
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
    # new_rows = processResults(results)
    # window['-PEOPLETABLE-'].update(new_rows)
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


def main():
    global TARGET, SETID, RESULTS, RECENT, setdbpath, MAXRECENT, keepalivemins, AUTOUPDATE, SEARCHING
    window1, window2, window3, window4, settingswindow = make_mainwindow(), None, None, None, None
    while True:
        window, event, values = sg.read_all_windows()

        if event in (sg.WIN_CLOSED, 'Exit'):
            if window == window1:
                break
            elif window == window2:
                window2.close()
                window2 = None
            elif window == window3:
                window3.close()
                window3 = None
            elif window == window4:
                window4.close()
                window4 = None
            elif window == settingswindow:
                settingswindow.close()
                window5 = None

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

        if event == '-UPDATESETS-':
            window2['-SETTABLE-'].update(values['-UPDATESETS-'])

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
