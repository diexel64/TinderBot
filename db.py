from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import re, os, csv

# ADD POSSIBILITY TO SELECT TO KEYS TO EXTRACT

baseFolder = os.path.dirname(os.path.abspath(__file__)) 

# Functions #

def check_in_collection(c, to_check):
    client = MongoClient('localhost', 27017)
    db = client.tinder
    collection = db.get_collection(c)
    return collection.find_one({'name': to_check})

def add_to_mongo(c, dictionary):
    client = MongoClient('localhost', 27017)
    db = client.tinder
    collection = db.get_collection(c)
    collection.insert_one(dictionary)

def get_from_mongo(c):
    client = MongoClient('localhost', 27017)
    db = client.tinder
    collection = db.get_collection(c)
    nb = collection.find().count()
    all = collection.find({}, {'_id': 0, 'name':1, 'age':1, 'description':1})
    all = [x for x in all]
    all = pd.DataFrame.from_dict(all)
    all = all.replace('\n', ' | ', regex=True)
    return all, nb

def query_user(c, name):
    client = MongoClient('localhost', 27017)
    db = client.tinder
    collection = db.get_collection(c)
    res_username = collection.find({'name': name}, {'_id': 0, 'name':1, 'age':1, 'description':1, 'date':1})
    res_username = [x for x in res_username]
    res_username = pd.DataFrame.from_dict(res_username)
    res_username = res_username.replace('\n', ' | ', regex=True)
    return res_username

def query_word(c, words):
    client = MongoClient('localhost', 27017)
    db = client.tinder
    collection = db.get_collection(c)
    regx = words.replace(', ', '|').replace(',', '|')
    regx = regx.split('|')
    for x in regx:
        x = '\b' + x + '\b'
    regx = '|'.join(regx)
    res_word = collection.find({"description": {'$regex': '(?i)' + regx}}, {'_id': 0, 'name':1, 'age':1, 'description':1})
    nb = collection.find({"description": {'$regex': '(?i)' + regx}}).count()
    res_word = [x for x in res_word]
    res_word = pd.DataFrame.from_dict(res_word)
    res_word = res_word.replace('\n', ' | ', regex=True)
    return res_word, nb

def query_date(c, date):
    client = MongoClient('localhost', 27017)
    db = client.tinder
    collection = db.get_collection(c)
    date = datetime(int(date.split('/')[2]), int(date.split('/')[1]), int(date.split('/')[0]))
    res_date = collection.find({'date': {'$gt': date}}, {'_id': 0, 'name':1, 'age':1, 'description':1, 'date':1})
    nb = res_date.count()
    res_date = [x for x in res_date]
    res_date = pd.DataFrame.from_dict(res_date)
    res_date = res_date.replace('\n', ' | ', regex=True)
    return res_date, nb

def get_insta(c):
    client = MongoClient('localhost', 27017)
    db = client.tinder
    collection = db.get_collection(c)
    words = "insta, ig, inst, instagram"
    regx = words.replace(', ', '|').replace(',', '|')
    regx = regx.split('|')
    for x in regx:
        x = '\b' + x + '\b'
    regx = '|'.join(regx)
    res_word = collection.find({"description": {'$regex': '(?i)' + regx}}, {'_id': 0, 'name':1, 'age':1, 'description':1})
    res_word = [x for x in res_word]
    res_word = pd.DataFrame.from_dict(res_word)
    insta_regex = r'(?i)ig( *?)(:?)( *?).*\S+|(?i)inst( *?)(:?)( *?).*\S+|(?i)insta( *?)(:?)( *?).*\S+|(?i)instagram( *?)(:?)( *?).*\S+'
    instas = []
    for x in res_word['description']:
        x = x.replace('\n', ' | ')
        ig = re.match(insta_regex, x)
        if ig == None:
            pass
        else:
            try:
                igrm = ig.group(0).replace('  ', ' ').replace(':', ' ').replace('  ', ' ').replace('@', '').split(' ')[1]
                instas.append(igrm)
            except:
                igrm = ig.group(0)
                instas.append(igrm)
    with open(baseFolder + '\\Extractions\\_Insta.csv', 'w', newline='') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(instas)
    print(instas)
