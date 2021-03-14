import sys
import os
import requests
import json
import re

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print('Usage: python3 main.py <folder>')
        print('Ex: python3 main.py /Users/Jamie/Desktop/icons')
        sys.exit(1)

    folderPath = sys.argv[1]
    if not folderPath.startswith('\\') and not folderPath.startswith('/'):
        path = os.path.abspath(os.path.dirname(__file__))
        folderPath = os.path.join(path, folderPath)
    
    for (dirPath, _, fileNames) in os.walk(folderPath):
        for fileName in fileNames:
            groups = re.match("([0-9A-z]+\.[0-9A-z]+\.[0-9A-z]+)", fileName).groups()
            if len(groups) > 0:
                name=groups[0]
                response = requests.get(f'https://itunes.apple.com/lookup/?bundleId={name}')
                if response.status_code == 200:
                    responseJson = json.loads(response.content.decode('utf-8'))
                    if int(responseJson["resultCount"]) > 0:
                            print(f"Renaming {fileName} to {responseJson['results'][0]['trackName'] + '.png'} in {dirPath}")
                            os.rename(os.path.join(dirPath, fileName), os.path.join(dirPath, responseJson['results'][0]['trackName'] + '.png'))
