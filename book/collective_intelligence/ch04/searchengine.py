#! /usr/bin/env python
import urllib2
import re
from bs4 import BeautifulSoup
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite

# create a list of words to ignore
ignorewords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

class crawler():
    #Initialize the crawler with the name of the database
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # Auxilliary function for getting an entry id and adding
    # it if it's not present
    def getentryid(self, table, field, value, createnew = True):
        cur = self.con.execute("\
                select rowid from %s where %s = '%s'" %(table, field, value))
        res = cur.fetchone()
        if res == None:
            cur = self.con.execute("\
                    insert into %s (%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    # Index and individual page
    def addtoindex(self, url, soup):
        if self.isindexed(url): return
        print 'Indexing %s' % url

        # Get the individual words
        text = self.gettextonly(soup)
        words = self.separatewords(text)

        # Get the url id
        urlid = self.getentryid('urllist', 'url', url)

        # Link each word to this url
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("\
                    insert into wordlocation(urlid, wordid, location)\
                            values (%d, %d, %d)" % (urlid, wordid, i))

    # Extract the text from an HTML page(no tags)
    def gettextonly(self, soup):
        v = soup.string
        if v == None:
            v = soup.contents
            resulttext = ''
            for t in v:
                subtext = self.gettextonly(t)
                resulttext += subtext + '\n'
            return resulttext
        else:
            return v.strip()

    # Separate the words by any non-whitespace character
    def separatewords(self, text):
        spliter = re.compile('\\W*')
        return [s.lower() for s in spliter.split(text) if s != '']

    # Return True if this url is already indexed
    def isindexed(self, url):
        print self.con.execute("select * from urllist")
        u = self.con.execute("select rowid from urllist where url = '%s'" % url).fetchone()
        if u != None:
            # Check if it has been crawled
            v = self.con.execute("\
                    select * from wordlocation where urlid = %d\
                    " % u[0]).fetchone()
            if v != None:
                return True
        return False

    # Add a link between two pages
    def addlinkref(self, urlFrom, urlTo, linkText):
        words = self.separatewords(linkText)
        fromid = self.getentryid('urllist', 'url', urlFrom)
        toid = self.getentryid('urllist', 'url', urlTo)
        if fromid == toid: return
        cur = self.con.execute("\
                insert into link(fromid, toid) values (%d, %d)\
                " %(fromid, toid))
        linkid = cur.lastrowid
        for word in words:
            if word in ignorewords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("\
                    insert into linkwords(linkid, wordid) values (%d, %d)\
                    " %(linkid, wordid))

    # Starting with a list of pages, do a breadth
    # first search to the given depth, indexing pages as we go
    def crawl(self, pages, depth = 2):
        for i in range(depth):
            newpages = set()
            for page in pages:
                try:
                    c = urllib2.urlopen(page)
                except:
                    print 'Could not open %s' % page
                    continue                  
                soup = BeautifulSoup(c.read())
                # self.addtoindex(page, soup)

                links = soup('a')
                for link in links:
                    if ('href' in dict(link.attrs)):
                        url = urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        url = url.split('#')[0] # remove location partion

                        if url[0: 4] == 'http' and not self.isindexed(url):
                            newpages.add(url)

                        linkText = self.gettextonly(link)
                        self.addlinkref(page, url, linkText)

                self.dbcommit()

            pages = newpages

    # Create the database tables
    def createindextables(self):
        self.con.execute('create table if not exists urllist(url)')
        self.con.execute('create table if not exists wordlist(word)')
        self.con.execute('create table if not exists wordlocation(urlid, wordid, location)')
        self.con.execute('create table if not exists link(fromid integer, toid integer)')
        self.con.execute('create table if not exists linkwords(wordid, linkid)')
        self.con.execute('create index if not exists wordidx on wordlist(word)')
        self.con.execute('create index if not exists urlidx on urllist(url)')
        self.con.execute('create index if not exists wordurlidx on wordlocation(wordid)')
        self.con.execute('create index if not exists urltoidx on link(toid)')
        self.con.execute('create index if not exists urlfromidx on link(fromid)')
        self.dbcommit()

class searcher():
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    def getmatchrows(self, q):
        # String to build the query
        fieldlist = 'w0.urlid'
        tablelist = ''
        clauselist = ''
        wordids = []

        # split the words by space
        words = q.split(' ')
        tablenumber = 0

        for word in words:
            # Get the wordid
            print word
            wordrow = self.con.execute("\
            select rowid from wordlist where word = '%s'\
            " % word).fetchone()

            if wordrow != None:
                wordid = wordrow[0]
                print wordrow[0]
                wordids.append(wordid)

                if tablenumber > 0:
                    tablelist += ','
                    clauselist += ' and '
                    clauselist += 'w%d.urlid = w%d.urlid and ' %(tablenumber - 1, tablenumber)
                fieldlist += ', w%d.location' % tablenumber
                tablelist += 'wordlocation w%d' % tablenumber
                clauselist += 'w%d.wordid = %d' % (tablenumber, wordid)
                tablenumber += 1
                print 'fieldlist: ', fieldlist
                print 'tablelist: ', tablelist
                print 'clauselist: ', clauselist

        # Create the query from separate parts
        fullquery = 'select %s from %s where %s' % (fieldlist, tablelist, clauselist)
        cur = self.con.execute(fullquery)
        print 'cur: ', cur
        rows = [row for row in cur]

        return rows, wordids

    def getscoredlist(self, rows, wordids):
        totalscores = dict([(row[0], 0) for row in rows])

        # This is where you will later put the scoring function
        weights = [(1.0, self.locationscore(rows)),
                (1.0, self.frequencyscore(rows)),
                (1.0, self.pagerankscore(rows)),
                (1.0, self.linktextscore(rows))]

        for (weight, scores) in weights:
            for url in totalscores:
                totalscores[url] += weight * scores[url]

        return totalscores

    def geturlname(self, id):
        return self.con.execute("\
                select url from urllist where rowid = %d\
                " % id).fetchone()[0]

    def query(self, q):
        rows, wordids = self.getmatches(q)
        scores = self.getscoredlist(rows, wordids)
        rankedscores = sorted([(score, url) for (url, score) in scores.items()], reverse = 1)
        for (score, urlid) in rankedscores[1: 10]:
            print '%f\t%s' % (score, self.geturlname(urlid))
        # return wordids, [r[i] for r in rankedscores[0: 10]]

    def normalizescores(self, scores, smallIsBetter = 0):
        vsmall = 0.00001 # Avoid division by zero errors
        if smallIsBetter:
            minscore = min(scores.values())
            return dict([(u, float(minscore)/max(vsmall, 1)) for (u, l) in scores.items()])
        else:
            maxscore = max(scores.values())
            if maxscore == 0:
                maxscore = vsmall
            return dict([(u, float(c)/maxscore) for (u, c) in scores.items()])

    def frequencyscore(self, rows):
        contents = dict([(row[0], 0) for row in rows])
        for row in rows:
            contents[row[0]] += 1
        return self.normalizescores(counts)

    def locationscore(self, rows):
        locations = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1: ])
            if loc < locations[row[0]]:
                locations[row[0]] = loc 
        return self.normalizescores(locations, smallIsBetter = 1)

    # weights = [(1.0, self.locationscore(rows))]

    def worddistance(self, rows):
        # If there's only one word, everyone wins
        if len(range(rows)) < 2:
            return dict([(row[0], 1.0) for row in rows])

        # Initialize the dictionary with large value
        mindistance = dict([(row[0], 1000000) for row in rows])

        for row in rows:
            dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
            if dist < mindistance[row[0]]:
                mindistance[row[0]] = dist 
        return self.normalizescores(mindistance, smallIsBetter = 1)

    def inboundlinkscore(self, rows):
        uniqueurls = set([row[0] for row in rows])
        inboundcount = dict([(u, self.con.execute("\
            select count(*) from link where toid = %d\
            " % u).fieldlist()[0]) for u in uniqueurls])
        return self.normalizescores(inboundcount)

    def calculatepagerank(self, iterations = 20):
        # clear out the current pagerank tables
        self.con.execute("drop table if exists pagerank")
        self.con.execute("create table pagerank(urlid primary key, score)")

        # Initialize every url with a pagerank of 1
        self.exe.execute("insert into pagerank select rowid, 1.0 from urllist")
        self.dbcommit()

        for i in range(iterations):
            print "Iteration %d" % (i)
            for (urlid, ) in self.con.execute("select distinct fromid from link where toid = %d" % urlid):

                # Get the PageRank of the linker
                linkingpr = self.con.execute("select score from pagerank where urlid = %d" % linker).fetchone()[0]

                # Get the total number of link from the linker
                linkingcount = self.con.execute("\
                    select count(*) from link where urlid = %d" % linker).fetchone()[0]
                pr += 0.85 * (linkingpr/linkingcount)
        self.con.execute("\
                update pagerank set score = %f where urlid = %d" %(pr, urlid))
        self.dbcommit()

    def pagerankscore(self, rows):
        pageranks = dict([(row[0], self.con.execute("\
            select score from pagerank where urlid = %d" % row[0]).fetchone()[0]) for row in rows])
        maxrank = max(pagerank.values())
        normalizescores = dict([(u, float(l)/maxrank) for (u, l) in pageraaks.items()])
        return normalizescores

    def linktextscore(self, rows, wordids):
        linkscores = dict([(row[0], 0) for row in rows])
        for wordid in wordids:
            cur = self.con.execute("\
                    select link.fromid, link.toid from linkwords, link where wordid = %d and linkwords.linkid = link.rowid" % wordid)
            for toid in linkscores:
                pr = self.con.execute("\
                        select score from pagerank where urlid = %d\
                        " % fromid).fetchone()[0]
                linkscore[toid] += pr 

        maxscore = max(linkscores.values())
        normalizescores = dict([(u, float(l)/maxscore) for (u, l) in linkscores.items()])
        return normalizescores




