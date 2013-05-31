#! /usr/bin/python
# -*- coding: utf8 -*-
from qqweibo import APIClient
import re, urllib,httplib
import webbrowser
import json
import time,argparse

APP_KEY = "801365768"
APP_SECRET = '38da467b6eebcddea6d697e45f759353'      # app secret
CALLBACK_URL = 'http://swiftkey.net/weibotest'  # callback url
LOGIN_NAME = '178800111'
PASSWORD = 'Liu790723'
WAIT_SEC = 24 #waiting period (seconds)
expires_in = time.time()
last_login = time.time()

'''weibo request limits
初级授权：
read: 1000次/小时
'''

#return value:
#access_token=ACCESS_TOKEN&expires_in=60&refresh_token=REFRESH_TOKEN&name=NAME

parser = argparse.ArgumentParser(description="coninuously calling a weibo api and store the json output string to a file")
parser.add_argument("api_name", help=r'weibo api to be called. see , see: http://open.weibo.com/wiki/微博API')
parser.add_argument("outFile", help="output path file")
parser.add_argument("-t", "--interval",  type=int, default=24, help="time interval between each request, default 24 seconds (150 requests/hour)" )

args = parser.parse_args()
WAIT_SEC = args.interval

print "waiting period = ", WAIT_SEC
print "api_name:",args.api_name

#everyone likes infinite loop!
ts = time.time()
print "current time=", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
#renew token if expired, not sure about the different limits on different accounts
# QQ weibo has a 3 month access_token lifespan
client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
url = client.get_authorize_url()    # redirect the user to `url'
print url
access_code = raw_input ("input access_code:")
#open_id = raw_input("input open id:")
open_id ='68A396EA09AF0134FE50D8BED80FE283'

r = client.request_access_token(access_code)
current_access_token = r.access_token  # access token. e.g. abc123xyz456
expires_in = r.expires_in      # token expires in
last_login = ts                # login in time
print "access_token=" ,current_access_token ,
print "expires_in=" , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_in)) ,
print "current_time=", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
client.set_access_token(current_access_token, open_id, expires_in)

while True:
  try:
    #renew token if expired, not sure about the different limits on different accounts
    # QQ weibo has a 3 month access_token lifespan
    if client.is_expires() : 
      r = client.refresh_token(current_access_token)
      current_access_token = r.access_token
   
    api_parts = re.split(r"/",args.api_name)
    if len(api_parts) == 1:
      api_1 = api_parts[0]
      api_2 = ""
    else:
      api_1 = api_parts[0]
      api_2 = api_parts[1]
 
    print "api call=", api_1 + "/"+ api_2
    ret = client.__getattr__(api_1).__getattr__(api_2).get(format="json", pos=0, reqnum=100)
    #ret = client.post.t__add_pic_url(content="test", clientip="real ip", pic_url="pic url")
    result = json.dumps(ret,ensure_ascii=False)
    print result
    #outf.write( result.encode('utf-8') )
    #outf.write("\n")
    #outf.close()
    time.sleep(WAIT_SEC)

  except UnicodeError,urllib2.HTTPError:
    print "some exception, will retry"
    time.sleep(1)
    continue
