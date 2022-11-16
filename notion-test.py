import json
import requests
import time


config = json.load(open('config.txt', "r"))

TOKEN = config['token']
PAGE_ID = config['db_id']
CFG_PATH = config['cfg_path']
playlist_input = config['playlist']

# map_dict = {'1': 'dust', '2': 'mirage', '3': 'inferno',
#             '4': 'overpass', '5': 'ancient', '6': 'nuke'}
# playlist_dict = {'1': 'dima', '2': 'igor'}

# mode_input = input('Mode (1-load, 2-reload): ')
# if mode_input == '1':
#     map_input = input(
#         'Map (1-dust, 2-mirage, 3-inferno, 4-overpass, 5-ancient, 6-nuke): ')
#     if map_input in map_dict:
#         map_input = map_dict[map_input]
#     else:
#         map_input = ''
#     playlist_input = input('Playlist (1-dima, 2-igor): ')
#     if playlist_input in playlist_dict:
#         playlist_input = playlist_dict[playlist_input]
#     else:
#         playlist_input = ''

#     new_config = {'token': TOKEN, 'db_id': PAGE_ID, 'cfg_path': CFG_PATH,
#                   'map': map_input, 'playlist': playlist_input}
#     json_object = json.dumps(new_config, indent=4)
#     with open("config.txt", "w") as outfile:
#         outfile.write(json_object)
# else:
#     map_input = config['map']
#     playlist_input = config['playlist']

url = "https://api.notion.com/v1/databases/61fe071adcfc42aba900d2bdb058926d/query"

payload = {"page_size": 100,
           "sorts": [{"property": "Order", "direction": "ascending"}]
           #  {"property": "Map", "direction": "ascending"}],
           #    "filter": {"and": [{"property": "Map", "rich_text": {"contains": "Dust"}}, {{"property": "Map", "rich_text": {"contains": "Dust"}}}]}
           }
headers = {
    "accept": "application/json",
    "Notion-Version": "2022-06-28",
    "content-type": "application/json",
    "authorization": "Bearer secret_o9i7RdJyj9jMoJvDXwQFLoxPDxsleyfLUiutxS9JKxZ"
}

response = requests.post(url, json=payload, headers=headers)
respons_json = json.loads(response.text)
results = respons_json['results']
# for i in respons_json['results']:
#     print(i['id'])
# assert 0
# print(len(results))

if len(respons_json['results']) == 100:
    last_id = results[-1]['id']
    # print(last_id)
    # assert 0
    payload = {"page_size": 100, "start_cursor": last_id,
               "sorts": [{"property": "Order", "direction": "ascending"}]}
    response = requests.post(url, json=payload, headers=headers)
    respons_json = json.loads(response.text)
    results = results + respons_json['results'][1:]
# print(len(results))
# assert 0

# print('len:', len(respons_json['results']))
# print(json.dumps(respons_json, indent=4))
res0 = {}
count = 0
for result in results:
    # print(result['properties']['Name']['title'])
    if len(result['properties']['Name']['title']) == 0 or len(result['properties']['Coordinates']['rich_text']) == 0:
        continue
    name = result['properties']['Name']['title'][0]['text']['content']
    name = 'say ' + name
    map = result['properties']['Map']['select']['name']
    coordinates = result['properties']['Coordinates']['rich_text'][0]['text']['content']
    coordinates = coordinates.split(' ')
    tmp = coordinates[3].split(';')
    new_y = str(round(float(tmp[0])-64, 6))
    tmp[0] = new_y
    tmp = ';'.join(tmp)
    coordinates[3] = tmp
    coordinates = ' '.join(coordinates)
    playlists = []
    for i in range(len(result['properties']['Playlists']['multi_select'])):
        playlists.append(result['properties']['Playlists']
                         ['multi_select'][i]['name'])
    # print(map, name)
    if (playlist_input in playlists or playlist_input == ''):
        if map not in res0:
            res0[map] = []
        res0[map].append([name, coordinates])
        count += 1
        # print(name, map, coordinates, playlists)
print()
print(f'{count} nades loaded\n')
# print(res0)
# assert 0
for res in res0:
    new_res = ''
    for i in res0[res]:
        new_res = new_res + \
            'script data.push(' + str(i).replace("'", '"') + ');' + '\n'

    template = open("nades.txt", "r").read()
    result = 'script data <- []\n' + new_res + '\n\n' + template

    csgo_dir = 'C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\csgo\cfg\\'
    f = open(csgo_dir + "n_" + res.lower() + ".cfg", "w", encoding="utf-8")
    # print(result)
    f.write(result)
    f.close()
time.sleep(3)
