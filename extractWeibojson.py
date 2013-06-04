#! /usr/bin/python

#print sina weibo api fields
import re,sys,json,argparse
count = 0

parser = argparse.ArgumentParser(description=r"extract files in sina weibo json string")
parser.add_argument("-f","--field_name", help=r'extract particular field data, else print all')
parser.add_argument("input", help=r"input file name")
args = parser.parse_args()

with open (args.input, 'r') as f:
  for line in f:
    jdata = json.loads(line)
    items = jdata['statuses']
    if not args.field_name:
      for i in items:
        count+=1
        for k,v in i.iteritems():
          print k ,"=", v , "|",
        print
    else:
      for i in items:
        count+=1
        print i[args.field_name].encode('utf-8')
