from selenium import webdriver
import datetime
import hashlib
import random
import time
import unicodecsv as csv


class Facebook:
    def __init__(self, email, password, max_wait=10, site="https://www.facebook.com/", geckopath='/usr/local/bin/geckodriver'):
        self.driver = webdriver.Firefox(executable_path=geckopath)
        self.driver.get(site)
        self.max_wait = max_wait
        self.login(email, password)

    def login(self, email, password):
        self.driver.find_element_by_name('email').send_keys(email)
        self.driver.find_element_by_name('pass').send_keys(password)
        time.sleep(random.uniform(0, self.max_wait * (1/6)))
        self.driver.find_element_by_id('loginbutton').click()

    def goto_page(self, site):
        self.driver.get(site)

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

    def scrape_mobile(self, number_of_pages, scrape_who_reacted=False, file_out='output.csv', hush_params=()):

        list_of_years = ["2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010", "2009"]
        year_pointer = 0

        # Test the hush params.
        try:
            can_hush = True
            if 4 >= len(hush_params) >= 2:
                x = Facebook.convert_to_time(hush_params[0])
                y = Facebook.convert_to_time(hush_params[1])
                if x != y:
                    can_hush = True
                else:
                    can_hush = False
                print("Enabling hush to sleep at", hush_params[0], "and wake at", hush_params[1])
            else:
                can_hush = False
        except:
            can_hush = False
            print("Invalid hush parameters.")

        # Print column headers
        df = [["text", "num_likes", "num_loves", "num_hahas", "num_wows", "num_sads", "num_angrys", "num_reacts", "event_link", "hashtags_used", "who_reacted"]]
        links_to_stories = []

        # Scrape link of "Full Story" for each post.
        with open("friendless_log.txt", "a") as log:
            for page in range(0, number_of_pages):
                    stories = self.driver.find_elements_by_xpath("//*[contains(text(), 'Full Story')]")
                    log.write(self.driver.current_url + "\n")
                    for story in stories:
                        links_to_stories.append(story.get_attribute('href'))
                        log.write("     " + str(story.get_attribute('href')) + "\n")
                    time.sleep(random.uniform(0, self.max_wait))
                    try:
                        x = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/div[1]/div[2]/div[2]/div[2]/a")
                        x.click()
                    except:
                        x = self.driver.find_element_by_xpath("//*[contains(text(), '" + list_of_years[year_pointer] + "')]")
                        x.click()
                        year_pointer += 1
                        if year_pointer >= len(list_of_years):
                            break

            log.close()

            with open("friendless_log.txt", "a") as log:
                log.write("\n\n<Console>\n\n")
                log.close()

        # Traverses each story link and scrapes data
        for link in links_to_stories:

            # Checks if the program should be put to sleep.
            if can_hush:
                Facebook.hush(str(hush_params[0]), str(hush_params[1]), seed=int(hush_params[2]), hit_box=int(hush_params[3]))

            time.sleep(random.uniform(0, self.max_wait))
            self.goto_page(link)
            # Scrape data
            try:
                poster = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/div[1]/div/div/div[3]/div[1]/div[1]/a").text
            except:
                poster = ""
            try:
                # Currently broken.
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
            who_reacted = []

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

            while scrape_who_reacted:
                try:
                    for x in range(1, 100):
                        try:
                            name = self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/table/tbody/tr/td/div/ul/li[" + str(x) + "]/table/tbody/tr/td/table/tbody/tr/td[3]/div/h3[1]").text
                            name = self.hash_sha256(name)  # Mandatory
                            who_reacted.append(name)
                        except:
                            break
                    time.sleep(random.uniform(0, self.max_wait))
                    self.driver.find_element_by_xpath("//*[contains(text(), 'See More')]").click()
                except:
                    break
            x = (".post text: | " + text + "\"\n" +
                 ".num_likes: | " + str(num_likes) + "\n" +
                 ".num_loves: | " + str(num_loves) + "\n" +
                 ".num_hahas: | " + str(num_hahas) + "\n" +
                 "..num_wows: | " + str(num_wows) + "\n" +
                 "..num_sads: | " + str(num_sads) + "\n" +
                 "num_angrys: | " + str(num_angrys) + "\n" +
                 "num_reacts: | " + str(num_reacts) + "\n" +
                 "event_link: | " + str(event_link) + "\n" +
                 "hashtags_used: " + str(hashtags_used) + "\n" +
                 "who_reacted:" + str(who_reacted) + "\n\n")
            print(x)
            with open("friendless_log.txt", "a") as log:
                log.write(x)
                log.close()

            df.append([str(text), str(num_likes), str(num_loves), str(num_hahas), str(num_wows), str(num_sads), str(num_angrys), str(num_reacts), str(event_link), str(hashtags_used), str(who_reacted)])
            with open(file_out, 'ab') as csv_file:
                writer = csv.writer(csv_file, lineterminator='\n')
                writer.writerow([str(text), str(num_likes), str(num_loves), str(num_hahas), str(num_wows), str(num_sads), str(num_angrys), str(num_reacts), str(event_link), str(hashtags_used), str(who_reacted)])
            csv_file.close()
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
        # Currently broken.
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

    def immitate_sleep(self, t_sleep, t_wake):
        print(datetime.datetime.now())

    @staticmethod
    def right_now():
        now = str(datetime.datetime.now())
        return [datetime.timedelta(hours=int(now[11:13]), minutes=int(now[14:16]), seconds=int(now[17:19])), int(now[0:4]), int(now[5:7]), int(now[8:10])]

    @staticmethod
    def convert_to_time(t):
        return datetime.timedelta(hours=int(t[0:2]), minutes=int(t[3:5]))

    @staticmethod
    def get_seconds(timedelta):
        t = str(timedelta)[-8:-3]
        if len(t) == 4:
            t = "0" + t
        return (float(t[0:2]) + (float(t[3:5]) / 60)) * 3600

    @staticmethod
    def hush(t_sleep, t_wake, seed=1800, hit_box=600):
        """
        Boolean returns are used in case of feeding
        the hush() function sleep/wake times from a
        cyclical/linear list. If True is returned,
        we know to move on to the next sleep/wake.
        """
        if t_sleep == t_wake:
            return True
        t_sleep = Facebook.convert_to_time(t_sleep)
        d = abs(t_sleep - Facebook.right_now()[0])
        if Facebook.get_seconds(d) <= hit_box:
            t_wake = Facebook.convert_to_time(t_wake)
            d = t_wake - t_sleep
            d = Facebook.get_seconds(d)
            r = random.uniform(-seed, seed)
            print("Nighty-night... ", Facebook.right_now()[0])
            time.sleep(d + r)
            print("I'm up! ", Facebook.right_now()[0])
            return True