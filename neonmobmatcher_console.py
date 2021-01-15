import sys
import requests
from alive_progress import alive_bar


def DoLookup(have_setid, have_name, want_setid, want_name):
    if have_setid == want_setid:
        shared_series_cards = GetCards(have_setid)
        seekers = GetSeekers(GetCardByName(shared_series_cards, have_name))
        owners = []
        if len(seekers) != 0:
            owners = GetOwners(GetCardByName(shared_series_cards, want_name))
    else:
        seekers = GetSeekers(GetCardByName(GetCards(have_setid), have_name))
        owners = []
        if len(seekers) != 0:
            owners = GetOwners(GetCardByName(GetCards(want_setid), want_name))

    commons = FindCommonTraders(seekers, owners)
    ParseTraders(commons)


def GetCards(setid):
    set_url = "https://www.neonmob.com/api/setts/" + str(setid) + "/"
    data = requests.request('GET', set_url).json()
    set_name = data['name']
    total = 0
    for cat in range(len(data['core_stats'])):
        total += data['core_stats'][cat]['total']
    for cat in range(len(data['special_stats'])):
        total += data['special_stats'][cat]['total']

    print("\nGetting cards from series \"" + set_name + "\"...")
    cards = []
    nxt = "/api/sets/" + str(setid) + "/pieces/"
    with alive_bar(total, bar='smooth', spinner='dots_recur') as bar:
        while True:
            data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
            nxt = data['payload']['metadata']['resultset']['link']['next']
            for card in data['payload']['results']:
                cards.append({'name': card['name'],
                              'id': card['id'],
                              'setName': set_name})
                bar()
            if not nxt:
                break
    return cards


def GetSeekers(card):
    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []
    print("\nGetting seekers of " + card['name'] + " [" + str(card['id']) + "]...")
    seekers = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/needers/?completion=desc&grade=desc&wishlisted=desc").json()
    total = data['count']

    with alive_bar(total, bar='smooth', spinner='dots_recur') as bar:
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
                bar()
            if not nxt:
                break
            data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    return seekers


def GetOwners(card):
    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []
    print("\nGetting owners of " + card['name'] + " [" + str(card['id']) + "]...")
    owners = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/owners/?completion=asc&grade=desc&owned=desc").json()
    total = data['count']

    with alive_bar(total, bar='smooth', spinner='dots_recur') as bar:
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
                bar()
            if not nxt:
                break
            data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    return owners


def GetCardByName(card_list, name):
    for card in card_list:
        if card['name'] == name:
            return card
    return {'name': name, 'id': -1, 'setName': card['setName']}


def FindCommonTraders(seeker_list, owner_list):
    if len(seeker_list) == 0:
        print("\nCouldn't find seekers.")
        return []
    if len(owner_list) == 0:
        print("\nCouldn't find owners.")
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


def ParseTraders(trader_list):
    if trader_list == []:
        print("\nNo matches found.\n")
    print()

    for trader in trader_list:
        needs_spec_perc = "--"
        has_spec_perc = "--"
        if trader['needs_special_piece_count'] > 0:
            needs_spec_perc = str(int((trader['needs_owned_special_piece_count'] /
                                       trader['needs_special_piece_count']) * 100))
        if trader['has_special_piece_count'] > 0:
            has_spec_perc = str(int((trader['has_owned_special_piece_count'] /
                                     trader['has_special_piece_count']) * 100))
        print()
        print(trader['name'] + " (" +
                       ParseTraderGrade(trader['trader_score']) +
                       ")")
        print("Needs: \"" + trader['needs_card_name'] +
                       ("\" (Wishlisted)"
                        if trader['wishlisted'] == 1 else "\"") +
                       " from series \"" + trader['needs_card_set_name'] +
                       "\" (" + str(trader['needs_owned_percentage']) +
                       "% core, " + needs_spec_perc + "% special)")
        print("Has: \"" + trader['has_card_name'] + "\" (" +
                       str(trader['print_count']) +
                       " copies) from series \"" +
                       trader['has_card_set_name'] + "\" (" +
                       str(trader['has_owned_percentage']) + "% core, " +
                       has_spec_perc + "% special)\n")


def ParseTraderGrade(grade):
    grades = ['F', 'F+', 'D-', 'D', 'D+', 'C-', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A', 'A+']
    return grades[int(grade)]


def main():
    have_setid = 0
    while True:
        have_setid_str = input("Have Set ID: ")
        try:
            have_setid = int(have_setid_str)
            break
        except ValueError as ve:
            print("You entered {}, which is not an integer.\n".format(have_setid_str))
            continue

    have_name = input("Have Name: ")

    want_setid = 0
    while True:
        want_setid_str = input("Want Set ID: ")
        try:
            want_setid = int(want_setid_str)
            break
        except ValueError as ve:
            print("You entered {}, which is not an integer.\n".format(want_setid_str))
            continue

    want_name = input("Want Name: ")

    DoLookup(have_setid, have_name, want_setid, want_name)


if __name__ == '__main__':
    # print(GetOwners({'name': 'Day 1', 'id': 180998, 'setName': 'The 100 Day Project II'}))
    # print(GetCards(20476))
    main()
