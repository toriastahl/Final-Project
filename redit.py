from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest

def getDates():
    r = requests.get('https://www.reddit.com/r/JoeRogan/search?q=general+discussion&sort=new&restrict_sr=on&t=all')
    soup = BeautifulSoup(r.content, 'html.parser')

    tags = soup.find_all("div", class_ = 'QBfRw7Rj8UkxybFpX-USO')
    dates = []
    num_comments = []
    for x in tags:
        title = x.find('h3', class_ = "_eYtD2XCVieq6emjKBH3m")
        for each in title:
            info = each.find('span').text.strip()
            date = info.split('- ')[1]
            dates.append(date)
        data = x.find('div', class_ = '_3-miAEojrCvx_4FQ8x3P-s ssgs3QQidkqeycI33hlBa')
        for each in data:
            info = each.find('span', class_ = 'FHCV02u6Cp2zYL0fhQPsO').text.strip()
            comments = info.split(' ')[0]
            num_comments.append(comments)
    zip1 = zip(dates, num_comments)
    dates_comments = list(zip1)
    return dates_comments

# def setUpDatabase(db_name):
#     path = os.path.dirname(os.path.abspath(__file__))
#     conn = sqlite3.connect(path+'/'+db_name)
#     cur = conn.cursor()
#     return cur, conn

def setUpComments(data, cur, conn):
    cur.execute('DROP TABLE IF EXISTS Popularity')
    cur.execute("CREATE TABLE Popularity (discussion_id TEXT PRIMARY KEY, dates TEXT, comments INTEGER)")
    conn.commit()

    count = 1
    for x in data:
        date = x[0]
        comments = x[1]
        discussion_id = count
        cur.execute("INSERT INTO Popularity (discussion_id, dates, comments) VALUES(?, ?, ?)", (disucssion_id, date, comments))
        count += 1
    conn.commit()

data = getDates()
print(data)
