import requests
import json
import sys
import os
import matplotlib
import sqlite3
import unittest
import matplotlib.pyplot as plt

#get data for 100 most recent episodes
def episodes_search(id, offset):
    token = 'BQD4wTxwnlzXeBfqifBA1YegzMl2fGlx3atht-DpIOA9N1ME5BCFOvxE5dYHqsTJ47k65z_rNqXRKLUPJ52SJ6-HEADUAsXyyNBvPw2cxv55yN1ijeT_Hdkahz0ZqTgT4wdme4uItqtYBPIN4G_Akz7WGw'
    baseurl = 'https://api.spotify.com/v1/shows/' + id + '/episodes'
    param = {'limit':25,'offset':offset, 'access_token':token}
    response = requests.get(baseurl, params = param)
    jsonVersion = response.json()
    return jsonVersion

#get ID for each of 100 episodes
def get_ids(id, offset):
    all_results = episodes_search(id, offset)
    ids = []
    for y in all_results['items']:
        new_id = y['id']
        ids.append(new_id)
    return ids

#use ID to get name and release date of each episode
def get_date_and_title(id,offset):
    all_results = get_ids(id, offset)
    info = []
    for x in all_results:
        base_url = 'https://api.spotify.com/v1/episodes/' + x
        param = {'access_token':'BQD4wTxwnlzXeBfqifBA1YegzMl2fGlx3atht-DpIOA9N1ME5BCFOvxE5dYHqsTJ47k65z_rNqXRKLUPJ52SJ6-HEADUAsXyyNBvPw2cxv55yN1ijeT_Hdkahz0ZqTgT4wdme4uItqtYBPIN4G_Akz7WGw'}
        response = requests.get(base_url, params = param)
        jsonVersion = response.json()
        title = jsonVersion['name']
        date = jsonVersion['release_date']
        info.append((title, date))
    return info


#print(get_date_and_title('4rOoJ6Egrf8K2IrywzwOMk'))

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpEpisodes(data, cur, conn):
    #cur.execute('DROP TABLE IF EXISTS Episodes')
    cur.execute("CREATE TABLE IF NOT EXISTS Spotify_Episodes (episode_id INTEGER PRIMARY KEY, name TEXT, release_date TEXT)")
    conn.commit()

    count = 1
    for x in data:
        # print(x)
        # print('\n')
        name = x[0]
        date = x[1]
        episode_id = count
        #Integer primary key NOT text
        cur.execute("INSERT OR IGNORE INTO Spotify_Episodes (episode_id, name, release_date) VALUES(?,?,?)", (episode_id, name, date))
        count += 1
    conn.commit()

def createPieChart(cur): 
    # Initialize the plotcd
    fig, ax1 = plt.subplots()
    l1 = []
    
    cur.execute('SELECT * FROM Spotify_Episodes')
    cur1 = cur.fetchall()
    for row in cur1:
        l1.append(row[1])
    reg = []
    special = []
    for name in l1:
        if name.startswith('#') == True:
            reg.append(name)
        else:
            special.append(name)
    labels = 'Regular Episodes', 'Special Episodes'
    sizes = [len(reg), len(special)]
    explode = (0,0)

    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',shadow=True, startangle=90)
    plt.title('Proportion of "Special Episodes" (episodes that are not numbered)')
    ax1.axis('equal')

    plt.show()

def main():
    cur, conn = setUpDatabase('JRP.db')
    try:
        cur.execute("select count(*) from Spotify_Episodes")  
        n = cur.fetchone()[0]
    except:
        n=0
    current_offset = n+1
    data = get_date_and_title('4rOoJ6Egrf8K2IrywzwOMk', current_offset)
    setUpEpisodes(data, cur, conn)

    #uncomment line below once desired amount of data has been gathered
    #createPieChart(cur)

    conn.close()


if __name__ == '__main__':
    main()
