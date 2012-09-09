#!/usr/bin/python

from ftmdb import *
import optparse
import sqlite3

class Graph(object):
    def __init__(self):
        self.graph = {}
        pass

    def add(self, f, t, v):
        if f not in self.graph: self.graph[f] = {}
        g = self.graph[f]
        if t not in g: g[t] = 0
        g[t] += v
        pass

    def keys(self):
        return self.graph.keys()

    def get(self, f, t):
        if f not in self.graph: return 0
        g = self.graph[f]
        if t not in g: return 0
        return g[t]

    def edges(self, f):
        if f not in self.graph: return []
        return self.graph[f].keys()

    def is_singleton(self, f):
        if f not in self.graph: return False
        return len(self.graph[f].keys()) == 1
    
    def singleton(self, f):
        return self.graph[f].keys()[0]

def main():
    parser = optparse.OptionParser(usage='%prog [options]')
    parser.add_option("-f", "--file", default='contributions.sqlite',
                      help='Read database file FILE')
    (options,args) = parser.parse_args()
    if len(args) != 0:
        parser.error("No command-line arguments accepted")
        pass
    db = sqlite3.connect(options.file)
    q = ContributionsFEC(db)

    # Build a graph of contributors to recipients.
    # graph is a dictionary keyed on contributor.
    # Its values are dictionaries based on recipient.
    # *Its* values are dollar amounts.
    contributors = Graph()
    recipients = Graph()
    def add_row(row):
        contributors.add(row[0], row[1], float(row[2]))
        recipients.add(row[1], row[0], float(row[2]))
        pass
    q._execute("SELECT contributor_name, recipient_name, amount " +
               "FROM " + q.table + " " +
               "WHERE contributor_type='C'",
               (), add_row)

    contributor_names = contributors.keys()
    contributor_names.sort()

    print "Organizations that only give to themselves:"
    for c in contributor_names:
        if (c in recipients.keys() and contributors.is_singleton(c) and
            contributors.singleton(c) == c):
            print "  {0}".format(c)
            pass
        pass

    print
    print "Contributors who are recipients with only one downstream recipient:"
    for c in contributor_names:
        if (c in recipients.keys() and contributors.is_singleton(c) and
            contributors.singleton(c) == c):
            print "  {0}: {1}".format(c, contributors.singleton(c))
            pass
        pass

    print
    print "Contributors with only one recipient and who aren't recipients themselves:"
    for c in contributor_names:
        if c not in recipients.keys() and contributors.is_singleton(c):
            print "  {0}: {1}".format(c, contributors.singleton(c))
            pass
        pass

    print
    print "Contributors with multiple recipients:"
    for c in contributor_names:
        if not contributors.is_singleton(c):
          print "  {0} ({1})".format(c, len(contributors.edges(c)))
          pass
        pass
    pass

if __name__ == '__main__':
    main()
    pass
