#! /usr/bin/env python
from math import tanh
from pysqlite2 import dbapi2 as sqlite

class searchnet():
    def __init__(self, dbname):
        self.con = sqlite.connect(dbname)

    def __del__(self):
        self.con.close()

    def __maketables(self):
        self.con.execute("create table if not exists hiddennode(create_key)")
        self.con.execute("create table if not exists wordhidden(fromid, toid, strength)")
        self.con.execute("create table if not exists hiddenurl(fromid, toid, strength)")
        self.con.commit()


    def getstrength(self, fromid, toid, layer):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'

        res = self.con.execute("\
                select strength from %s where fromid = %d and toid = %d" %(table, fromid, toid)).fetchone()

        if res == None:
            if layer == 0:
                return -2
            if layer == 1:
                return 0

        return res[0]

    def setstrength(self, fromid, toid, layer, strength):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'

        res = self.con.execute("\
                select rowid from %s  where fromid = %d and toid = %d" %(table, fromid, toid)).fetchone()

        if res == None:
            self.con.execute("\
                    insert into %s (fromid, toid, strength) values (%d, %d, %f)" %(table, fromid, toid, strength))
        else:
            rowid = res[0]
            self.con.execute("\
                    update %s set strength = %f where rowid = %d" %(table, strength, rowid))

    def generatehiddennode(self, wordids, urls):
        if len(wordids) > 3:
            return None
        # check if we already created a node for this set of words
        createkey = '_'.join(sorted([str(wi) for wi in wordids]))
        res = self.con.execute("\
                select rowid from hiddennode where create_key = '%s'" % createkey).fetchone()

        # if not, create it
        if res == None:
            cur = self.con.execute("\
                    insert into hiddennode (create_key) values ('%s')" % createkey)
            hidderid = cur.lastrowid

            # puts in some default weights
            for wordid in wordids:
                self.setstrength(wordid, hidderid, 0, 1.0/len(wordids))
            for urlid in urls:
                self.setstrength(hidderid, urlid, 1, 0.1)
            self.con.commit()

    def getallhiddenids(self, wordids, urlids):
        l1 = {}
        for wordid in wordids:
            cur = self.con.execute("\
                    select toid from wordhidden where fromid = %d" % wordid)
            for row in cur: 
                l1[row[0]] = 1
        for urlid in urlids:
            cur = self.con.execute("\
                    select fromid from hiddenurl where toid = %d" % urlid)
            for row in cur:
                l1[row[0]] = 1
        return l1.keys()


    def setupnetwork(self, wordids, urlids):
        # value list
        self.wordids = wordids
        self.hiddenids = self.getallhiddenids(wordids, urlids)
        self.urlids = urlids

        # node output
        self.ai = [1.0]*len(self.wordids)
        self.ah = [1.0]*len(self.hiddenids)
        self.ao = [1.0]*len(self.urlids)

        # create weight matrix
        self.wi = [[self.getstrength(wordid, hidderid, 0)
            for hidderid in hiddenids]
            for wordid in wordids]
        self.wo = [[self.getstrength(hidderid, urlid, 1)
            for urlid in self.urlids]
            for hidderid in self.hiddenids]

    def feedforward(self):
        # The only input are the query words 
        for i in range(len(self.wordids)):
            self.ai[i] = 1.0
        
        # hidden activitions
        for j in range(len(self.hiddenids)):
            sum = 0.0
            for i in range(len(self.wordids)):
                sum += self.ai[i] * self.wi[i][j]
            self.ah[j] = tanh(sum)

        # output activitions
        for k in range(len(self.urlids)):
            sum = 0.0
            for j in range(len(self.hiddenids)):
                sum += self.ah[j] * self.wo[j][k]
            self.ao[k] = tanh(sum)
        return self.ao[:]

    def getresult(self, wordids, urlids):
        self.setupnetwork(wordids, urlids)
        return self.feedforward()



            



