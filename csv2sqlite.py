#!/usr/bin/python
"""Import a CSV file into a (SQLite) database.

This can be run as a command-line tool; give on the command line the name
of the CSV file, the name of the SQLite database file, and the name of
the SQLite database table.

This can also be invoked programmatically.  Call csv2sqlite.do_import()
with the file-like object for the input file, the database connection
object, and the name of the database table.  This should work for any
database sufficiently similar to SQLite for the Python database API to
work."""

import csv
import optparse
import sqlite3
import sys

def do_import(f, db, table, drop=False, create=True, progress=None):
    """Import content from CSV file-like object 'f' into database 'db'
    using table name 'table'.  By default the table will be CREATE TABLE'd,
    but if the optional 'create' parameter is set to False it will not be
    and data will only be added to an existing table.  If the 'drop'
    parameter is set to true then the table will be dropped before
    recreating it.  If 'progress' is given, it is a function called with
    the total number of processed rows, every 10,000 rows."""
    cur = db.cursor()

    if drop:
        create = True # this makes no sense otherwise
        try:
            cur.execute("DROP TABLE {0}".format(table))
        except sqlite3.OperationalError, e:
            pass # no such table, ignore
        pass

    csvr = csv.DictReader(f)
    # DictReader will read the list of field names from the first line
    columns = [ "{0} VARCHAR(1024)".format(c) for c in csvr.fieldnames ]
    # TODO: Different database drivers use different syntax
    qmarks = [ "?" for c in csvr.fieldnames ]
    insert = "INSERT INTO {0} VALUES ({1})".format(table, ', '.join(qmarks))

    if create:
        query = "CREATE TABLE {0} ({1})".format(table, ', '.join(columns))
        cur.execute(query)
        pass

    count = 0
    for row in csvr:
        count += 1
        if progress is not None and (count % 10000) == 0:
            progress(count)
            pass
        values = []
        for f in csvr.fieldnames:
            values.append(row[f])
            pass
        cur.execute(insert, values)
        pass
    db.commit()
    if progress is not None:
        progress(count)
    pass
    
if __name__ == '__main__':
    parser = optparse.OptionParser(usage='%prog file.csv file.sqlite table')
    parser.add_option("-d", "--drop", action="store_true",
                      help="Drop the table before recreating it")
    (options,args) = parser.parse_args()
    if len(args) < 3:
        parser.error("must provide CSV, database file, and table names")
        pass
    f = open(args[0], 'r')
    db = sqlite3.connect(args[1])
    table = args[2]
    def progress(n): print "...{0}".format(n)

    do_import(f, db, table, drop=options.drop, progress=progress)

    f.close()
    pass
