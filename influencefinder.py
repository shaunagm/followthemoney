# Jessie Lowell - code for "triangle" problem at Follow the Money workshop

#MoC: (Candidate for Sen or House is AC) Z (Party is AB)
#Sector: U
#Corp: O
#Donation $: I

import csv

# Gather the basics

bill = input('Enter a bill number: ')
sector = input('Enter a sector code: ')
y_or_n = input('Do you want to see information for supporters or opponents of the bill? ')

# Open the CSV files and create the lists

f1 = open('contributions.fec.2012.csv', 'rt')
f2 = open('resultsdump.csv', 'wt')

reader_votes = csv.reader(open('something.csv', 'rb'))
# This last line is wrong - need program to get info from Sunlight API
list_moc = [] #list for members of congress who voted the relevant way, we need to fill it

reader_contribs = csv.reader(f1)
list_assoc_moc = [] # members of congress - each name will appear many times in this list since they probably got many contributions
list_party = [] # member's party
list_sector = [] # sector of donation - currently 5-char code, Dexter's script is supposed to fix this
list_corp = [] # corpration of donation
list_amount = [] # amount of donation

for row in reader_contribs: # loops through whole FEC spreadsheet
	for moc in list_moc: # did candidate on this row vote the relevant way?  If yes:
		if row(25) == moc: # then append the relevant data to the previously-initialized lists
			list_assoc_moc.append(row(25))
			list_party.append(row(27))
			list_sector.append(row(20))
			list_corp.append(row(14))
			list_amount.append(row(8))

f1.close() # close that file

# Dump result data

# Each donation record gets its own row
writer = csv.writer(open('resultsdump.csv', 'wb', buffering=0))
for x in range(0,len(list_assoc_moc)):
	writer.writerow((list_assoc_moc(x), list_party(x), list_sector(x), list_corp(x), list_amount(x)))

f2.close(); # close results dump file
