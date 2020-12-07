import re
import os
import numpy as np
import sqlite3
import youtube_dl
from tabulate import tabulate
import csv
import pandas
import unittest
import matplotlib
import matplotlib.pyplot as plt

#set up database
def readDataFromFile(filename):
    full_path = os.path.join(os.path.dirname(__file__), filename)
    f = open(full_path, encoding='utf-8')
    file_data = f.read()
    f.close()
    return file_data

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# #below is all the functions to pull data from youtube (when the videos use to exist...)
# def getData():
#     ydl = youtube_dl.YoutubeDL({'outtmpl': '%(id)s%(ext)s'})

#     with ydl:
#         ydl.params.update(ignoreerrors=True) #Dom Irrera's podcast is blocked on Copyright grounds
#         result = ydl.extract_info(
#             'https://www.youtube.com/playlist?list=UUzQUP1qoWDoEbmsQxvdjxgQ',
#             download = False # We just want to extract the info
#         )
#     id = []
#     titles = []
#     views = []
#     likes = []
#     dislikes = []
#     avg_rating = []
#     guest_names = []
#     for t in range(len(result['entries'])):
#         try:
#             id.append(result['entries'][t]['id'])
#             titles.append(result['entries'][t]['title'])
#             views.append(result['entries'][t]['view_count'])
#             likes.append(result['entries'][t]['like_count'])
#             dislikes.append(result['entries'][t]['dislike_count'])
#             avg_rating.append(result['entries'][t]['average_rating'])
#         except:
#             pass
#     dir = os.path.dirname('youtube_data.csv')
#     out_file = open(os.path.join(dir, 'youtube_data.csv'), "w")

#     #get guest names from titles
#     regex = r'^.*?#.*?(-|with)+\s*?(?P<name>.*?)(\(.*?\))?$'
#     pattern = re.compile(regex)
#     #go through each title and use refex to get name
#     for title in titles:
#         try:
#             guests = re.split(',|&', pattern.match(title).group('name'))
#             for person in guests:
#                 guest_names.append(person.strip()) 
#         except:
#             guest_names.append('N/A')
#     #write data to csv file
#     with open('youtube_data.csv') as f:
#         csv_writer = csv.writer(out_file, delimiter=",", quotechar='"')
#         csv_writer.writerow(["id","video_id","title","view","likes","dislikes","rating","guestid"])
#         for x in range(len(titles)):
#             try:
#                 cur.execute('SELECT id FROM JRP_guest_count WHERE name = ?',(guest_names[x], ))
#                 guestid = cur.fetchone()[0]
#             except:
#                 guestid=-1
#             csv_writer.writerow([id[x],titles[x],views[x],likes[x],dislikes[x],avg_rating[x],guestid])
#     out_file.close()

#function to put 25 items from csv file to database
def uploadDataJRE(cur,conn):
    cur.execute('''CREATE TABLE IF NOT EXISTS JRP (id INTEGER UNIQUE, video_id TEXT, title TEXT, views INTEGER, likes INTEGER, dislikes INTEGER, rating REAL, guestid INTEGER)''')
    # Pick up where we left off
    start = None
    #select max id (last one put in db)
    cur.execute('SELECT id FROM JRP WHERE id = (SELECT MAX(id) FROM JRP)')
    start = cur.fetchone()
    if (start!=None):
        start = start[0] + 1
    else:
        start = 1
    #open file to read data
    with open('youtube_data.csv','r') as f:
        csvreader = csv.reader(f)
        for i in range(start-1): # count and skip past rows alredy in file
            next(csvreader)
        row = next(csvreader)
        for row in csvreader:
            cur.execute("INSERT OR IGNORE INTO JRP (id,video_id,title,views,likes,dislikes,rating,guestid) VALUES (?,?,?,?,?,?,?,?)",(start,row[0],row[1],row[2],row[3],row[4],row[5],-1))
            start=start + 1
            #if 25 were added break
            if (start-1) % 25 == 0:
                break
    conn.commit()

#returns list of names from titles that are in the format (Joe Rogan Experience #1560 - Mike Baker)         
def getNames(cur):
    names = []
    cur.execute('SELECT title FROM JRP')
    titles = cur.fetchall()
    regex = r'^.*?#.*?(-|with)+\s*?(?P<name>.*?)(\(.*?\))?$'
    pattern = re.compile(regex)
    #go through each title and use regex to get name only getting section name
    for title in titles:
        try:
            title = title[0]
            #guests = re.findall(regex,title)
            guests = re.split(',|&', pattern.match(title).group('name'))
            for person in guests:
                names.append(person.strip()) 
        except:
            #title is irregular or a small highlight clip
            pass
    return names

