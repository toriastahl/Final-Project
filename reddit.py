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

    count = 1
    # counter = 0
    for x in dates_comments:
        date = x[0]
        comments = x[1]
        discussion_id = count
        cur.execute("INSERT INTO Popularity (discussion_id, dates, comments) VALUES(?, ?, ?)", (discussion_id, date, comments))
        count += 1
        # counter += 1
        # if counter == 25:
        #     break
    conn.commit()


def makeVisualizations(cur):
    # Initialize the plotcd
    fig = plt.figure()
    ax1 = fig.add_subplot()   

    fig, ax1 = plt.subplots()
    width = 0.35
 
    dict1 = {}
    cur.execute("SELECT dates,comments FROM Popularity")
    info = cur.fetchall()
    for row in info:
        dict1[row[0]]=row[1]
    dates = []
    comments = []
    for key,value in dict1.items():
        key_split = key.split(',')
        dates.append(key_split[0])
        comments.append(value)
    
    dates = ['\n'.join(wrap(x, 100)) for x in dates]
    ax1.bar(dates,comments, width, color='blue')
    ax1.set(xlabel='Date', ylabel='Number of Comments', title='Popularity of Podcast Dates by Comments on Reddit')
    ax1.set_xticklabels(dates,FontSize='7',rotation=70)

    plt.show()

def vizualizationByComments(cur):
#percentage of posts above 100 comments
    total_posts = 0
    cur.execute("SELECT dates FROM Popularity")
    info = cur.fetchall()
    for x in info:
        total_posts += 1

    num_posts = 0
    cur.execute("SELECT comments FROM Popularity WHERE comments >=?", (50,))
    data = cur.fetchall()
    for y in data:
        num_posts += 1
    posts_below = total_posts - num_posts
    
    labels = ['Posts above 100 comments (%d)'%num_posts,'Posts below 100 comments (%d)'%posts_below]
    sizes = [percBelow,prcAbove]
    colors = ['red','blue']
    fig = plt.figure()
    ax1 = fig.add_subplot()
    plt.pie(sizes,  labels=labels, colors=colors,
        autopct='%1.1f%%', startangle=14
       )
    ax1.set(title='Discussion Posts Above 100 Comments %s Versus Below')
    plt.axis('equal')
    plt.show()


def main():
    data = getDates('FP_reddit.htm')
    cur, conn = setUpDatabase('JRP.db')
    setUpComments(data,cur,conn)

    #plot data
    # makeVisualizations(cur)
    vizualizationByComments(cur)

if __name__ == '__main__':
    main()
