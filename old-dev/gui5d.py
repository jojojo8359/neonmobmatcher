import requests
import PySimpleGUI as sg


def GetOwners(card, force=False):
    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []

    # currentMillis = int(round(time.time() * 1000))
    # if str(card['id']) in OCACHE.keys() and not force:
    #     print("Card is in cache")
    #     if currentMillis - OCACHE[str(card['id'])]['time'] < (keepalivemins * 60 * 1000):
    #         print("Time is under 10 minutes")
    #         return OCACHE[str(card['id'])]['owners']

    print("\nGetting owners of " + card['name'] + " [" + str(card['id']) + "]...")
    owners = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/owners/?completion=asc&grade=desc&owned=desc").json()
    total = data['count']
    i = 0

    while True:
        nxt = data['next']
        for owner in data['results']:
            owners.append({'id': owner['id'],
                           'name': owner['name'],
                           'trader_score': owner['trader_score'],
                           'owns': [
                               {
                                   'card_id': card['id'],
                                   'card_name': card['name'],
                                   'set_name': card['setName'],
                                   'print_count': owner['print_count'],
                                   'total_specials': owner['special_piece_count'],
                                   'specials': owner['owned_special_piece_count'],
                                   'percentage': owner['owned_percentage']
                               }
                           ],
                           'wants': []
                           })
            i += 1
            sg.one_line_progress_meter('My progress meter', i, total, "Getting owners of " + card['name'] + " [" + str(card['id']) + "]...", orientation='h')
        if not nxt:
            break
        data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    return owners


def GetSeekers(card, force=False):
    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []

    print("\nGetting seekers of " + card['name'] + " [" + str(card['id']) + "]...")
    seekers = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/needers/?completion=desc&grade=desc&wishlist=desc").json()
    total = data['count']
    i = 0

    while True:
        nxt = data['next']
        for seeker in data['results']:
            seekers.append({'id': seeker['id'],
                            'name': seeker['name'],
                            'trader_score': seeker['trader_score'],
                            'wants': [
                                {
                                    'card_id': card['id'],
                                    'card_name': card['name'],
                                    'set_name': card['setName'],
                                    'wishlisted': seeker['wishlisted'],
                                    'total_specials': seeker['special_piece_count'],
                                    'specials': seeker['owned_special_piece_count'],
                                    'percentage': seeker['owned_percentage']
                                }
                            ],
                            'owns': []
                            })
            i += 1
            sg.one_line_progress_meter('My progress meter', i, total, "Getting seekers of " + card['name'] + " [" + str(card['id']) + "]...", orientation='h')
        if not nxt:
            break
        data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    return seekers


card1 = {'name': "Joe B. Gamble", 'id': 56093, 'setName': "RANDOM! the Comic TCC"}
GetSeekers(card1)
