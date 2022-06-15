import requests, re, time, os, json
from datetime import datetime, timedelta
from colorama import init, Fore
init()

config = None

for files in os.walk('.'):
    if 'config.json' in str(files):
        config = json.load(open('config.json','r'))
        break
    else:
        webhook = input('Enter webhook: ')
        discord_id = input('Enter discord id to ping when an item updates: ')
        config = { 
            "webhook": webhook,
            "discord_id": discord_id
        }
        with open('config.json','w') as file:
            json.dump(config, file, indent=4)

class Updates:
    def __init__(self):
        self.previousCheck = []
        self.firstCheck()
        self.constantChecks()

    def firstCheck(self):
        catalog = requests.get('https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId=1&limit=60&sortType=3').json()['data']
        self.previousCheck = [item["id"] for item in catalog if item['itemType'] == 'Asset']

    def constantChecks(self):
        while True:
            try:
                catalog = requests.get('https://catalog.roblox.com/v1/search/items?category=All&creatorTargetId=1&limit=60&sortType=3').json()['data']
                current = [item["id"] for item in catalog if item['itemType'] == 'Asset']
                for item in current:
                    if not item in self.previousCheck:
                        itemInfo = requests.get(f'https://api.roblox.com/marketplace/productinfo?assetId={item}').json()
                        itemImage = requests.get(f'https://thumbnails.roblox.com/v1/assets?assetIds={item}&size=250x250&format=Png&isCircular=false').json()['data'][0]['imageUrl']

                        itemName = itemInfo['Name']
                        itemLimited = itemInfo['IsLimited']
                        itemForSale = itemInfo['IsForSale']
                        itemPrice = itemInfo['PriceInRobux']
                        itemCreation = itemInfo['Created'].split('T')[0]
                        itemDescription = itemInfo['Description']
                        itemUpdated = itemInfo['Updated'].split('T')[0]

                        if itemUpdated == str(datetime.now() - timedelta(hours=1)).split(' ')[0]:

                            data = {
                            'content': f'<@{config["discord_id"]}>',
                            'embeds':[{
                                'author': {
                                    'name': f'{itemName}',
                                    'url': f'https://www.roblox.com/catalog/{item}'
                                    },
                                'color': int('b972cf',16),
                                'fields': [
                                    {'name': f'Price','value': f'{str(itemPrice)}','inline':True},
                                    {'name': f'Limited','value': f'{str(itemLimited)}','inline':True},
                                    {'name': f'\u200b','value': f'\u200b','inline':True},
                                    {'name': f'On sale','value': f'{str(itemForSale)}','inline':True},
                                    {'name': f'Created','value': f'{itemCreation}','inline':True},
                                    {'name': f'Updated','value': f'{itemUpdated}','inline':True},
                                    {'name': f'Description','value': f'{itemDescription}','inline':False},
                                        ],
                                'thumbnail': {
                                  'url': itemImage,
                                  }
                                }]
                            }

                            requests.post(config['webhook'], json=data)
                            print(f'{Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}] An item was updated ([{Fore.GREEN}{item}{Fore.WHITE}])')

                self.previousCheck = current
                print(f'{Fore.WHITE}[{Fore.MAGENTA}+{Fore.WHITE}] Finished checking catalog')
                time.sleep(60)
            except Exception as err:
                pass

c = Updates()
