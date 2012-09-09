#!/usr/bin/python

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

class DatabaseQueries(object):
    """Base class to do queries on databases."""
    def __init__(self, db, table):
        self.db = db
        self.cursor = db.cursor()
        self.table = table
        pass

    @staticmethod
    def _results(result, f):
        """Go through the results of a database execute() function and
        call 'f' on each row."""
        while True:
            row = result.fetchone()
            if row is None: break
            f(row)
            pass
        return

    def _execute(self, query, values, f):
        """Run a single SQL query, with provided query parameters,
        and run the function 'f' on each result row."""
        results = self.cursor.execute(query, values)
        self._results(results, f)
        pass

    def select_from(self, column):
        """Select a single column's value from the current table.
        Get the distinct values from that column as a list."""
        results = []
        def f(row): results.append(row[0])
        self._execute("SELECT DISTINCT {0} FROM {1}".format(column, self.table),
                      (), f)
        return results

    pass

class ContributionsFEC(DatabaseQueries):
    def __init__(self, db, table='fec'):
        super(ContributionsFEC, self).__init__(db, table)
        pass

    def contributors(self):
        """Get a list of all contributors."""
        return self.select_from('contributor_name')

    def recipients(self):
        """Get a list of all contribution recipients."""
        return self.select_from('recipient_name')

    def contributions_for_recipient(self, name):
        """Get a dictionary with contributor key and dollar amount value
        of all contributions to a named recipient."""
        query = ("SELECT contributor_name, sum(amount) " +
                 "FROM {0} WHERE recipient_name=? GROUP BY contributor_name"
                 ).format(self.table)
        result = self.cursor.execute(query, [name])
        results = {}
        def f(row): results[row[0]] = row[1]
        self._results(result, f)
        for k in results.keys():
            results[k] = float(results[k])
            pass
        return results

    @staticmethod
    def contributions_by_percent(table):
        """Given a table of contributions by dollar amount, return an
        equivalent table of contributions by percentage of the total."""
        # NB: right now we have only TEXT data
        total = 0.0
        for k in table.keys():
            total += table[k]
            pass
        result = {}
        for k in table.keys():
            result[k] = table[k] / total
            pass
        return result


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
