import requests
import json
import hashlib


def fetchdb():
    db = requests.request('GET', 'https://raw.githubusercontent.com/jojojo8359/neonmob-set-db/main/all-sets.json').json()
    return db


def downloaddb():
    db = fetchdb()
    with open('db.json', 'w') as f:
        json.dump(db, f)


def fetchmd5():
    md5 = requests.request('GET', 'https://raw.githubusercontent.com/jojojo8359/neonmob-set-db/main/all-sets.md5').text
    return md5.split('  ')[0]


def verify(truemd5):
    filename = 'db.json'
    with open(filename, 'rb') as f:
        data = f.read()
        returnedmd5 = hashlib.md5(data).hexdigest()
    return truemd5 == returnedmd5


def updatedb():
    if not verify(fetchmd5()):
        print("Database is not up to date, downloading newest version...")
        downloaddb()
        if not verify(fetchmd5()):
            print("Database is still not up to date, please update manually. https://github.com/jojojo8359/neonmob-set-db/blob/main/all-sets.json")
        else:
            print("Database has been sucessfully updated.")
    else:
        print("Database is up to date.")


def main():
    updatedb()


if __name__ == '__main__':
    main()
