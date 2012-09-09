"""Database-access functions.

These are helpers of various sorts to help you get along with the
SQLite database that 'csvsetup.py' will create for you.  Generally
you will need to do something like

from ftmdb import *
import sqlite3
db = sqlite3.connect('contributions.sqlite')
fec = ContributionsFEC(db)

to access specific tables with helpers here."""

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
