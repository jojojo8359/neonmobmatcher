#!/usr/bin/python3

# ****************************************************************************
# NeonMob Trade Matcher Tool
# Version: 0.4.1
# ****************************************************************************
# Copyright (c) 2021 Joel Keaton
# All rights reserved.
# ****************************************************************************

import sys
import tkinter as tk

if sys.platform.startswith('darwin'):
    import tkmacosx as tkx
import requests


# from conditional import conditional


class ScrolledText(tk.Frame):
    """ A class for combining a Tk Text object with a Scrollbar object.
    """

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack(expand=tk.YES, fill=tk.BOTH)
        self.MakeWidgets()

    def MakeWidgets(self):
        sbar = tk.Scrollbar(master=self)
        if sys.platform.startswith('darwin'):
            text = tk.Text(master=self, relief=tk.SUNKEN, width=120,
                           highlightbackground="black")
        else:
            text = tk.Text(master=self, relief=tk.SUNKEN, width=120)
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.text = text

    def ClearText(self):
        # Clear all of the text in the text box.
        self.text.delete("1.0", tk.END)

    def AppendText(self, text=""):
        # Append the supplied text, then scroll to the bottom.
        self.text.insert(tk.END, text)
        self.text.see("end")


class MatcherGui:
    """ The GUI class for the NeonMob Matcher application class.
    """

    def __init__(self, app):
        self.nm_app = app
        self.window = tk.Tk()
        self.window.title("NeonMob Matcher")
        self.MakeWidgets()

    def MakeWidgets(self):
        self.frame_1 = tk.Frame(master=self.window)
        self.label_1 = tk.Label(master=self.frame_1, text="Have Set ID:")
        self.entry_1 = tk.Entry(master=self.frame_1, width=40)
        self.label_1.grid(row=0, column=0, sticky="w")
        self.entry_1.grid(row=0, column=1, sticky="w")

        self.frame_2 = tk.Frame(master=self.window)
        self.label_2 = tk.Label(master=self.frame_2, text="Have Name:")
        self.entry_2 = tk.Entry(master=self.frame_2, width=40)
        self.label_2.grid(row=0, column=0, sticky="w")
        self.entry_2.grid(row=0, column=1, sticky="w")

        self.frame_3 = tk.Frame(master=self.window)
        self.label_3 = tk.Label(master=self.frame_3, text="Want Set ID:")
        self.entry_3 = tk.Entry(master=self.frame_3, width=40)
        self.label_3.grid(row=0, column=0, sticky="w")
        self.entry_3.grid(row=0, column=1, sticky="w")

        self.frame_4 = tk.Frame(master=self.window)
        self.label_4 = tk.Label(master=self.frame_4, text="Want Name:")
        self.entry_4 = tk.Entry(master=self.frame_4, width=40)
        self.label_4.grid(row=0, column=0, sticky="w")
        self.entry_4.grid(row=0, column=1, sticky="w")

        self.frame_5 = tk.Frame(master=self.window)
        if sys.platform.startswith('darwin'):
            self.button_submit = tkx.Button(master=self.frame_5,
                                            text="Submit",
                                            bg='white',
                                            fg='black',
                                            command=self.SubmitQuery)
            self.button_quit = tkx.Button(master=self.frame_5,
                                          text="Quit",
                                          bg='white', fg='black',
                                          command=self.QuitProg)
        else:
            self.button_submit = tk.Button(master=self.frame_5,
                                           text="Submit",
                                           command=self.SubmitQuery)
            self.button_quit = tk.Button(master=self.frame_5,
                                         text="Quit",
                                         command=self.QuitProg)
        self.button_submit.grid(row=0, column=0, sticky="w")
        self.button_quit.grid(row=0, column=1, sticky="w")

        self.frame_6 = tk.Frame(master=self.window)
        self.text_box = ScrolledText(master=self.frame_6)

        # Lay out the frames using the grid layout manager.
        self.frame_1.grid(row=0, column=0, padx=5, pady=5)
        self.frame_2.grid(row=1, column=0, padx=5, pady=5)
        self.frame_3.grid(row=2, column=0, padx=5, pady=5)
        self.frame_4.grid(row=3, column=0, padx=5, pady=5)
        self.frame_5.grid(row=4, column=0, padx=5, pady=5)
        self.frame_6.grid(row=5, column=0, padx=5, pady=5)

        # Stop window resizing.
        self.window.resizable(False, False)

    def RunGui(self):
        self.window.mainloop()

    def Clear(self):
        self.text_box.ClearText()
        if sys.platform.startswith('darwin'):
            self.window.update()
        else:
            self.window.update_idletasks()

    def Print(self, text):
        self.text_box.AppendText(text)
        if sys.platform.startswith('darwin'):
            self.window.update()
        else:
            self.window.update_idletasks()

    def SubmitQuery(self):
        # Get the entry text.
        have_setid_str = self.entry_1.get()
        have_name = self.entry_2.get()
        want_setid_str = self.entry_3.get()
        want_name = self.entry_4.get()

        # Clear the output text box.
        self.Clear()

        # Validate the set IDs.
        try:
            have_setid = int(have_setid_str)
        except ValueError as ve:
            self.Print("You entered {}, which is not an integer.\n".format(
                have_setid_str))
            return

        try:
            want_setid = int(want_setid_str)
        except ValueError as ve:
            self.Print("You entered {}, which is not an integer.\n".format(
                want_setid_str))
            return

        # Call the application with the input.
        self.nm_app.DoLookup(have_setid, have_name, want_setid, want_name)

    def QuitProg(self):
        sys.exit()