#count names and remove singles of guests
def countNames(names):
    returndict = dict()
    for person in names: 
        returndict[person] = returndict.get(person,0)+1
    return sorted(returndict.items(), key=lambda x: x[1], reverse=True)
    


#puts the names into file
def printNamesPretty(counts,file):
    dir = os.path.dirname(file)
    out_file = open(os.path.join(dir, file), "w")
    with open(file) as f:
        csv_writer = csv.writer(out_file, delimiter=",", quotechar='"')
        csv_writer.writerow(["Guest","Number Apperances"])
        for x in counts:
            csv_writer.writerow([x[0], x[1]])

#make seperate table for guests that appear more than once
def putNamesInData(counts,cur,conn):
    cur.execute('DROP TABLE IF EXISTS JRP_guest_count')
    cur.execute('CREATE TABLE JRP_guest_count (id INTEGER PRIMARY KEY, name TEXT, apperances INTEGER)')
    y=1
    for x in counts:
        cur.execute("INSERT INTO JRP_guest_count (id,name,apperances) VALUES (?,?,?)",(y,x[0],x[1]))
        y+=1
    conn.commit()

def fillGuestId(cur,conn):
    regex = r'^.*?#.*?(-|with)+\s*?(?P<name>.*?)(\(.*?\))?$'
    pattern = re.compile(regex)
    cur.execute("""SELECT * FROM JRP""")
    results = cur.fetchall()
    for row in results:
        id=row[0] 
        title = row[2]
        
        names=[]
        try:
            guests = re.split(',|&', pattern.match(title).group('name'))
            for person in guests:
                names.append(person.strip())
        except:
            pass
        if(len(names)==1):
            cur.execute("SELECT id FROM JRP_guest_count WHERE JRP_guest_count.name = ?" , (names[0],))
            guestid = cur.fetchone()
            cur.execute("UPDATE JRP SET guestid = ? WHERE id = ?",(guestid[0],id))
        else:
            guestid=0
         
            #put guest id of 0 for exceptions of multiple people on episode, or a special clip
            cur.execute("UPDATE JRP SET guestid = ? WHERE id = ?",(guestid,id))
    conn.commit()

def barChartGuests(cur):
    # Initialize the plotcd
    fig, ax1 = plt.subplots()
    l1 = dict()
    #select top 8 guests already in order 
    cur.execute('SELECT * FROM JRP_guest_count LIMIT 8')
    cur1 = cur.fetchall()
    for row in cur1:
        l1[row[1]]=row[2]
    

    #(names,values)
    people = []
    apperances=[]
    for key,value in l1.items():
        people.append(key)
        apperances.append(value)
   
    ax1.bar(people,apperances,align='center', alpha=0.5)
    plt.title('8 Most Common Guests on JRP')
    plt.xlabel('Guest Name')
    plt.ylabel('Apperances')

    # #make plot with Jack Dorsey episode show likes to dislikes ratio
    # ax2 = fig.add_subplot(182)

    # #find top 8 disliked episodes
    # l1 = list()
    # cur.execute('SELECT name,apperances FROM JRP_guest_count LEFT JOIN Categories ON Restaurants.category_id=Categories.id WHERE Restaurants.rating >= ? AND Categories.title == ? ',(rating,category))
    # for row in cur:
    #     l1.append(row)
    # return l1

    # #(names,values)
    # ax1.bar([l1[0][0],l1[1][0],l1[2][0],l1[3][0],l1[4][0],l1[5][0],l1[6][0],l1[7][0]],[l1[0][1],l1[1][1],l1[2][1],l1[3][1],l1[4][1],l1[5][1],l1[6][1],l1[7][1]])
    # ax1.title('8 Most Common Guests on JRP')
    # ax1.xlabel('Guest Name')
    # ax1.ylabel('Apperances')

    # Show the plot
    plt.show()


def main():
    #database set up and add 25 at a time
    #PUT AT LEAST 200 PEOPLE BEFORE GETTING APPERANCES/GUEST NAMES BELOW 
    cur, conn = setUpDatabase('JRP.db')
    uploadDataJRE(cur,conn)


    #getting the names and counts of 
    # names = getNames(cur)   
    # countedNames = countNames(names)
    # printNamesPretty(countedNames, 'fileOutPutGuests.txt')
    # putNamesInData(countedNames,cur,conn)

    #uncomment when done making guest ID table and insert common key
    #fillGuestId(cur,conn)

    #plot data
    #barChartGuests(cur)

#help resources 
    #https://stackoverflow.com/questions/29582736/python3-is-there-a-way-to-iterate-row-by-row-over-a-very-large-sqlite-table-wi
    #https://stackoverflow.com/questions/26464567/csv-read-specific-row
    #https://stackoverflow.com/questions/3024546/change-one-cells-data-in-mysql
if __name__ == '__main__':
    main()
