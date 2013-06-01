This is script that continusously send Sina Weibo API requests and store the return
json string.

To be able to use this script you will need:
1. a Sina weibo account  : http://www.weibo.com
2. access to a Sina Weibo app key
3. access to a Sina Weibo app secret
4. if the app is a "test app", then the weibo account used to login must be added to the test app list.
   login to http://open.weibo.com/apps/<appid>/info/test 
   and check / add
5. in sina app security settings (http://open.weibo.com/apps/<appid>/info/advanced), 
   the "domain binding"(绑定域名)
   must match your callback url domain


You can create a developer app account once you have a Weibo account,
but any app you create would be a "test app", meaning you will have limited
API access (it is sufficient for getting user weibo entries, comments etc)
Also there is a limit for no. of requests limitations:
If you read Chinese, check here: 
http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI#.E6.8E.A5.E5.8F.A3.E8.AE.BF.E9.97.AE.E9.A2.91.E6.AC.A1.E6.9D.83.E9.99.90

per IP limits:
test account: 1,000 requests/hour
normal account: 10,000 requests/hour

per app per user limits:
  test account: 
    TOTAL:   150 / hour
    Tweet:   30 / hour
    Comment: 60 / hour
    ...

execute ./weibo_fetcher.py  to see the needed parameters
you will need to specify at least:

<api_name>:  this can be any valid weibo api names, such as "statuses/public_timeline" and it will parse and run that api request, full list can be found here: http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI

<output file> : output (json string) will be written (append) here 

Alternatively, ask @wei or @leilei for already setup app details.
