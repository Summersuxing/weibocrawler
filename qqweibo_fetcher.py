#! /usr/bin/python
# -*- coding: utf8 -*-
from qqweibo import APIClient
import re, urllib,httplib
import webbrowser
import json
import sys,math,time,argparse,ConfigParser

'''qq weibo request limits
初级授权：
read: 1000次/小时
'''

class QQWeiboFetcher():
  '''init'''
  def __init__(self, app_key, app_secret, callback_url, open_id=None):
        self.app_key = str(app_key)
        self.app_secret = str(app_secret)
        self.open_id = open_id
        #self.qq_login = str(qq_login)
        #self.qq_password = str(qq_password)
        self.callback_url = str(callback_url)
        self.api_reset_time = 0
        self.remaining_api_hits = 0

  def authorize(self):
    #self.open_id = open_id
    self.client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
    url = self.client.get_authorize_url()
    print "authorize url=%s", url
    access_code = raw_input("paste access code:")
    if not self.open_id:
      self.open_id = raw_input("paste open id:")
    #open_key = raw_input("paste open key:")

    r = self.client.request_access_token(access_code)
    access_token = r.access_token  # access token. e.g. abc123xyz456
    expires_in = r.expires_in      # token expires in
    self.client.set_access_token(r.access_token, self.open_id, r.expires_in)
    print "expires_in=" , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_in)) ,
    print "current_time=", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime( time.time() ))

  def run(self, api_name, params_dict) :
    #parse parameter string into dictionary obj.
    ret = self.client.__getattr__(api_name)(**params_dict)
    return json.dumps(ret,ensure_ascii=False)

if __name__=='__main__':
  #populate config settings
  config = ConfigParser.ConfigParser()
  config.read('config.cfg')
  APP_KEY = config.get('qqweibo', 'qq_weibo_app_id')
  APP_SECRET = config.get('qqweibo', 'qq_weibo_app_secret')      # app secret
  CALLBACK_URL = config.get('qqweibo', 'qq_weibo_callback_url')  # callback url
  OPEN_ID = config.get('qqweibo','qq_open_id')
  #LOGIN_NAME = config.get('qqweibo', 'qq_weibo_login')  # NOT USED YET
  #PASSWORD = config.get('qqweibo', 'qq_weibo_password') # NOT USED YET
  count = 0
  retry_interval = 5

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
  fetcher = QQWeiboFetcher(app_key=APP_KEY, app_secret=APP_SECRET, callback_url=CALLBACK_URL, open_id=OPEN_ID)  
  fetcher.authorize()

  if args.interval and args.interval > 0:
    print "manual interval"
    WAIT_SEC = args.interval
  else: #set wait interval dynamically
    ## check how many api calls are available
    noCalls = 1000
    WAIT_SEC = math.ceil(3600.0 / noCalls)

  print "\nwaiting period = ", WAIT_SEC
  print "api_name:",args.api_name
  print "params:", params_dict

  with (open(args.output, 'a') if args.output else sys.stdout) as outf:
    #everyone loves infinite loop!
    while True:
      count +=1
      try:
        if fetcher.client.is_expires() :
          r = fetcher.client.refresh_token(fetcher.client.access_token)
          fetcher.client.set_access_token(r.access_token, r.expires_in)
          print "expires_in=" , time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_in)) ,
          print "current_time=", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime( time.time() ))


        result = fetcher.run(args.api_name, params_dict)
        print "localtime=[%s], running api '%s' , loop=%s" % (time.strftime('%Y-%m-%d %H:%M:%S'),args.api_name,count)

        outf.write( result.encode('utf-8') )
        outf.write("\n")
        #take a break, have a kit-kat
        time.sleep(WAIT_SEC)
      
      except KeyboardInterrupt:
        outf.flush()
        outf.close()
      except ( httplib.BadStatusLine) as e:
        print "Connection error: %s, retry in %s seconds" % e.errstr , retry_interval
        time.sleep(retry_interval)
        continue
      #except:
      #  print "unknown error: %s, retry in %s seconds" % sys.exc_info(), retry_interval
      #  time.sleep(retry_interval)

