import requests
import json
import sys

#get data for 100 most recent episodes
def episodes_search(id):
    baseurl = 'https://api.spotify.com/v1/shows/' + id + '/episodes'
    offset1 = 1
    param = {'limit':50,'offset':offset1, 'access_token':'BQAJ8UViPjldce4oXB4JmjBP-QlKvAxlMIj3HpeeZvclfZzEBQZTzLuaqvRBLmwcLq_KmoDHD5ihhSJkisfG3iwT-5KphYTKiwLRvU8JoD0q6FSYmAFvdgFr1UogVuBH28qXd7Mk6Qb6VY4226sguXKVIA'}
    response = requests.get(baseurl, params = param)
    jsonVersion = response.json()
    offset1 +=50
    id = '4rOoJ6Egrf8K2IrywzwOMk'
    baseurl = 'https://api.spotify.com/v1/shows/' + id + '/episodes'
    param = {'limit':50,'offset':offset1, 'access_token':'BQAJ8UViPjldce4oXB4JmjBP-QlKvAxlMIj3HpeeZvclfZzEBQZTzLuaqvRBLmwcLq_KmoDHD5ihhSJkisfG3iwT-5KphYTKiwLRvU8JoD0q6FSYmAFvdgFr1UogVuBH28qXd7Mk6Qb6VY4226sguXKVIA'}
    response2 = requests.get(baseurl, params = param)
    jsonVersion2 = response2.json()
    return (jsonVersion, jsonVersion2)

#get ID for each of 100 episodes
def get_ids(id):
    all_results = episodes_search(id)
    ids = []
    for x in all_results:
        for y in x['items']:
            new_id = y['id']
            ids.append(new_id)
    return ids

#use ID to get name and release date of each episode
def get_date_and_title(id):
    all_results = get_ids(id)
    info = []
    for x in all_results:
        base_url = 'https://api.spotify.com/v1/episodes/' + x
        param = {'access_token':'BQAJ8UViPjldce4oXB4JmjBP-QlKvAxlMIj3HpeeZvclfZzEBQZTzLuaqvRBLmwcLq_KmoDHD5ihhSJkisfG3iwT-5KphYTKiwLRvU8JoD0q6FSYmAFvdgFr1UogVuBH28qXd7Mk6Qb6VY4226sguXKVIA'}
        response = requests.get(base_url, params = param)
        jsonVersion = response.json()
        title = jsonVersion['name']
        date = jsonVersion['release_date']
        info.append((title, date))
    return info


print(get_date_and_title('4rOoJ6Egrf8K2IrywzwOMk'))

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpEpisodes(data, cur, conn):
    cur.execute('DROP TABLE IF EXISTS Episodes')
    cur.execute("CREATE TABLE Episodes (episode_id TEXT PRIMARY KEY, name TEXT, release_date TEXT)")
    conn.commit()

    count = 1
    for x in data:
        name = x[0]
        date = x[1]
        episode_id = count
        cur.execute("INSERT INTO Episodes (episode_id TEXT PRIMARY KEY, name TEXT, release_date TEXT) VALUES(?, ?, ?)", (episode_id, name, date))
        count += 1
    conn.commit()

def main():
    data = get_date_and_title('4rOoJ6Egrf8K2IrywzwOMk'
    cur, conn = setUpDatabase('episodes.db')
    setUpCategoriesTable(data, cur, conn)
    setUpRestaurantTable(data, cur, conn)
    conn.close()


if __name__ == "__main__":
    main()
    unittest.main(verbosity = 2)