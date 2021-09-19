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


def GetCards(setid, showBar, force=False):
    cards = loadCards(setid)
    if cards != 0 and not force:
        print("Card found in cache")
        return cards

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
    with conditional(showBar, alive_bar(total, bar='smooth', spinner='dots_recur')) as bar:
        first = True
        while True:
            raw = requests.request('GET', "https://www.neonmob.com" + nxt)
            if raw.status_code == 500 and first:
                print("Using fallback card endpoint...")
                raw = requests.request('GET', "https://www.neonmob.com/api/sets/" + str(setid) + "/piece-names")
                data = raw.json()
                for card in data:
                    cards.append({'name': card['name'],
                                  'id': card['id'],
                                  'setName': set_name})
                    if showBar:
                        bar()
                if not showBar:
                    print('...', end="", flush=True)
                break
            else:
                data = raw.json()
                nxt = data['payload']['metadata']['resultset']['link']['next']
                for card in data['payload']['results']:
                    cards.append({'name': card['name'],
                                  'id': card['id'],
                                  'setName': set_name})
                    if showBar:
                        bar()
                if not showBar:
                    print(". ", end="", flush=True)
                first = False
                if not nxt:
                    break
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
                                'wishlisted': seeker['wishlisted'],
                                'needs_special_piece_count': seeker['special_piece_count'],
                                'needs_owned_special_piece_count': seeker['owned_special_piece_count'],
                                'needs_owned_percentage': seeker['owned_percentage']})
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
                               'print_count': owner['print_count'],
                               'has_special_piece_count': owner['special_piece_count'],
                               'has_owned_special_piece_count': owner['owned_special_piece_count'],
                               'has_owned_percentage': owner['owned_percentage'],
                               'has_card_name': card['name'],
                               'has_card_set_name': card['setName']})
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


def main():
    card = {'name': "Joe B. Gamble", 'id': 56093, 'setName': "RANDOM! the Comic TCC"}
    # GetSeekers(card, True, force=True)
    # GetOwners(card, True)
    # GetCards(5908, True)
    # purgeCache()
    searchDB("art")


if __name__ == '__main__':
    main()
