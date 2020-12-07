from bs4 import BeautifulSoup
import requests
import re
import os
import json
import csv
import unittest
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from textwrap import wrap

#Dr. Ericson approved the .htm file to scrape Date of discussion and number of comments on that date in tuples
def getDates(filename):
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
    dates_comments = list(zip1)[:100]
    return dates_comments

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

#put 25 items into database at a time
def setUpComments(dates_comments, cur, conn):
    cur.execute('DROP TABLE IF EXISTS Popularity')
    cur.execute("CREATE TABLE Popularity (discussion_id TEXT PRIMARY KEY, dates TEXT, comments INTEGER)")

    # sorted_comments = sorted(dates_comments, key = lambda x: int(x[1]), reverse = True)
    # print(sorted_comments)

    #get max id from database
    # start = None
    # cur.execute("SELECT discussion_id FROM Popularity WHERE disucssion_id = (SELECT MAX(discussion_id) FROM Popularity)")
    # start = cur.fetchone()
    # if (start != None):
    #     start = start[0] + 1
    # else:
    #     start = 1

    count = 1
    for x in dates_comments:
        # for i in range(start-1):
        #     next(dates_comments)
        # row = next(dates_comments)
        # for row in dates_comments:
        date = x[0]
        comments = x[1]
        discussion_id = count
        cur.execute("INSERT INTO Popularity (discussion_id, dates, comments) VALUES(?, ?, ?)", (discussion_id, date, comments))
        count += 1
            #break at 25 entries
            # if (counter - 1) % 25 == 0:
            #     break
    conn.commit()

# def DateFormat(dates_commenets, cur, conn):
#     new_format = []
#     for x in dates_comments:
#         date = x[1]
#         for x in date:

def makeVisualizations(cur):
    #create graph
    # fig = plt.figure()
    # ax1 = fig.add_subplot()

    fig, ax1 = plt.subplots()
    N = 11
    width = 0.35
    ind = np.arange(N)
    # cur.execute("SELECT dates,comments FROM Popularity")
    # data = cur.fetchall()
    # dates = []
    # comments = []
    # for row in data:
    #     dates.append(row[0])
    #     comments.append(row[1])
    dict1 = {}
    cur.execute("SELECT dates,comments FROM Popularity")
    info = cur.fetchall()
    for row in info:
        dict1[row[0]]=row[1]
    dates = []
    comments = []
    for key,value in dict1.items():
        dates.append(key)
        comments.append(value)
    
    ax1.bar(dates,comments, width, color='blue')
    ax1.set_xticks(ind + width/ 2)
    ax1.set_xticklabels(("December", "November", "October","Septempter", "October"))
    ax1.autoscale_view()
    # plt.set_xticklabels(("December", "November", "October","Septempter", "October"))
    # plt.xticks(dates, comments, rotation=90)
    # comments=['\n'.join(wrap(x,16)) for x in comments]
    ax1.set(xlabel='Date', ylabel='Number of Comments', title='Popularity of Podcast Dates by Comments on Reddit')

    plt.show()

def main():
    data = getDates('FP_reddit.htm')
    cur, conn = setUpDatabase('JRP.db')
    setUpComments(data,cur,conn)

    #plot data
    makeVisualizations(cur)

if __name__ == '__main__':
    main()
