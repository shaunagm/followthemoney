import os, sys
import cPickle as pickle

from codeToIndustry import *

codeHash = {}

codeFile = open('catcodes.csv', 'rb')

for i in codeFile:
    list = i.split('","')
    #list = map(lambda x: x[1:-1], list)
    print list
    di = decodeIndustry()
    di.code = list[1]
    di.name = list[2]
    di.industry = list[3]
    codeHash[di.code] = di


pickle.dump(codeHash, open('industry.p', 'wb'))
