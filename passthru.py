#!/usr/bin/python

from ftmdb import *
import optparse
import sqlite3

class Graph(object):
    """A directed graph."""
    def __init__(self):
        self.graph = {}
        pass

    def add(self, f, t, v):
        """Add a from-to edge to the graph with value 'v'.  If there is
        already an edge in the graph, increase its value by 'v'."""
        if f not in self.graph: self.graph[f] = {}
        g = self.graph[f]
        if t not in g: g[t] = 0
        g[t] += v
        if g[t] == 0: self.remove(f, t)
        pass

    def remove(self, f, t):
        """Remove a from-to edge from the graph."""
        if f not in self.graph: return
        g = self.graph[f]
        del g[t]
        if len(g) == 0: del self.graph[f]
        return

    def self_loops(self):
        """Return a list of node names such that there is an edge from
        that node to itself."""
        result = []
        for k in self.keys():
            if k in self.graph[k]:
                result.append(k)
                pass
            pass
        return result

    def keys(self):
        """Get all of the 'from' names of the graph."""
        return self.graph.keys()

    def get(self, f, t):
        """Get the value on a specific edge in the graph, or 0 if the
        edge is not in the graph."""
        if f not in self.graph: return 0
        g = self.graph[f]
        if t not in g: return 0
        return g[t]

    def edges(self, f):
        """Get all of the 'to' nodes in the graph for a given 'from' node."""
        if f not in self.graph: return []
        return self.graph[f].keys()

    def is_singleton(self, f):
        """Determine whether a 'from' node has exactly one 'to' node for it."""
        if f not in self.graph: return False
        return len(self.graph[f].keys()) == 1
    
    def singleton(self, f):
        """If self.is_singleton(f), get the name of the single 'to' node."""
        return self.graph[f].keys()[0]

    def reverse(self):
        """Return a graph with the same values as this, but with the
        'from' and 'to' edges swapped."""
        g = Graph()
        for f in self.graph.keys():
            for t in self.graph[f].keys():
                g.add(t, f, self.graph[f][t])
                pass
            pass
        return g

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
    def add_row(row):
        contributors.add(row[0], row[1], float(row[2]))
        pass
    q._execute("SELECT contributor_name, recipient_name, amount " +
               "FROM " + q.table + " " +
               "WHERE contributor_type='C'",
               (), add_row)
    # Find organizations that give to themselves.  Remove those self
    # loops, but also print out the names of organizations that
    # we're removing from the graph this way.
    self_loops = contributors.self_loops()
    self_loops.sort()
    print "Organizations that only give to themselves:"
    for c in self_loops:
        if contributors.is_singleton(c):
            print "  {0}".format(c)
            pass
        contributors.remove(c, c)
        pass

    recipients = contributors.reverse()

    contributor_names = contributors.keys()
    contributor_names.sort()

    print
    print "Contributors with only one recipient and who aren't recipients themselves:"
    for c in contributor_names:
        if c not in recipients.keys() and contributors.is_singleton(c):
            print "  {0}: {1}".format(c, contributors.singleton(c))
            pass
        pass

    print
    print "Contributors who are recipients with only one downstream recipient:"
    for c in contributor_names:
        if c in recipients.keys() and contributors.is_singleton(c):
            print ("  {0}: {1} ({2} contributors)"
                   .format(c, contributors.singleton(c),
                           len(recipients.edges(c))))
            pass
        pass

    print
    print "Contributors with multiple recipients:"
    for c in contributor_names:
        if not contributors.is_singleton(c):
          print ("  {0} ({1} contributors, {2} recipients)"
                 .format(c, len(recipients.edges(c)),
                         len(contributors.edges(c))))
          pass
        pass
    pass

if __name__ == '__main__':
    main()
    pass
