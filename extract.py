#!/usr/bin/python
import re,sys

f = open (sys.argv[1],'r')
for line in f:
    pattern = re.compile(r'"text":\s{0,1}"(.+?)"',re.VERBOSE)
    res = pattern.findall(line)
    for item in res:
      print item

