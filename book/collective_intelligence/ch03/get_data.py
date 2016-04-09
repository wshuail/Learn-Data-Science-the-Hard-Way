#! /usr/bin/env python
# -*- coding: utf-8 -*-

from generatefeedvector import getwordcount

apcount = {}
wordcount = {}
feedlist = [line for line in file('feedlist.txt')]
for feedurl in feedlist:
    try:
        print 'feedurl: ', feedurl
        title, wc = getwordcount(feedurl)
        wordcount[title] = wc
        for word, count in wc.items():
            apcount.setdefault(word, 0)
            if count > 0:
                apcount[word] += 1
    except:
        print 'Failed to parse the feedurl.'

wordlist = []
for w, bc in apcount.items():
    frac = float(bc)/len(feedlist)
    if frac > 0.1 and frac < 0.5:
        wordlist.append(w)

out = file('blogdata.txt', 'w')
out.write('Blog')
for word in wordlist:
    out.write('\t%s' %word)
out.write('\n')

for blog, wc in wordcount.items():
    out.write(blog)
    for word in wordlist:
        if word in wc:
            out.write('\t%d' %wc[word])
        else:
            out.write('\t0')
    out.write('\n')
