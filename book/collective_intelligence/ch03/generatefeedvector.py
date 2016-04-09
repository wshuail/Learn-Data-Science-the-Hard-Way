#! /usr/bin/env python
# -*- coding: utf-8 -*-

import feedparser
import re

def getwordcount(url):
    # parse the feed
    d = feedparser.parse(url)
    wc = {}
    
    # loop over all entries
    for e in d.entries:
        if 'summary' in e:
            summary = e.summary
        else:
            summary = e.description
            
        # Extract a list of words
        words = getwords(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
    return getattr(d.feed, 'title', 'Unknown title'), wc

def getwords(html):
    # remove all the html tags
    txt = re.compile(r'<[^>]+>').sub('', html)
    # split words by all non-alpha characters
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    # convert to lowcase
    return [word.lower() for word in words if word != '']

