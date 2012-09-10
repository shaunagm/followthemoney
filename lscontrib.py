#!/usr/bin/python

from ftmdb import *
import optparse
import sqlite3

def main():
    parser = optparse.OptionParser(usage='%prog [options] "name"')
    parser.add_option("-f", "--file", default='contributions.sqlite',
                      help='Read database file FILE')
    parser.add_option("--from", action='store_true', dest='fr',
                      help='Show contributions from given name')
    parser.add_option("--to", action='store_false', dest='fr',
                      help='Show contributions to given name')
    (options,args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Give one contributor or recipient name")
        pass
    db = sqlite3.connect(options.file)
    q = ContributionsFEC(db)

    query = "SELECT "
    if options.fr:
        query += "recipient_name"
    else:
        query += "contributor_name"
        pass
    query += ", transaction_type, date, amount FROM fec WHERE "
    if options.fr:
        query += "contributor_name"
    else:
        query += "recipient_name"
        pass
    query += "=? ORDER BY date"
    def f(row):
        print "{0} {1} {2} {3}".format(row[2], row[1], row[0], row[3])
        pass
    print query
    q._execute(query, (args[0],), f)
    pass

if __name__ == '__main__':
    main()
    pass
