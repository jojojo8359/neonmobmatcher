import requests


def get_json(url):
    """Uses requests to get json data from a specific url

    :param str url: The url to get json data from
    :returns: json data if successfully fetched, -1 otherwise
    """
    try:
        r = requests.request('GET', url)
        r.raise_for_status()
        json_data = r.json()
        return json_data
    except requests.exceptions.ConnectionError as e:
        print('Network problem has occurred.', e)
        return -1
    except requests.exceptions.HTTPError as e:
        print('An HTTP error has occurred.', e)
        return -1
    except requests.exceptions.Timeout as e:
        print('Request timed out.', e)
        return -1
    except requests.exceptions.TooManyRedirects as e:
        print('Request redirected too many times.', e)
        return -1
    except requests.exceptions.RequestException as e:
        print('Other request error has occurred.', e)
        return -1


def get_text(url):
    """

    :param url: The url to get text from
    :type url: str
    :return: text if successfully fetched, -1 otherwise
    :rtype:
    """
    try:
        r = requests.request('GET', url)
        r.raise_for_status()
        text_data = r.text
        return text_data
    except requests.exceptions.ConnectionError as e:
        print('Network problem has occurred.', e)
        return -1
    except requests.exceptions.HTTPError as e:
        print('An HTTP error has occurred.', e)
        return -1
    except requests.exceptions.Timeout as e:
        print('Request timed out.', e)
        return -1
    except requests.exceptions.TooManyRedirects as e:
        print('Request redirected too many times.', e)
        return -1
    except requests.exceptions.RequestException as e:
        print('Other request error has occurred.', e)
        return -1


id = 238793
page = 1
last_active = ''

while not last_active:
    print("Page " + str(page))
    activity_url = "https://napi.neonmob.com/activityfeed/user/" + str(id) + "/?amount=20&page=" + str(page)
    activity_data = get_json(activity_url)
    for activity in activity_data:
        if activity['type'] == 'pack-opened':  # pack-opened
            last_active = activity['created']
            break
    page += 1
    if page == 101:
        break

print(last_active)
