# neonmobmatcher
This tool allows the user to find other NeonMob card collectors for making specific card trades (trading card X for card Y), which the NeonMob site currently does not support.

## Requirements
- Python 3
- TkInter (and TkMacOSX for Mac)
- requests
- alive_progress (for console version)
- conditional (for console version)

To install all required modules in your environment:
- `pip3 install -r requirements.txt` for GUI
- `pip3 install -r mac-gui.txt` for GUI on Mac
- `pip3 install -r console.txt` for console version

## How to Use
1. Identify the card series ID number (see my [nm-trade-tracker Chrome extension](https://github.com/jojojo8359/nm-trade-tracker)) of the card you wish to trade away and enter in the "Have Set ID" box. (Once the extension is installed, go to the series page for the card series of interest and click on "Your Cards." Hover over the series title, and the six digit series ID number will appear.)
2. Enter the name of the card you wish to trade away (exactly as shown on the website, including whitespace and punctuation) and enter in the "Have Card Name" box. (Copy and paste if needed.)
3. Repeat steps 1-2 for the card you wish to obtain from another user (enter in "Want Set ID" and "Want Card Name").
4. Click "Submit." Results will show as a list of possible users to trade with (more desirable towards the top, as organized by wishlisted, completion, and trader grade).
