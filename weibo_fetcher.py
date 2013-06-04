#! /usr/bin/python
# -*- coding: utf8 -*-
from weibo import APIClient
import sys,re,urllib,httplib
import webbrowser
import json
import math,time,argparse,ConfigParser

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
        self.api_reset_time = 0
        self.remaining_api_hits = 0
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
    if not location:
      print "incorrect server response, check app/login details?"
      exit(-1)
    #print location
    code = location.split('=')[1]
    conn.close()
    #print code
    return code

  #return the remaining API calls
  def getHourlyAPICallLimit(self):
    callDict = self.client.account.rate_limit_status.get() 
    self.api_reset_time = float( callDict['reset_time_in_seconds'] )
    self.remaining_api_hits = min(int(callDict['remaining_ip_hits']), int(callDict['remaining_user_hits']))
    #this is the number of available api calls per hour, reset every whole hour 
    return callDict['user_limit']

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
  #populate config settings
  config = ConfigParser.ConfigParser()
  config.read('config.cfg')
  APP_KEY = config.get('sinaweibo', 'sina_weibo_app_id')
  APP_SECRET = config.get('sinaweibo', 'sina_weibo_app_secret')      # app secret
  CALLBACK_URL = config.get('sinaweibo', 'sina_weibo_callback_url')  # callback url
  LOGIN_NAME = config.get('sinaweibo', 'sina_weibo_login')
  PASSWORD = config.get('sinaweibo', 'sina_weibo_password')
  count = 0

  parser = argparse.ArgumentParser(description="coninuously calling a given Sina weibo api and store the json output string to a file")
  parser.add_argument("api_name", help=r'weibo api to be called. such as "statuses/pubilc_timeline", see: http://open.weibo.com/wiki/微博API')
  parser.add_argument("-o","--output", help="output path file (append if exists)")
  parser.add_argument("-t", "--interval",  type=int, help="set manual time interval between each request in seconds" )
  parser.add_argument("-p", "--parameters", help='extra api parameters, e.g. "p1=v1,p2=v2,etc..." ')

  args = parser.parse_args()
  #parse parameters
  params_dict = {}

  if args.parameters:
    p = re.split(',',args.parameters)
    for item in p:
      (k,v) = re.split('=', item)
      params_dict[k] = v

  #initialize, will call authorize() first time here
  fetcher = SinaWeiboFetcher(app_key=APP_KEY, app_secret=APP_SECRET, weibo_login=LOGIN_NAME, weibo_password=PASSWORD, callback_url=CALLBACK_URL)  
  
  if args.interval and args.interval > 0:
    print "manual interval"
    WAIT_SEC = args.interval
  else: #set wait interval dynamically
    ## check how many api calls are available
    noCalls = fetcher.getHourlyAPICallLimit()
    WAIT_SEC = math.ceil(3600.0 / noCalls)

  print "\nwaiting period = ", WAIT_SEC
  print "api_name:",args.api_name
  print "params:", params_dict

  if args.output:
    outf = open(args.output, 'a')
  else:
    outf = sys.stdout

  #everyone loves infinite loop!
  while True:
    try:
      count+=1
      if fetcher.isTokenExpired() :
        fetcher.authorize()

      result = fetcher.run(args.api_name, params_dict)
      print "localtime=[", time.strftime('%Y-%m-%d %H:%M:%S'),"], running", '"', args.api_name,'"', count, "times"

      outf.write( result.encode('utf-8') )
      outf.write("\n")
      #outf.flush() 
      #take a break, have a kit-kat
      time.sleep(WAIT_SEC)
    
    except KeyboardInterrupt:
      outf.flush()
      outf.close()
    else:
      #some error, retry
      retry_interval = 5
      print "unknown error, retry in", retry_interval, "seconds"
      time.sleep(retry_interval)
      continue


