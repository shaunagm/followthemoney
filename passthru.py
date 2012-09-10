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
    parser.add_option("-i", "--individuals", action="store_true",
                      help='Include contributions from individuals')
    parser.add_option("--print-self", action="store_true",
                      help='Print donors that only give to themselves')
    (options,args) = parser.parse_args()
    if len(args) != 0:
        parser.error("No command-line arguments accepted")
        pass
    db = sqlite3.connect(options.file)
    q = ContributionsFEC(db)

    # Build a graph of contributors to recipients.
    # Edge values are dollar amounts.
    contributors = Graph()
    # Do some pre-processing on transaction types:
    # http://influenceexplorer.com/about/methodology/campaign_finance
    # suggests only including specific types.
    valid_types = [ '10', '11', '15', '15e', '15j', '22y',
                    '24k', '24r', '24z',
                    'Z90' ]
    def add_row(row):
        if row[3] in valid_types:
            contributors.add(row[0], row[1], float(row[2]))
            pass
        pass
    query = ("SELECT contributor_name, recipient_name, amount, " +
             "transaction_type " + "FROM " + q.table)
    if not options.individuals:
        query += " WHERE contributor_type='C'"
        pass
    q._execute(query, (), add_row)
    # Find organizations that give to themselves.  Remove those self
    # loops, but also print out the names of organizations that
    # we're removing from the graph this way.
    self_loops = contributors.self_loops()
    self_loops.sort()
    if options.print_self:
        print "Organizations that only give to themselves:"
        pass
    for c in self_loops:
        if options.print_self and contributors.is_singleton(c):
            print "  {0}".format(c)
            pass
        contributors.remove(c, c)
        pass
    if options.print_self:
        print
        pass

    # Now:
    # contributors is a graph from givers to receivers
    # recipients is a graph from receivers to givers
    # len(contributors.edges(me)) is the number of people me gives to
    # contributors.singleton(me) is the person I give to (if only one)
    recipients = contributors.reverse()

    contributor_names = contributors.keys()
    contributor_names.sort()

    # At this point, we can look at:
    # * No contributors (individual)
    # * No recipients (candidate)
    # * One contributor (shell)
    # * One recipient (committee)
    # * Many contributors
    # * Many recipients
    # So let's split both graphs into lists of (zero, one, many):
    def split_graph(g):
        zero = []
        one = []
        many = []
        for n in g.keys():
            l = len(g.edges(n))
            if l == 0: zero.append(n)
            elif l == 1: one.append(n)
            else: many.append(n)
            pass
        return (set(zero), set(one), set(many))
    (candidates, committees, givers) = split_graph(contributors)
    (individuals, shells, receivers) = split_graph(recipients)

    # The single thing we're most interested in is things with only
    # one recipient.
    l = list(committees)
    l.sort()
    # "Pass-thru" entities with only one giver
    print "Pass-thru entities:"
    for r in l:
        if r in shells:
            print ("  {0} (from {1} to {2})"
                   .format(r, recipients.singleton(r),
                           contributors.singleton(r)))
            pass
        pass
    print

    print "Committees for a single receiver:"
    for r in l:
        if r in receivers:
            print ("  {0} ({1} contributors, to {2})"
                   .format(r, len(recipients.edges(r)),
                           contributors.singleton(r)))
            pass
        pass
    print

    l = list(shells)
    l.sort()
    print "Other shells:"
    for c in l:
        if c not in committees:
            print ("  {0} (for {1}, {2} recipients)"
                   .format(c, recipients.singleton(c),
                           len(contributors.edges(c))))
            pass
        pass
    print

    pass

if __name__ == '__main__':
    main()
    pass
