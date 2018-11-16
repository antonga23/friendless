# _Friendless_, a Post-CA Facebook Scraper [2018 Edition]
### Introduction
Does the bulky Facebook API access got you ticked? Want to
 just download a script and instantly scrape entire pages?
 Look no further! I am proud to present to you a page scraper
 that laughs in the face of API access!
 
This is a post-Cambridge Analytica, post-GDPR and GDPR-compliant
 scraper with built in PII-hashing so that it may
 be used in something like social network analysis, whilst maintaining
 anonymity of users.
 
 ### Getting Started
1. Place the Facebook.py script into your working directory.
1. Check that the location of your geckodriver is in `/usr/local/bin/geckodriver` on
Mac, or wherever your PATH is set to on Windows 
(see [this guide](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
 to locate PATH on a Windows machine).
For a guide to downloading geckodriver for Firefox, click 
[here](http://lmgtfy.com/?q=geckodriver+download+for+firefox).
1. Follow the code example below:
```python
from Facebook import *
import unicodecsv as csv

# Enter login info of an account.
email = "phonyemail@aol.net"  
password = "P@$$W0RD" 
# At 5 events per page, the parameter 1 will return 5 events.
number_of_pages = 1       

# Create a Facebook object with your credentials, and a maximum wait time in seconds for each operation.
fb = Facebook(email, password, max_wait=10, geckopath='/usr/local/bin/geckodriver')

# Navigate to the mobile version of the site. Navigate with www.mobile.facebook.com on Firefox.
fb.goto_page("https://mobile.facebook.com/SOME_PAGE/super_long_link...")

df = fb.scrape_mobile(number_of_pages, scrape_who_reacted=True, hush_params=["21:30", "07:30", 30, 30])
# hush_params puts the bot to sleep for about 8 hours a night to prevent looking sketchy..
# [time to sleep, time to wake,
# Returns a nested list (ready to be iterated through and written to csv) of the format:
# [text, num_likes, num_loves, num_hahas, num_wows, num_sads, num_angrys, num_reacts, event_link, hashtags_used(list), reacted(hashed list)]
```
### Additional Features
`parse_log(read_loc, write_loc)` - call from main to parse a log file. This is useful in case
the csv was corrupted or came across an odd character during the scraping process.


### Disclaimer

**I take it as a personal challenge to try to find loopholes in privacy and API's so that companies
(_\*cough\* Facebook \*cough\*_) might learn to be a little more responsible with their data practices.**

I am not responsible for any trouble you get yourself into because of this script. This is purely to
educate the community about ways of getting around sticky API access to scrape data, and to demonstrate
the power of Python! To learn more about the GDRP regulations, click
[here](https://gdpr-info.eu/art-23-gdpr/).