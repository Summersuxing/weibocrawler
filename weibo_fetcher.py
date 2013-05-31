#! /usr/bin/python
# -*- coding: utf8 -*-
from weibo import APIClient
import re, urllib,httplib
import webbrowser
import json
import time,argparse

APP_KEY = "527876810"
APP_SECRET = 'bab48b7876ee6a0aa6393eaf995228cd'      # app secret
CALLBACK_URL = 'http://swiftkey.net/weibotest'  # callback url
LOGIN_NAME = 'Weibo account'
PASSWORD = 'password'
WAIT_SEC = 24 #waiting period (seconds)
expires_in = time.time()
last_login = time.time()

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

print "waiting period = ", WAIT_SEC
print "api_name:",args.api_name

#everyone likes infinite loop!
while True:
  try:
    ts = time.time()
    print "current time=", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
    outf = open(args.outFile, 'a')
    #renew token if expired, not sure about the different limits on different accounts
    #so also force relogin every 23.5 hours
    if ts >= expires_in or (ts - last_login > 84600) : 
      print "(re)getting access token"
      client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
      url = client.get_authorize_url()    # redirect the user to `url'
      access_code = get_code()
      r = client.request_access_token(access_code)
      access_token = r.access_token  # access token. e.g. abc123xyz456
      expires_in = r.expires_in      # token expires in
      last_login = ts                # login in time
      print "access_token=" ,access_token ,
      print "expires_in=" , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_in)) ,
      print "current_time=", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))
      client.set_access_token(access_token, expires_in)
   
    api_parts = re.split(r"/",args.api_name)
    if len(api_parts) == 1:
      api_1 = api_parts[0]
      api_2 = ""
    else:
      api_1 = api_parts[0]
      api_2 = api_parts[1]
 
    print "api call=", api_1 + "/"+ api_2
    ret = client.__getattr__(api_1).__getattr__(api_2).get()
    #ret = client.trends.hourly.get()
    result = json.dumps(ret,ensure_ascii=False)
    #print result
    outf.write( result.encode('utf-8') )
    outf.write("\n")
    outf.close()
    time.sleep(WAIT_SEC)

  except UnicodeError,urllib2.HTTPError:
    print "some exception, will retry"
    time.sleep(1)
    continue
