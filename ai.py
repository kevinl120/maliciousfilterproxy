#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Reads /data/data.cvs and uses logistic regression to classify malicious URLs

Original Code: http://fsecurify.com/using-machine-learning-detect-malicious-urls/
It has been slightly modified
"""

import numpy as np
import pandas as pd
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

def getTokens(input):
	tokensBySlash = str(input.encode('utf-8')).split('/')	#get tokens after splitting by slash
	allTokens = []
	for i in tokensBySlash:
		tokens = str(i).split('-')	#get tokens after splitting by dash
		tokensByDot = []
		for j in range(0,len(tokens)):
			tempTokens = str(tokens[j]).split('.')	#get tokens after splitting by dot
			tokensByDot = tokensByDot + tempTokens
		allTokens = allTokens + tokens + tokensByDot
	allTokens = list(set(allTokens))	#remove redundant tokens
	if 'com' in allTokens:
		allTokens.remove('com')	#removing .com since it occurs a lot of times and it should not be included in our features
	return allTokens

def TL():
	allurls = './data/data.csv'	#path to our all urls file
	allurlscsv = pd.read_csv(allurls,',',error_bad_lines=False)	#reading file
	allurlsdata = pd.DataFrame(allurlscsv)	#converting to a dataframe

	allurlsdata = np.array(allurlsdata)	#converting it into an array
	random.shuffle(allurlsdata)	#shuffling

	y = [d[1] for d in allurlsdata]	#all labels 
	corpus = [d[0] for d in allurlsdata]	#all urls corresponding to a label (either good or bad)
	vectorizer = TfidfVectorizer(tokenizer=getTokens)	#get a vector for each url but use our customized tokenizer
	X = vectorizer.fit_transform(corpus)	#get the X vector

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)	#split into training and testing set 80/20 ratio

	lgs = LogisticRegression()	#using logistic regression
	lgs.fit(X_train, y_train)
	print(lgs.score(X_test, y_test))	#pring the score. It comes out to be 98%
	return vectorizer, lgs
