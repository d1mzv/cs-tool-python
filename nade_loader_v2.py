import traceback
import sys
import json
import requests
import shutil


MONTHS = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apd', '05': 'May', '06': 'Jun',
          '07': 'Jul', '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}


def show_exception_and_exit(exc_type, exc_value, tb):
    traceback.print_exception(exc_type, exc_value, tb)
    input("")
    sys.exit(-1)


def read_config():
    f = open("config.txt")
    json_str = f.read()
    json_str_fixed = json_str.replace("\\", "\\\\")
    config = json.loads(json_str_fixed)
    config['cfg_path'] = config['steam_path'] + \
        '\\steamapps\\common\\Counter-Strike Global Offensive\\csgo\\cfg\\'
    return config


def get_data(url, headers, start_cursor=None):
    if start_cursor == None:
        payload = {"page_size": 100,
                   "sorts": [{"property": "Order", "direction": "ascending"}]}
    else:
        payload = {"page_size": 100, "start_cursor": start_cursor,
                   "sorts": [{"property": "Order", "direction": "ascending"}]}
    print('Fetching Nade Playlists...' + str(start_cursor))
    response = requests.post(url, json=payload, headers=headers)
    respons_json = json.loads(response.text)
    # print(respons_json)
    results = respons_json['results']
    if start_cursor != None:
        results = respons_json['results'][1:]
    if len(results) == 100:
        last_id = results[-1]['id']
        return (results + get_data(url, headers, start_cursor=last_id))
    else:
        return results


def adjust_coordinates(coordinates):
    coordinates = coordinates.split(' ')
    tmp = coordinates[3].split(';')
    new_y = str(round(float(tmp[0])-64, 6))
    tmp[0] = new_y
    tmp = ';'.join(tmp)
    coordinates[3] = tmp
    coordinates = ' '.join(coordinates)
    return coordinates


def process_data(data):
    processed_data = []
    for item in data:
        try:
            info = {}
            info['map'] = item['properties']['Map']['select']['name']
            # info['id'] = str(item['properties']['Order']['number']).zfill(2)
            info['id'] = item['properties']['Order']['number']
            if info['id'] is not None:
                info['id'] = str('%.1f' % info['id']).zfill(4)
            info['name'] = item['properties']['Name']['title'][0]['text']['content']
            if item['properties']['Throw Type']['select'] is not None:
                info['throw'] = item['properties']['Throw Type']['select']['name']
            else:
                info['throw'] = ''
            # if len(item['properties']['Note']['rich_text']) != 0:
            #     info['Note'] = item['properties']['Note']['rich_text'][0]['text']['content']
            # else:
            #     info['Note'] = ''
            info['coordinates'] = adjust_coordinates(
                item['properties']['Coordinates']['rich_text'][0]['text']['content'])

            info['playlists'] = []
            for i in range(len(item['properties']['Playlists']['multi_select'])):
                info['playlists'].append(item['properties']['Playlists']
                                         ['multi_select'][i]['name'])
            info['created_by'] = item['properties']['Created by']['created_by']['name']
            info['created_by'] = info['created_by'].split(
                ' ')[0][0] + '.' + info['created_by'].split(' ')[1]
            info['created_date'] = item['properties']['Created']['created_time'].split('T')[
                0]
            info['created_date'] = MONTHS[info['created_date'].split(
                '-')[1]] + ' ' + info['created_date'].split('-')[2]
            info['url'] = item['url']
            # print(json.dumps(data, indent=4))
            # print(item['url'])
            # assert 0
            processed_data.append(info)
        except IndexError:
            continue
    with open('data.txt', 'w') as fout:
        json.dump(processed_data, fout)


def generate_filters():
    f = open('data.txt')
    data = json.load(f)
    unique_maps = []
    unique_playlists = ['All']
    unique_created_by = ['All']
    for nade in data:
        if nade['map'] not in unique_maps:
            unique_maps.append(nade['map'])
        for playlist in nade['playlists']:
            if playlist not in unique_playlists:
                unique_playlists.append(playlist)
        if nade['created_by'] not in unique_created_by:
            unique_created_by.append(nade['created_by'])
    unique_maps.reverse()
    unique_maps = ['All'] + unique_maps
    # print(unique_maps)
    # print(unique_playlists)
    # print(unique_created_by)
    return unique_maps, unique_playlists, unique_created_by


def main():
    sys.excepthook = show_exception_and_exit
    config = read_config()
    url = f"https://api.notion.com/v1/databases/{config['db_id']}/query"
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28",
        "content-type": "application/json",
        "authorization": f"Bearer {config['token']}"
    }
    data = get_data(url, headers)
    processed_data = process_data(data)


def load():
    f = open('data_filtered.txt')
    data_filtered = json.load(f)
    result = ''
    for nade in data_filtered:
        command = f"say {nade['id']} {nade['name']}"
        if nade['throw'] != '':
            command += f" [{nade['throw']} Throw]"
        coordinate = nade['coordinates']
        result += 'script data.push(' + str([command, coordinate]).replace("'",
                                                                           '"') + ');' + '\n'
    template = open("nades.txt", "r").read()
    result = 'script data <- []\n' + result + '\n\n' + template
    config = read_config()
    f = open(config['cfg_path'] + "n_selected.cfg", "w", encoding="utf-8")
    f.write(result)
    f.close()
    if config['copy_prac_cfg']:
        shutil.copy("prac.cfg", config['cfg_path'] + "prac.cfg")


if __name__ == "__main__":
    main()
