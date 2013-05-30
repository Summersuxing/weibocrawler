#! /usr/bin/python
# -*- coding: utf8 -*-
from weibo import APIClient
import re, urllib,httplib
import webbrowser
import json
import time,argparse

APP_KEY = "weibo app key"
APP_SECRET = 'weibo app secret'      # app secret
CALLBACK_URL = 'http://swiftkey.net/weibotest'  # callback url
LOGIN_NAME = 'Your weibo login account'
PASSWORD = 'your weibo login password'
WAIT_SEC = 10 #waiting period (seconds)
expires_in = 0

'''weibo request limits
一、针对一个服务器IP的请求次数限制
测试授权：
1000次/小时
普通授权：
10000次/小时

二、针对一个用户在使用一个应用的请求次数限制
测试授权：
总限制：单用户每应用 150次/小时
发微博：单用户每应用 30次/小时
发评论：单用户每应用 60次/小时
加关注：单用户每应用 60次/小时 100次/天
普通授权：
总限制：单用户每应用 1000次/小时
发微博：单用户每应用 30次/小时
发评论：单用户每应用 60次/小时
加关注：单用户每应用 60次/小时 200次/天
'''
def get_code():
    conn = httplib.HTTPSConnection('api.weibo.com')
    postdata = urllib.urlencode     ({'client_id':APP_KEY,'response_type':'code','redirect_uri':CALLBACK_URL,'action':'submit','userId':LOGIN_NAME,'passwd':PASSWORD,'isLoginSina':0,'from':'','regCallback':'','state':'','ticket':'','withOfficalFlag':0})
    conn.request('POST','/oauth2/authorize',postdata,{'Referer':url,'Content-Type': 'application/x-www-form-urlencoded'})
    res = conn.getresponse()
    #print 'headers===========',res.getheaders()
    print 'msg===========',res.msg
    print 'status===========',res.status
    print 'reason===========',res.reason
    print 'version===========',res.version
    location = res.getheader('location')
    #print location
    code = location.split('=')[1]
    conn.close()
    #print code
    return code


parser = argparse.ArgumentParser(description="coninuously calling a weibo api and store the json output string to a file")
parser.add_argument("api_name", help=r'weibo api to be called. see , see: http://open.weibo.com/wiki/微博API')
parser.add_argument("outFile", help="output path file")
parser.add_argument("-t", "--interval",  type=int, default=24, help="time interval between each request, default 24 seconds (150 requests/hour)" )

args = parser.parse_args()

WAIT_SEC = args.interval

outf = open(args.outFile, 'a')

print "waiting period = ", WAIT_SEC
print "api_name:",args.api_name
while True:
  try:
    ts = time.time()
    print "current timestamp=", ts
    #renew token if expired
    if ts >= expires_in: 
      print "(re)getting access token"
      client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
      url = client.get_authorize_url()    # redirect the user to `url'
      access_code = get_code()
      r = client.request_access_token(access_code)
      access_token = r.access_token  # access token. e.g. abc123xyz456
      expires_in = r.expires_in      # token expires in

      print "access_token=" ,access_token, "expires_in=" ,expires_in, "current_time=",ts
      client.set_access_token(access_token, expires_in)
    
    (api_1, api_2) = re.split(r"/",args.api_name)
    print "api_1=",api_1, "api_2=", api_2
    ret = client.__getattr__(api_1).__getattr__(api_2).get()
    #ret = client.trends.hourly.get()
    result = json.dumps(ret,ensure_ascii=False)
    print result
    outf.write( result.encode('utf-8') )
    outf.write("\n")
#     ret = client.trend.hourly.get(0
    time.sleep(WAIT_SEC)

  except UnicodeError:
    print "some exception, will retry"
    time.sleep(1)
    continue

f.close()   
