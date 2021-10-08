# neonmobmatcher
This tool lets you find possible trades for specific cards on [NeonMob](https://www.neonmob.com/).

For example, if you have a duplicate card in a series and need one more card of the same rarity, you can specify both cards in the matcher, and it will give a list of possible NeonMob trading partners for that specifc trading scenario.

## Requirements
- [Python 3](https://www.python.org/downloads/)
- [requests](https://pypi.org/project/requests/)
- [PySimpleGUI (TK version)](https://pypi.org/project/PySimpleGUI/)

To install all required modules in your environment:

`pip3 install -r requirements.txt`

## How to Use
The search list has two sides: one for cards you want to receive in a trade, and one for cards you want to trade away. In order to add cards to one side, click the "+" button to the right of the list. Begin typing in the box to search for the series by title. (As you use NMM more, this window will begin displaying recent series you searched for when the search box is left empty.) Then, select the name of the card you want from the resulting list for that series to add it to the trade list. (You can sort the list by name or rarity by right-clicking anywhere in the table.) If you want to select multiple cards from a series at once, either Shift-click or Control-click another card in the list. If you want to add all cards of a specific rarity to the trade list, select that rarity from the dropdown at the bottom of the window and click "Add All of Rarity." To remove a card from a trade list, click on the card title to highlight it and click the "-" button on the same side of the trade. To clear all cards from a trade list, click the "C" button.

You can add as many cards as needed to each side of the trade. Before searching, there are a few options that can help refine your trade search. The "Force Refresh" option, when checked, will perform a fresh trade search, ignoring existing results in the results cache. When checked, the "2+ Prints" checkbox will only include results for other users who have two or more copies of cards you are looking for. The And/Or Mode dropdown can help filter ownership criteria as follows:

### "And" Mode
- Suppose you have a duplicate Rare card and want a list of traders needing that card and having duplicates of two Uncommon cards you seek. Be sure to select "And" before starting the search, and your search results will include all the NM traders who are seeking your card and have duplicates of BOTH of the two cards you seek.

### "Or" Mode
- Suppose you just received a duplicate Extra Rare card in a series and want to trade it for *either* of the last two Extra Rares you need to complete that level. Add the name of your ER duplicate to the "Cards I want to trade away" list and the names of both cards you still need to the "Cards I'm seeking from someone else" list and be sure to select "Or" before starting the search. Your search results will include all the NM traders who are seeking your card and have a duplicate of *either* of the two cards you still need.

Once a trade search is completed, a results window will appear. If the top list is empty, no traders were found for your search. :( If traders were found, they will appear in the top list. Clicking on a trader's name will show the cards that would be exchanged in the two lower tables. If a card in the left card list is selected (owned by another trader), the print numbers of that card will be displayed at the bottom the window. If a trader is selected from the top list and "Open User Profile" is clicked, that trader's NeonMob page will open in your default web browser.

## Data Caching
The matcher uses NM set data from [neonmob-set-db](https://www.github.com/jojojo8359/neonmob-set-db), a self-updating database that contains information about all NeonMob sets: past, present, and future. By default, the matcher will attempt to get the latest version of the database on startup. This can be configured in the application settings (found in the File menu), and the database can also be manually updated (using the "Update Database" option in the File menu).

The first time a set is queried, the list of cards in that set is stored locally (but just the first time). Card information *can* change over time, but it does not happen very often. If you want to update the list of cards in a set, click the "Refresh" button while looking through cards in that set.

When a search is successfully performed, traders that match search criteria are locally saved. By default, this cache will expire 10 minutes after a result is saved, but this value can be changed in the application settings. This makes doing repeat searches very quick (especially if you just want to change searching options).