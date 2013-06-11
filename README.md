
provide scripts that continusously send Sina/QQ Weibo API requests and store the return
json string.

##                        Sina Weibo Fetcher
###Sina Weibo App setup
To be able to use this script you will need some Sina weibo details:

1. a Sina weibo account  : http://www.weibo.com
2. access to a Sina Weibo app key
3. access to a Sina Weibo app secret
4. if the app is a "test app", then the weibo account used to login must be added to the test app list.
   login to http://open.weibo.com/apps/<appid\>/info/test 
   and check / add
5. in sina app security settings (http://open.weibo.com/apps/<appid\>/info/advanced), 
   the "domain binding"(绑定域名)
   must match your callback url domain

You can create a developer app account once you have a Weibo account,
but any app you create would be a "test app", meaning you will have limited
API access (it is sufficient for getting user weibo entries, comments etc)
Also there is a limit for no. of requests limitations:
If you read Chinese, check here: 
http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI#.E6.8E.A5.E5.8F.A3.E8.AE.BF.E9.97.AE.E9.A2.91.E6.AC.A1.E6.9D.83.E9.99.90

Alternatively, ask wei@swiftkey.net or leilei@swiftkey.net for already setup app details.

###API limits
Per IP limits:

+ test account: 1,000 requests/hour
+ normal account: 10,000 requests/hour

Per app per user limits:
  test account: 

+ TOTAL:   150 / hour
+ Tweet:   30 / hour
+ Comment: 60 / hour

### Running the program

Before running, you should check that all details (app/login) are correctly stored
in the **config.cfg** file, then run *sinaweibo_fetcher.py* 

you will need to specify at least:

[api_name]: this can be any valid weibo APIs, such as "statuses/public_timeline", it will parse and run that API request, full list can be found here:

>http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI

if you do not specify the -t interval, it will work out the number of available api calls per hour from the server then evenly spreads the interval.



##                 QQ Weibo Fetcher

###QQ Weibo setup
Tencent QQ operates a similar Weibo service, you also need a QQ account for Oauth2
and a userable app account. 


### API Limits
read: 1000 / hour

###Authentication
Currently the script cannot authenticate user automatically, mainly due to the additonal QQ login security (when the Oauth page popup sometimes it requires user to enter a captcha)
As a result when you run this script, a redirect url will be displayed and you should paste this to your browser and submit the login detais (and captha). 
Now here is the tricky part: if successful, it will redirect you to your call back
URL, WITH PARAMETERS such as CODE and OPENID attached, for example:

http://swiftkey.net/weibotest?code=XXX&openid=YYYY&openkey=ZZZZZ&state=

we need the *code* to continue. Most browsers have a "developer/debug mode" (if you are using Chrome, press F12) that let you see the parameters. You will have to manually enter the code to the console and continue.
The *code* is valid for 10 mins

*NOTE* that every QQ Weibo API requires (more) compulsory parameters than Sina Weibo, make sure you read the required paramter to pass to the script (using -p) , 
for example, the "statuses/public_timeline" API requires 3 additional parameters, e.g.

> ./qqweibo_fetcher.py "statuses/public_timeline" -p "format=json,pos=0,reqnum=100"


In the config file there is a qq_open_id field, this value is the "openid" value in the URL, this value is associated with
the QQ Login name/number. It is not quite clear what this is for, since give it an arbitary value will work (for the API I used), but advicable to put the correct value so once you have it , put it in the config so you don't need to enter this everytime. 

###Running
you will need to specify at least:

[api_name]: this can be any valid weibo APIs, such as "statuses/public_timeline", it will parse and run that API request, full list can be found here:

>http://wiki.open.t.qq.com/index.php/API%E6%96%87%E6%A1%A3

if you do not specify the -t interval, it will work out the number of available api calls per hour from the server then evenly spreads the interval.
