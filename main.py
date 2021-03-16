import sys
import os
import requests
import json
import re
from countries import countriesList
from threading import Thread
import time
import curses
import sys
import signal

class Main():
    shouldSkip = False
    done = False
    window = None

    def __init__(self):
        self.shouldSkip = False
        self.done = False

    def run(self, window):
        self.window = window
        window.scrollok(1)
        window.timeout(1)

        Thread(target=self.handleKeyPressLoop, args=()).start()

        window.addstr('Starting...\n')

        folderPath = sys.argv[1]
        if not folderPath.startswith('\\') and not folderPath.startswith('/'):
            path = os.path.abspath(os.path.dirname(__file__))
            folderPath = os.path.join(path, folderPath)
        
        for (dirPath, _, fileNames) in os.walk(folderPath):
            for fileName in fileNames:
                newName = fileName.replace('.png', '')
                match = re.match("([0-9A-z-]+\.[0-9A-z-]+(\.[0-9A-z-]+){0,})", newName)
                if match != None:
                    groups = match.groups()
                    if len(groups) > 0:
                        name=groups[0]
                        for country in countriesList:
                            response = requests.get(f'https://itunes.apple.com/lookup/?bundleId={name}&country={country.lower()}')
                            if response.status_code == 200:
                                responseJson = json.loads(response.content.decode('utf-8'))
                                if not self.done:
                                    if int(responseJson["resultCount"]) > 0:
                                        self.window.addstr(f"Renaming {fileName} to {responseJson['results'][0]['trackName'] + '.png'} in {dirPath}\n")
                                        try:
                                            os.rename(os.path.join(dirPath, fileName), os.path.join(dirPath, responseJson['results'][0]['trackName'].replace('/', ' ').replace(':', ' ').replace('-', ' ').replace('|', ' ').replace('&', ' ') + '.png'))
                                        except:
                                            self.window.addstr(f"[ERROR - SKIPPING] Failed to rename {fileName} to {responseJson['results'][0]['trackName'] + '.png'} in {dirPath}\n")
                                        break
                                    else:
                                        if self.shouldSkip or "apple" in name:
                                            self.shouldSkip = False
                                            self.window.addstr(f'[ERROR - SKIPPING] BundleID {name} not found. Going onto the next one\n')
                                            break
                                        else:
                                            self.window.addstr(f'[ERROR - SKIPPING] BundleID {name} not found on Apple\'s Lookup Website (Country: {country}). Trying next country\n')
                            

        self.done = True

    def setDoneFlag(self):
        self.window.addstr('CTRL+C detected, quitting')
        self.done = True
        curses.endwin()
        os._exit(0)

    def handleKeyPressLoop(self):
        keyAlreadyPressed = False

        while not self.done:
            key = self.window.getch()
            if key == 32:
                if not keyAlreadyPressed:
                    self.shouldSkip = True
                    keyAlreadyPressed = True
                    time.sleep(0.1)
            elif key == 3:
                self.setDoneFlag()
            else:
                if keyAlreadyPressed:
                    keyAlreadyPressed = False
            time.sleep(0.05)

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print('Usage: python3 main.py <folder>')
        print('Ex: python3 main.py /Users/Jamie/Desktop/icons')
        done = True
        sys.exit(1)

    main = Main()
    curses.wrapper(main.run)
    curses.echo()