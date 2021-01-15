import time
import random

from alive_progress import alive_bar

with alive_bar(200, bar='smooth', spinner='dots_recur') as bar:
    for i in range(200):
        time.sleep(random.random() / 8)
        bar()
