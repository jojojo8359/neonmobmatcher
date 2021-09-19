import requests
from conditional import conditional
from alive_progress import alive_bar
import time
import json
from os import path
from timeit import default_timer as timer

SCACHE = {}
OCACHE = {}

keepalivemins = 10

setdbpath = "db.json"
SETDB = {}


def loadSetDB():
    global SETDB
    with open(setdbpath, 'r') as f:
        SETDB = json.load(f)


def printseries(serieslist):
    for series in serieslist:
        print(series['name'] + ' (' + str(series['id']) + ') by ' + series['creator']['username'] + ': ' + series['difficulty'] + ' ' + series['edition_size'] + ' series')


def searchDB(query):
    global SETDB
    start = timer()
    if SETDB == {}:
        loadSetDB()
    filtered = list(filter(lambda series: query.lower() in series['name'].lower() or query.lower() in series['name_slug'].lower() or query.lower() in series['creator']['username'].lower() or query.lower() in series['creator']['name'], SETDB))
    filtered.reverse()

    printseries(filtered)
    end = timer()
    print(str(len(filtered)) + " results in " + str(end - start))


def loadCache():
    global SCACHE, OCACHE
    with open('cache/scache.json', 'r') as f:
        SCACHE = json.load(f)
    with open('cache/ocache.json', 'r') as f:
        OCACHE = json.load(f)


def purgeCache():
    global SCACHE, OCACHE
    loadCache()
    currentMillis = int(round(time.time() * 1000))
    for k in list(SCACHE.keys()):
        if currentMillis - SCACHE[k]['time'] >= (keepalivemins * 60 * 1000):
            del SCACHE[k]
    for k in list(OCACHE.keys()):
        if currentMillis - OCACHE[k]['time'] >= (keepalivemins * 60 * 1000):
            del OCACHE[k]
    saveCache()


def deleteCache():
    with open('cache/scache.json', 'w') as f:
        json.dump({}, f)
    with open('cache/ocache.json', 'w') as f:
        json.dump({}, f)


def saveCache():
    global SCACHE, OCACHE
    with open('cache/scache.json', 'w') as f:
        json.dump(SCACHE, f)
    with open('cache/ocache.json', 'w') as f:
        json.dump(OCACHE, f)


def loadCards(setid):
    if path.exists('cache/cards/' + str(setid) + '.json'):
        with open('cache/cards/' + str(setid) + '.json', 'r') as f:
            cards = json.load(f)
        return cards
    else:
        return 0


def saveCards(setid, cards):
    with open('cache/cards/' + str(setid) + '.json', 'w') as f:
        json.dump(cards, f)


def GetCards(setid, force=False):
    cards = loadCards(setid)
    if cards != 0 and not force:
        print("Card found in cache")
        return cards

    set_url = "https://www.neonmob.com/api/setts/" + str(setid) + "/"
    data = requests.request('GET', set_url).json()
    set_name = data['name']
    # total = 0
    # for cat in range(len(data['core_stats'])):
    #     total += data['core_stats'][cat]['total']
    # for cat in range(len(data['special_stats'])):
    #     total += data['special_stats'][cat]['total']

    print("\nGetting cards from series \"" + set_name + "\"...")
    cards = []
    raw = requests.request('GET', "https://www.neonmob.com/api/sets/" + str(setid) + "/piece-names")
    data = raw.json()
    for card in data:
        cards.append({'name': card['name'],
                      'rarity': card['rarity']['name'],
                      'id': card['id'],
                      'setName': set_name})
    saveCards(setid, cards)
    return cards


def GetSeekers(card, showBar, force=False):
    global SCACHE

    purgeCache()

    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []

    currentMillis = int(round(time.time() * 1000))
    if str(card['id']) in SCACHE.keys() and not force:
        print("Card is in cache")
        if currentMillis - SCACHE[str(card['id'])]['time'] < (keepalivemins * 60 * 1000):
            print("Time is under 10 minutes")
            return SCACHE[str(card['id'])]['seekers']

    print("\nGetting seekers of " + card['name'] + " [" + str(card['id']) + "]...")
    seekers = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/needers/?completion=desc&grade=desc&wishlist=desc").json()
    total = data['count']

    with conditional(showBar, alive_bar(total, bar='smooth', spinner='dots_recur')) as bar:
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
                if showBar:
                    bar()
            if not showBar:
                print(". ", end="", flush=True)
            if not nxt:
                break
            data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    try:
        SCACHE.pop(str(card['id']))
    except KeyError:
        print("Card is not in cache")
    currentMillis = int(round(time.time() * 1000))
    SCACHE.update({card['id']: {'time': currentMillis, 'cardName': card['name'], 'setName': card['setName'], 'seekers': seekers}})
    saveCache()
    return seekers


