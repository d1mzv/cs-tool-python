import sys
import json
import requests
import shutil


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("")
    sys.exit(-1)


sys.excepthook = show_exception_and_exit

while True:
    f = open("config.txt")
    json_str = f.read()
    json_str_fixed = json_str.replace("\\", "\\\\")
    config = json.loads(json_str_fixed)

    TOKEN = config['token']
    DB_ID = config['db_id']
    CFG_PATH = config['steam_path'] + \
        '\\steamapps\\common\\Counter-Strike Global Offensive\\csgo\\cfg\\'
    PLAYLIST = config['playlist']
    COPY_PRAC = config['copy_prac_cfg']

    url = f"https://api.notion.com/v1/databases/{DB_ID}/query"

    payload = {"page_size": 100,
               "sorts": [{"property": "Order", "direction": "ascending"}]
               #  {"property": "Map", "direction": "ascending"}],
               #    "filter": {"and": [{"property": "Map", "rich_text": {"contains": "Dust"}}, {{"property": "Map", "rich_text": {"contains": "Dust"}}}]}
               }
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {TOKEN}"
    }

    print('Fetching Nade Playlists...')

    response = requests.post(url, json=payload, headers=headers)
    respons_json = json.loads(response.text)
    results = respons_json['results']

    if len(respons_json['results']) == 100:
        last_id = results[-1]['id']
        payload = {"page_size": 100, "start_cursor": last_id,
                   "sorts": [{"property": "Order", "direction": "ascending"}]}
        response = requests.post(url, json=payload, headers=headers)
        respons_json = json.loads(response.text)
        results = results + respons_json['results'][1:]
    res0 = {}
    count = 0
    for result in results:
        if len(result['properties']['Name']['title']) == 0 or len(result['properties']['Coordinates']['rich_text']) == 0:
            continue

        id = str(result['properties']['Order']['number'])
        name = result['properties']['Name']['title'][0]['text']['content']
        name = 'say ' + id + '. ' + name
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
        if (PLAYLIST in playlists or PLAYLIST == ''):
            if map not in res0:
                res0[map] = []
            res0[map].append([name, coordinates])
            count += 1

    print(f'Done, {count} nades loaded')

    for res in res0:
        new_res = ''
        for i in res0[res]:
            new_res = new_res + \
                'script data.push(' + str(i).replace("'", '"') + ');' + '\n'

        template = open("nades.txt", "r").read()
        result = 'script data <- []\n' + new_res + '\n\n' + template

        f = open(CFG_PATH + "n_" + res.lower() + ".cfg", "w", encoding="utf-8")
        f.write(result)
        f.close()
    if COPY_PRAC:
        shutil.copy("prac.cfg", CFG_PATH + "prac.cfg")
    input("\nPress Enter to Refresh\n")
