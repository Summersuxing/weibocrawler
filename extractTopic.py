#! /usr/bin/python
#coding=utf8

import sys,re,json

with open (sys.argv[1], 'r') as f:
  for line in f:
    jdata = json.loads(line)
    items = jdata['trends']
    l = items.values()[0]
    for it in l:
      print it['query'].encode('utf8')
    