def GetOwners(card, showBar, force=False):
    global OCACHE

    purgeCache()

    if card['id'] == -1:
        print("\nCouldn't find card " + card['name'] + " in set " + card['setName'])
        return []

    currentMillis = int(round(time.time() * 1000))
    if str(card['id']) in OCACHE.keys() and not force:
        print("Card is in cache")
        if currentMillis - OCACHE[str(card['id'])]['time'] < (keepalivemins * 60 * 1000):
            print("Time is under 10 minutes")
            return OCACHE[str(card['id'])]['owners']

    print("\nGetting owners of " + card['name'] + " [" + str(card['id']) + "]...")
    owners = []
    data = requests.request('GET', "https://www.neonmob.com/api/pieces/" + str(card['id']) + "/owners/?completion=asc&grade=desc&owned=desc").json()
    total = data['count']

    with conditional(showBar, alive_bar(total, bar='smooth', spinner='dots_recur')) as bar:
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
                if showBar:
                    bar()
            if not showBar:
                print(". ", end="", flush=True)
            if not nxt:
                break
            data = requests.request('GET', "https://www.neonmob.com" + nxt).json()
    try:
        OCACHE.pop(str(card['id']))
    except KeyError:
        print("Card is not in cache")
    currentMillis = int(round(time.time() * 1000))
    OCACHE.update({card['id']: {'time': currentMillis, 'cardName': card['name'], 'setName': card['setName'], 'owners': owners}})
    saveCache()
    return owners


"""
Person:
{
    'id': int,
    'name': str,
    'trader_score': int?,
    'owns': [
        {
            'card_id': int,
            'card_name': str,
            'set_name': str,
            'print_count': int,
            'percentage': str?,
            'specials': int,
            'total_specials': int
        }
    ],
    'wants': [
        {
            'card_id': int,
            'card_name': str,
            'set_name': str,
            'wishlisted': bool?,
            'percentage': str?,
            'specials': int,
            'total_specials': int
        }
    ]
}

"""


def combinePeople(list1, *lists):
    master = []
    allids = []
    for larg in lists:
        list1.extend(larg)

    for person in list1:
        if person['id'] not in allids:
            master.append(person)
            allids.append(person['id'])
        else:
            currentindex = [i for i, t in enumerate(master) if t['id'] == person['id']][0]
            currentperson = master[currentindex]
            for i in range(len(person['owns'])):
                check = True
                for j in range(len(currentperson['owns'])):
                    if person['owns'][i]['card_name'] == currentperson['owns'][j]['card_id']:
                        check = False
                if check:
                    currentperson['owns'].append(person['owns'][i])

            for i in range(len(person['wants'])):
                check = True
                for j in range(len(currentperson['wants'])):
                    if person['wants'][i]['card_name'] == currentperson['wants'][j]['card_id']:
                        check = False
                if check:
                    currentperson['wants'].append(person['wants'][i])
    return master