class NeonMobMatcher:
    """ The class for the NeonMob Matcher application.
    """

    def __init__(self):
        self.grades = ['F', 'F+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B',
                       'B+', 'A-', 'A', 'A+']

    def SetGui(self, g):
        self.gui = g

    def DoLookup(self, have_setid, have_name, want_setid, want_name):
        self.gui.Clear()

        if have_setid == want_setid:
            shared_series_cards = self.GetCards(have_setid)
            seekers = self.GetSeekers(self.GetCardByName(
                shared_series_cards, have_name))
            owners = []
            if len(seekers) != 0:
                owners = self.GetOwners(self.GetCardByName(
                    shared_series_cards, want_name))
        else:
            seekers = self.GetSeekers(self.GetCardByName(
                self.GetCards(have_setid), have_name))
            owners = []
            if len(seekers) != 0:
                owners = self.GetOwners(self.GetCardByName(
                    self.GetCards(want_setid), want_name))

        commons = self.FindCommonTraders(seekers, owners)
        self.ParseTraders(commons)

    def GetSeekers(self, card, showBar=False):
        if card['id'] == -1:
            self.gui.Print("\n\nCouldn't find card " + card['name'] + " in set " + card['setName'])
            return []
        self.gui.Print("\n\nGetting seekers of " + card['name'] + " [" + str(card['id']) + "]...\n. ")
        seekers = []
        data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/needers/?completion=desc&grade=desc&wishlisted=desc").json()
        # total = data['count']

        # with conditional(showBar, alive_bar(total, bar='smooth', spinner='dots_recur')) as bar:
        while True:
            nxt = data['next']
            for seeker in data['results']:
                seekers.append({'id': seeker['id'],
                                'name': seeker['name'],
                                'trader_score': seeker['trader_score'],
                                'wishlisted': seeker['wishlisted'],
                                'needs_special_piece_count': seeker['special_piece_count'],
                                'needs_owned_special_piece_count': seeker['owned_special_piece_count'],
                                'needs_owned_percentage': seeker['owned_percentage'],
                                'needs_card_name': card['name'],
                                'needs_card_set_name': card['setName']})
                if showBar:
                    pass  # bar()
            if not showBar:
                self.gui.Print(". ")
            if not nxt:
                break
            data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
        return seekers

    def GetOwners(self, card, showBar=False):
        if card['id'] == -1:
            self.gui.Print("\n\nCouldn't find card " + card['name'] + " in set " + card['setName'])
            return []
        self.gui.Print("\n\nGetting owners of " + card['name'] + " [" + str(card['id']) + "]...\n. ")
        owners = []
        data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/owners/?completion=asc&grade=desc&owned=desc").json()
        # total = data['count']

        # with conditional(showBar, alive_bar(total, bar='smooth', spinner='dots_recur')) as bar:
        while True:
            nxt = data['next']
            for owner in data['results']:
                owners.append({'id': owner['id'],
                               'name': owner['name'],
                               'trader_score': owner['trader_score'],
                               'print_count': owner['print_count'],
                               'has_special_piece_count': owner['special_piece_count'],
                               'has_owned_special_piece_count': owner['owned_special_piece_count'],
                               'has_owned_percentage': owner['owned_percentage'],
                               'has_card_name': card['name'],
                               'has_card_set_name': card['setName']})
                if showBar:
                    pass  # bar()
            if not showBar:
                self.gui.Print(". ")
            if not nxt:
                break
            data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
        return owners

    def GetCards(self, setid, showBar=False):
        set_url = "https://www.neonmob.com/api/setts/" + str(setid) + "/"
        data = requests.request('GET', set_url).json()
        set_name = data['name']
        total = 0
        for cat in range(len(data['core_stats'])):
            total += data['core_stats'][cat]['total']
        for cat in range(len(data['special_stats'])):
            total += data['special_stats'][cat]['total']

        self.gui.Print("Getting cards from series \"" + set_name + "\"...\n. ")

        cards = []
        nxt = "/api/sets/" + str(setid) + "/pieces/"
        # with conditional(showBar, alive_bar(total, bar='smooth', spinner='dots_recur')) as bar:
        first = True
        while True:
            raw = requests.request('GET', "https://www.neonmob.com" + nxt)
            if raw.status_code == 500 and first:
                self.gui.Print("Using fallback card endpoint...\n")
                raw = requests.request('GET', "https://www.neonmob.com/api/sets/" + str(setid) + "/piece-names")
                data = raw.json()
                for card in data:
                    cards.append({'name': card['name'],
                                  'id': card['id'],
                                  'setName': set_name})
                    if showBar:
                        pass  # bar()
                if not showBar:
                    self.gui.Print("...\n")
                break
            else:
                data = raw.json()
                nxt = data['payload']['metadata']['resultset']['link']['next']
                for card in data['payload']['results']:
                    cards.append({'name': card['name'],
                                  'id': card['id'],
                                  'setName': set_name})
                    if showBar:
                        pass  # bar()
                if not showBar:
                    self.gui.Print(". ")
                first = False
                if not nxt:
                    break
        return cards

    def GetCardByName(self, card_list, name):
        for card in card_list:
            if card['name'] == name:
                return card
        return {'name': name, 'id': -1, 'setName': card['setName']}

    def FindCommonTraders(self, seeker_list, owner_list):
        if len(seeker_list) == 0:
            self.gui.Print("\nCouldn't find seekers.")
            return []
        if len(owner_list) == 0:
            self.gui.Print("\nCouldn't find owners.")
            return []
        commons = []

        for seeker in seeker_list:
            for owner in owner_list:
                if seeker['id'] == owner['id'] and owner['print_count'] >= 2:
                    user = seeker.copy()

                    user['print_count'] = owner['print_count']
                    user['has_special_piece_count'] = owner['has_special_piece_count']
                    user['has_owned_special_piece_count'] = owner['has_owned_special_piece_count']
                    user['has_owned_percentage'] = owner['has_owned_percentage']
                    user['has_card_name'] = owner['has_card_name']
                    user['has_card_set_name'] = owner['has_card_set_name']

                    commons.append(user)

        return commons

    def ParseTraders(self, trader_list):
        if not trader_list:
            self.gui.Print("\n\nNo matches found.\n")
        self.gui.Print("\n")
        for trader in trader_list:
            needs_spec_perc = "--"
            has_spec_perc = "--"
            if trader['needs_special_piece_count'] > 0:
                needs_spec_perc = str(int((trader['needs_owned_special_piece_count'] /
                                           trader['needs_special_piece_count']) * 100))
            if trader['has_special_piece_count'] > 0:
                has_spec_perc = str(int((trader['has_owned_special_piece_count'] /
                                         trader['has_special_piece_count']) * 100))
            self.gui.Print("\n" + trader['name'] + " (" +
                           self.ParseTraderGrade(trader['trader_score']) +
                           ")\n")
            self.gui.Print("Needs: \"" + trader['needs_card_name'] +
                           ("\" (Wishlisted)"
                            if trader['wishlisted'] == 1 else "\"") +
                           " from series \"" + trader['needs_card_set_name'] +
                           "\" (" + str(trader['needs_owned_percentage']) +
                           "% core, " + needs_spec_perc + "% special)\n")
            self.gui.Print("Has: \"" + trader['has_card_name'] + "\" (" +
                           str(trader['print_count']) +
                           " copies) from series \"" +
                           trader['has_card_set_name'] + "\" (" +
                           str(trader['has_owned_percentage']) + "% core, " +
                           has_spec_perc + "% special)\n")

    def ParseTraderGrade(self, grade):
        return self.grades[int(grade)]


def main():
    # Create the application first, then the GUI.
    app = NeonMobMatcher()
    gui = MatcherGui(app)
    # Link the application to the GUI.
    app.SetGui(gui)
    # Run the application.
    gui.RunGui()


if __name__ == '__main__':
    main()
