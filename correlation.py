#!/usr/bin/python

from ftmdb import *
import optparse
import sqlite3

def main():
    parser = optparse.OptionParser(usage='%prog [options] "candidate"')
    parser.add_option("-f", "--file", default='contributions.sqlite',
                      help='Read database file FILE')
    (options,args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Give exactly one candidate name")
        pass
    candidate = args[0]
    db = sqlite3.connect(options.file)
    q = ContributionsFEC(db)
    recipients = q.recipients()
    ts = {}
    for r in recipients: ts[r] = q.contributions_for_recipient(r)
    me = ts[candidate]
    similarities = {}
    for r in recipients:
        if r == candidate: continue
        similarities[r] = similarity(me, ts[r])
        pass
    similarities[candidate] = 0.0
    # sort the list of recipients in descending order by similarity score
    recipients.sort(None, lambda k: similarities[k], True)
    #print "Top recipient: {0}".format(recipients[0])
    #for (k, v1, v2) in common_contributors(me, ts[recipients[0]]):
    #    print "  {0}: {1} to me, {2} to them".format(k, v1, v2)
    #    pass
    print "Top ten:"
    for r in recipients[:10]:
        print "  {0}: {1}".format(r, similarities[r])
        pass
    pass



def similarity(t1, t2):
    """Return some sort of numeric index of how similar two tables, keyed
    by contributor name, are."""
    # First pass: just count number of keys in common
    return len(common_contributors(t1, t2))

def common_contributors(t1, t2):
    """Go through two tables of contributor amounts.  Return tuples of
    (name, amount1, amount2) for all common contributors."""
    result = []
    for k in t1.keys():
        if k in t2:
            t = (k, t1[k], t2[k])
            result.append(t)
            pass
        pass
    return result

if __name__ == '__main__':
    main()
    pass