def getCommons(people, owned, want, mode='and', checkprintcount=False):
    """
    people: list of people to search through
    owned: list of card ids to check
    want: list of card ids to check
    mode: 'and' or 'or'
    """
    master = []
    if mode == 'and':
        for person in people:
            mastercheck = True
            if len(person['owns']) == 0 or len(person['wants']) == 0:
                continue
            # print("Person does not have empty lists")
            for ownedid in owned:
                cardcheck = False
                for ownedcard in person['owns']:
                    if checkprintcount and ownedcard['print_count'] < 2:
                        break
                    elif ownedid == ownedcard['card_id']:
                        cardcheck = True
                        break
                if not cardcheck:
                    mastercheck = False
                    break
            for wantedid in want:
                cardcheck = False
                for wantedcard in person['wants']:
                    if wantedid == wantedcard['card_id']:
                        cardcheck = True
                        break
                if not cardcheck:
                    mastercheck = False
                    break
            if mastercheck:
                master.append(person)
    elif mode == 'or':
        for person in people:
            mastercheck = False
            printcheck = False
            if len(person['owns']) == 0 or len(person['wants']) == 0:
                continue
            for ownedid in owned:
                cardcheck = False
                for ownedcard in person['owns']:
                    if checkprintcount and ownedcard['print_count'] < 2:
                        printcheck = True
                        break
                    elif ownedid == ownedcard['card_id']:
                        cardcheck = True
                        break
                if cardcheck:
                    mastercheck = True
            for wantedid in want:
                cardcheck = False
                for wantedcard in person['wants']:
                    if wantedid == wantedcard['card_id']:
                        cardcheck = True
                        break
                if cardcheck:
                    mastercheck = True
            if mastercheck and not printcheck:
                master.append(person)
    return master


def main():
    # deleteCache()
    # card = {'name': "Joe B. Gamble", 'id': 56093, 'setName': "RANDOM! the Comic TCC"}
    card = {"name": "Freedom", "rarity": "Common", "id": 207486, "setName": "Wicked Mind"}
    card2 = {"name": "Lying", "rarity": "Common", "id": 207487, "setName": "Wicked Mind"}
    card3 = {"name": "Night Walk", "rarity": "Common", "id": 207488, "setName": "Wicked Mind"}
    seekers = GetSeekers(card, True)
    owners = GetOwners(card2, True)
    owners2 = GetOwners(card3, True)
    everyone = combinePeople(seekers, owners, owners2)
    # print(everyone)
    filtered = getCommons(everyone, [207487, 207488], [207486], 'or', checkprintcount=False)
    print(filtered)

    person1 = [{
        "id": 75532,
        "name": "Kyla Sedai",
        "trader_score": 13.0,
        "wants":
        [
            {
                "card_id": 207486,
                "card_name": "Freedom",
                "set_name": "Wicked Mind",
                "wishlisted": 0,
                "total_specials": 6,
                "specials": 0,
                "percentage": 59
            }
        ],
        "owns":
        []
    }]

    person2 = [{
        "id": 75532,
        "name": "Kyla Sedai",
        "trader_score": 13.0,
        "owns":
        [
            {
                "card_id": 207487,
                "card_name": "Lying",
                "set_name": "Wicked Mind",
                "print_count": 2,
                "total_specials": 6,
                "specials": 2,
                "percentage": 81
            },
            {
                "card_id": 207488,
                "card_name": "Night Walk",
                "set_name": "Wicked Mind",
                "print_count": 3,
                "total_specials": 6,
                "specials": 2,
                "percentage": 81
            }
        ],
        "wants":
        []
    }]

    person3 = [{
        "id": 2697,
        "name": "Ben Frank",
        "trader_score": 13.0,
        "wants":
        [
            {
                "card_id": 207486,
                "card_name": "Freedom",
                "set_name": "Wicked Mind",
                "wishlisted": 0,
                "total_specials": 6,
                "specials": 2,
                "percentage": 59
            }
        ],
        "owns":
        [
            {
                "card_id": 207487,
                "card_name": "Lying",
                "set_name": "Wicked Mind",
                "print_count": 1,
                "total_specials": 6,
                "specials": 2,
                "percentage": 59
            },
            {
                "card_id": 207488,
                "card_name": "Night Walk",
                "set_name": "Wicked Mind",
                "print_count": 1,
                "total_specials": 6,
                "specials": 2,
                "percentage": 59
            }
        ]
    }]

    # processed = getCommons(person3, [207487, 207488], [207486], 'and', checkprintcount=False)
    # print(processed)

    # asdf = combinePeople(person1, person2)
    # print(asdf)

    # everyone3 = []
    # for person in everyone2:
    #     one = False
    #     for card in person['owns']:
    #         if card['print_count'] < 2:
    #             one = True
    #     if one == False:
    #         everyone3.append(person)
    # print(everyone3)
    # GetCards(22311, True)
    # purgeCache()
    # searchDB("art")


if __name__ == '__main__':
    main()
