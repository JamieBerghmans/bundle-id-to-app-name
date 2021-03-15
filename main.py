import sys
import os
import requests
import json
import re
from countries import countriesList
from threading import Thread
import keyboard
import time

class Main():
    shouldSkip = False
    done = False
    
    def __init__(self):
        self.shouldSkip = False
        self.done = False
        Thread(target=self.handleKeyPressLoop, args=()).start()

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
                                        print(f"Renaming {fileName} to {responseJson['results'][0]['trackName'] + '.png'} in {dirPath}")
                                        try:
                                            os.rename(os.path.join(dirPath, fileName), os.path.join(dirPath, responseJson['results'][0]['trackName'].replace('/', ' ').replace(':', ' ').replace('-', ' ').replace('|', ' ').replace('&', ' ') + '.png'))
                                        except:
                                            print(f"[ERROR - SKIPPING] Failed to rename {fileName} to {responseJson['results'][0]['trackName'] + '.png'} in {dirPath}")
                                        break
                                    else:
                                        if self.shouldSkip or "apple" in name:
                                            self.shouldSkip = False
                                            print(f'[ERROR - SKIPPING] BundleID {name} not found. Going onto the next one')
                                            break
                                        else:
                                            print(f"[ERROR - SKIPPING] BundleID {name} not found on Apple's Lookup Website (Country: {country}). Trying next country")

        self.done = True

    def setDoneFlag(self):
        print('CTRL+C detected, quitting')
        self.done = True

    def handleKeyPressLoop(self):
        keyAlreadyPressed = False
        keyboard.add_hotkey('ctrl+c', lambda: self.setDoneFlag())

        while not self.done:
            if keyboard.is_pressed("space"):
                if not keyAlreadyPressed:
                    self.shouldSkip = True
                    keyAlreadyPressed = True
                    time.sleep(0.1)
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

    print('If key presses to skip don\'t work, you might have to run this scrip as root.')
    main = Main()