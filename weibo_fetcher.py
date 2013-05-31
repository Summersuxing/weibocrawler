#! /usr/bin/python
# -*- coding: utf8 -*-
from weibo import APIClient
import re, urllib,httplib
import webbrowser
import json
import time,argparse

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

class SinaWeiboFetcher():
  '''init'''
  def __init__(self, app_key, app_secret, weibo_login, weibo_password, callback_url):
        self.app_key = str(app_key)
        self.app_secret = str(app_secret)
        self.weibo_login = str(weibo_login)
        self.weibo_password = str(weibo_password)
        self.callback_url = str(callback_url)
        #weibo login / get token
        self.authorize()


#get auth code automatically
  def get_code(self, url):
    conn = httplib.HTTPSConnection('api.weibo.com')
    postdata = urllib.urlencode({'client_id':self.app_key,'response_type':'code','redirect_uri':self.callback_url,'action':'submit','userId':self.weibo_login,'passwd':self.weibo_password,'isLoginSina':0,'from':'','regCallback':'','state':'','ticket':'','withOfficalFlag':0})
    conn.request('POST','/oauth2/authorize',postdata,{'Referer':url,'Content-Type': 'application/x-www-form-urlencoded'})
    res = conn.getresponse()
    #print 'headers===========',res.getheaders()
    print res.msg
    print 'status:',res.status
    print 'reason:',res.reason
    #print 'version===========',res.version
    location = res.getheader('location')
    #print location
    code = location.split('=')[1]
    conn.close()
    #print code
    return code


  def authorize(self):
    self.client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    url = self.client.get_authorize_url()    # redirect the user to `url'
    access_code = self.get_code(url)
    r = self.client.request_access_token(access_code)
    access_token = r.access_token  # access token. e.g. abc123xyz456
    self.last_login = time.time()
    self.client.set_access_token(r.access_token,r.expires_in)
    #print "access_token=" ,r.access_token ,
    print "expires_in=" , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r.expires_in)) ,
    print "login_time=", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.last_login))


  #check if the access_token is expired now
  def isTokenExpired(self):
    return not self.client.access_token or time.time() >= self.client.expires 

  #run a weibo api call, use this function after authorize() (e.g. must have a valid access_token)
  def run(self, api_name, params_dict) :
    #parse parameter string into dictionary obj.
    api_parts = re.split(r"/",api_name)
    if len(api_parts) == 1:
      api_1 = api_parts[0]
      api_2 = ""
    else:
      api_1 = api_parts[0]
      api_2 = api_parts[1]
    
    #some python "%$"$£$!"£" to use method names "dynamically"
    ret = self.client.__getattr__(api_1).__getattr__(api_2).get(**params_dict)
    return json.dumps(ret,ensure_ascii=False)

if __name__=='__main__':
  APP_KEY = "527876810"
  APP_SECRET = 'bab48b7876ee6a0aa6393eaf995228cd'      # app secret
  CALLBACK_URL = 'http://swiftkey.net/weibotest'  # callback url
  LOGIN_NAME = 'ld312@sina.cn'
  PASSWORD = '820110'
  WAIT_SEC = 24 #waiting period (seconds)
  count = 0

  parser = argparse.ArgumentParser(description="coninuously calling a weibo api and store the json output string to a file")
  parser.add_argument("api_name", help=r'weibo api to be called. see , see: http://open.weibo.com/wiki/微博API')
  parser.add_argument("outFile", help="output path file (will append if exists)")
  parser.add_argument("-t", "--interval",  type=int, default=24, help="time interval between each request, default 24 seconds (150 requests/hour)" )
  parser.add_argument("-p", "--parameters", help='extra api parameters, e.g. "p1=v1,p2=v2,etc..." ')

  args = parser.parse_args()
  WAIT_SEC = args.interval
  #parse parameters
  params_dict = {}

  if args.parameters:
    p = re.split(',',args.parameters)
    for item in p:
      (k,v) = re.split('=', item)
      params_dict[k] = v

  
  print "waiting period = ", WAIT_SEC
  print "api_name:",args.api_name
  print "params:", params_dict

  #initialize, will call authorize() first time here
  fetcher = SinaWeiboFetcher(app_key=APP_KEY, app_secret=APP_SECRET, weibo_login=LOGIN_NAME, weibo_password=PASSWORD, callback_url=CALLBACK_URL)  

  #everyone loves infinite loop!
  while True:
    try:
      count+=1
      if fetcher.isTokenExpired() :
        fetcher.authorize()
      
      result = fetcher.run(args.api_name, params_dict)
      print "localtime=[", time.strftime('%Y-%m-%d %H:%M:%S'),"], running", count, "times"
      

      #write to a file in append mode
      #this is inside an infinite loop so assume there are plently of
      #time between each loop!!!
      outf = open(args.outFile, 'a')
      outf.write( result.encode('utf-8') )
      outf.write("\n")
      outf.close()

      time.sleep(WAIT_SEC)

    except UnicodeError,urllib2.HTTPError:
      print "some exception, will retry"
      time.sleep(1)
      continue

