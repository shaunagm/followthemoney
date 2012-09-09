#!/usr/bin/python
"""Set up SQLite databases from CSV files."""

import csv2sqlite
import optparse
import os
import sqlite3
import zipfile

csvs = [ { 'csv': 'contributions.fec.2012.csv',
           'zip': 'contributions.fec.2012.csv.zip',
           'url': 'http://datacommons.s3.amazonaws.com/subsets/td-20120907/contributions.fec.2012.csv.zip',
           'table': 'fec',
           'index': ['recipient_name'] } ]

def main():
    parser = optparse.OptionParser(usage='%prog [options]')
    parser.add_option("-p", "--path", default='data',
                      help="Find CSV files in PATH [./data]")
    parser.add_option("-f", "--file", default='contributions.sqlite',
                      help="Use SQLite database in FILE [contributions.sqlite]")
    (options,args) = parser.parse_args()
    def fn(f): return os.path.join(options.path, f)
    db = sqlite3.connect(options.file)
    cursor = db.cursor()
    # PRECHECK: Every file must exist.
    good = True
    for record in csvs:
        if os.path.exists(fn(record['csv'])): continue
        if os.path.exists(fn(record['zip'])): continue
        good = False
        print "Missing CSV file {0}; download from".format(fn(record['csv']))
        print record['url']
        pass
    if not good: return
    def progress(n): print "...{0}".format(n)
    for record in csvs:
        if os.path.exists(fn(record['csv'])):
            f = open(fn(record['csv']), 'r')
        else: # by assertion the zip file exists
            z = zipfile.ZipFile(fn(record['zip']), 'r')
            f = z.open(record['csv'], 'r')
            pass
        print "Importing table {0} from file {1}".format(record['table'],
                                                         record['csv'])
        csv2sqlite.do_import(f, db, record['table'], drop=True,
                             progress = progress)
        # Create any indexes required
        if 'index' in record:
            for column in record['index']:
                print "...index {0}".format(column)
                cursor.execute("CREATE INDEX {0}_{1} ON {0} ({1})"
                               .format(record['table'], column))
                pass
            db.commit()
            pass
        pass
    pass

if __name__ == '__main__':
    main()
    pass
