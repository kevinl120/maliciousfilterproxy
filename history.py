#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analyzes Chrome history and populates MongoDB
"""

import ai
import os
import sqlite3
from pymongo import MongoClient
from shutil import copyfile

print("machine learning...")
vectorizer, lgs  = ai.TL()

def populateMongoDB():
    """ Top level function to be called by proxy.py to populate MongoDB """
    client = MongoClient()
    db = client.test_database
    collection = db.test_collection
    collection.delete_many({})
    print("populating mongoDB...")
    sites = readBrowserHistory()
    for site in sites:
        predict(db, site)
    client.close()
    
def readBrowserHistory():
    """ Reads Chrome browser history and returns set of URLs """    
    history_db = os.path.expanduser('~') + "/Library/Application Support/Google/Chrome/Default/history"
    # copy history_db to workaround Chrome history permissions
    copy_db = os.path.expanduser('~') + "/History"
    copyfile(history_db, copy_db)
    c = sqlite3.connect(copy_db)
    cursor = c.cursor()
    select_statement = "SELECT urls.url FROM urls, visits WHERE urls.id = visits.url;"
    cursor.execute(select_statement)
    results = cursor.fetchall()
    c.close()
    sites = set()
    for result in results:
        sites.add(parse(result[0]))
    return sites

def parse(url):
    """ Removes "http://", "https://" or "www" from a URL, ai module learns without prefixes """
    domain = url.replace("http://", "")
    domain = domain.replace("https://", "")
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def predict(db, site):
    """ Uses ai module to classify URLs, populates MongoDB, returns classification result """
    try:
        X_predict = [site]
        X_predict = vectorizer.transform(X_predict)
        y_Predict = lgs.predict(X_predict)
        print(site, y_Predict)	# print predicted values
        db.posts.replace_one({"url":site}, {"url":site, "score":y_Predict[0]},
                upsert=True);
        return y_Predict[0]
    except Exception as e:
        # ignore malformed URLs
        print("failed to predict ", site)
        pass

def isBadUrl(url):
    """
        Called by proxy.py to query a URL to classify it as good/bad
        Returns True for bad url, False otherwise
    """
    url = parse(url)
    client = MongoClient()
    db = client.test_database
    res = db.posts.find_one({ "url": url })
    if res:
        val = res['score']
    else:
        print("-----new url---", url)
        val = predict(db, url)
    if val == "bad":
        print("---bad url---", url)
        client.close()
        return True
    else:
        print("---good url---", url)
        client.close()
        return False
