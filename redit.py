from bs4 import BeautifulSoup
import requests
import re
import os
import csv
import unittest
import sqlite3
import matplotlib.pyplot as plt

def getDates(filename): #how can I make it grab 100 entries/ load the whole page?
    #download as htm file to get all of the data
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), filename), 'r') as f:
        r = f.read()
    # soup = BeautifulSoup(r, 'html.parser')
    # r = requests.get('https://www.reddit.com/r/JoeRogan/search?q=general+discussion&sort=new&restrict_sr=on&t=all')
    soup = BeautifulSoup(r, 'html.parser')

    tags = soup.find_all("h3", class_ = "_eYtD2XCVieq6emjKBH3m")
    dates = []
    for x in tags:
        title = x.find('span').text.strip()
        if title.startswith("Daily General Discussion"):
            date = title.split('- ')[1]
            dates.append(date)
    
    tags2 = soup.find_all('span', class_='FHCV02u6Cp2zYL0fhQPsO')
    num_comments = []
    for each in tags2:
        info = each.text.strip()
        comments = info.split(' ')[0]
        num_comments.append(comments)

    zip1 = zip(dates, num_comments)
    dates_comments = list(zip1)
    print(dates_comments)
    return dates_comments

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpComments(dates_comments, cur, conn):
    cur.execute('DROP TABLE IF EXISTS Popularity')
    cur.execute("CREATE TABLE Popularity (discussion_id TEXT PRIMARY KEY, dates TEXT, comments INTEGER)")

    count = 1
    for x in dates_comments:
        date = x[0]
        comments = x[1]
        discussion_id = count
        cur.execute("INSERT INTO Popularity (discussion_id, dates, comments) VALUES(?, ?, ?)", (discussion_id, date, comments))
        count += 1
    conn.commit()

def main():
    data = getDates('FP_reddit.htm')
    cur, conn = setUpDatabase('Popularity.db')
    setUpComments(data,cur,conn)

if __name__ == '__main__':
    main()
