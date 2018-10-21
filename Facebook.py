from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import hashlib
import random
import time


class Facebook:
    def __init__(self, email, password, max_wait=10, site="https://www.facebook.com/", geckopath='/usr/local/bin/geckodriver'):
        self.driver = webdriver.Firefox(executable_path=geckopath)
        self.driver.get(site)
        self.login(email, password)
        self.max_wait = max_wait

    def login(self, email, password):
        self.driver.find_element_by_name('email').send_keys(email)
        self.driver.find_element_by_name('pass').send_keys(password)
        time.sleep(random.uniform(0, self.max_wait))
        self.driver.find_element_by_id('loginbutton').click()

    def goto_page(self, site):
        self.driver.get(site)

    def scrape(self, site):
        response = requests.get(site)
        soup = BeautifulSoup(response.content, 'lxml')
        f = soup.find('div', attrs={'class': '_4-u3 _5sqi _5sqk'})
        print(f.find('span', attrs={'class': '_52id _50f5 _50f7'}))

    def scroll(self, x, y):
        self.driver.execute_script("window.scrollTo(" + str(x) + ", " + str(y) + ")")

    def infinite_scroll(self, n):
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        i = 0

        for x in range(0, n):
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(random.uniform(0, 7))

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def scrape_mobile(self, number_of_pages):
        # Print column headers
        df = [["poster", "timestamp", "text", "num_likes", "num_loves", "num_hahas", "num_wows", "num_sads", "num_angrys", "num_reacts", "event_link", "hashtags_used", "reacted"]]
        links_to_stories = []
        # Scrape link of "Full Story" for each post.
        for page in range(0, number_of_pages):
            stories = self.driver.find_elements_by_xpath("//*[contains(text(), 'Full Story')]")
            for story in stories:
                links_to_stories.append(story.get_attribute('href'))
            time.sleep(random.uniform(0, self.max_wait))
            self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/a").click()

        # Traverses each story link and scrapes data
        for link in links_to_stories:
            time.sleep(random.uniform(0, self.max_wait))
            self.goto_page(link)
            # Scrape data
            try:
                poster = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/div[1]/div/div/div[3]/div[1]/div[1]/a").text
            except:
                poster = ""
            try:
                timestamp = self.parse_fb_date(self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/abbr").text)
            except:
                timestamp = ""
            try:
                # FB sometimes uses photo upload descriptions as the text chunk, so we try both places.
                text = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/div[1]/div[1]/div/div[1]/div[2]").text
                hashtags_used = self.get_hashtags(text)
            except:
                try:
                    text = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/div[1]/div/div/div[3]/div[1]/div[1]/div").text
                    hashtags_used = self.get_hashtags(text)
                except:
                    text = ""  # done
                    hashtags_used = []

            event_link = link  # done
            num_likes = 0  # done
            num_loves = 0  # done
            num_hahas = 0  # done
            num_wows = 0  # done
            num_sads = 0  # done
            num_angrys = 0  # done
            reacted = []

            # Click the reactions icon.
            self.driver.find_element_by_xpath('//a[contains(@href, "reaction/profile")]').click()
            # Start at 2 because "All" doesn't have an image element to scrape.
            for x in range(2, 10):
                try:
                    react = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table/tbody/tr/td/div/div/a[" + str(x) + "]/img").get_attribute('alt')
                    count = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table/tbody/tr/td/div/div/a[" + str(x) + "]").get_attribute('href')
                    count = count[count.find("total_count=") + len("total_count="):]
                    count = int(count[0: count.find("&")])
                    if react == "Like":
                        num_likes = count
                    elif react == "Love":
                        num_loves = count
                    elif react == "Haha":
                        num_hahas = count
                    elif react == "Wow":
                        num_wows = count
                    elif react == "Angry":
                        num_angrys = count
                    elif num_sads == "Sad":
                        num_angrys = count
                except:
                    break

            num_reacts = num_likes + num_loves + num_hahas + num_wows + num_sads + num_angrys  # done

            while True:
                try:
                    for x in range(1, 100):
                        try:
                            name = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table/tbody/tr/td/div/ul/li[" + str(x) + "]/table/tbody/tr/td/table/tbody/tr/td[3]/div/h3[1]").text
                            name = self.hash_sha256(name)  # Mandatory
                            reacted.append(name)
                        except:
                            break
                    time.sleep(random.uniform(0, self.max_wait))
                    self.driver.find_element_by_xpath("//*[contains(text(), 'See More')]").click()
                except:
                    break

            df.append([poster, timestamp, text, num_likes, num_loves, num_hahas, num_wows, num_sads, num_angrys, num_reacts, event_link, hashtags_used, reacted])
        return df



    @staticmethod
    def hash_sha256(string):
        """
        Failure to encrypt any personally identifiable information
        is a violation of the Global Data Protection Regulation.
        Also, don't be an @$$H0L3 with the data.
        """
        m = hashlib.sha256()
        m.update(bytearray(string, 'utf8'))
        m.digest()
        return str(m.hexdigest())

    def __enum_month__(self, month):
        return{
            'January': "01",
            'February': "02",
            'March': "03",
            'April': "04",
            'May': "05",
            'June': "06",
            'July': "07",
            'August': "08",
            'September': "09",
            'October': "10",
            'November': "11",
            'December': "12"
        }[month]

    def parse_fb_date(self, date, current_year=2018):
        month = date[0:date.find(" ")]
        date = date.replace(month, "").strip()
        month = self.__enum_month__(month)
        day = date[0:date.find(" ")]

        if len(day) == 1:
            day = "0" + day
        date = date.replace(day, "").strip()
        if date[0:date.find(" ")] == "at":
            year = str(current_year)
        else:
            year = date[:date.find(" ")]

            date = date.replace(year, "").strip()
        date = date.replace("at", "").strip()
        day = day.replace(",", "")
        if len(day) == 1:
            day = "0" + day

        # Now, to handle the time
        if date[-2:] == "PM":
            timestamp = str((int(date[0:2]) + 12) % 24) + date[2:5]
        else:
            timestamp = date[:-2].strip()
        if len(timestamp) == 4:
            timestamp = "0" + timestamp
        return day + "-" + month + "-" + year + " | " + timestamp

    def get_hashtags(self, string):
        words = string.split()
        list_out = []
        for word in words:
            if (len(word) > 2) and ("#" in word[0:1]):
                list_out.append(word)
        return list_out

