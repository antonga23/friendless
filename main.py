from Your import *
from Facebook import *
import unicodecsv as csv

email = Your.username_here()  # DO NOT COMMIT WITH THIS INFO
password = Your.password_here()    # DO NOT COMMIT WITH THIS INFO
number_of_pages = 3000

fb = Facebook(email, password, max_wait=1, geckopath='C:\Windows\geckodriver.exe')
fb.goto_page("https://www.facebook.com/pg/BMOREHUMANE/posts/?ref=page_internal")
fb.goto_page("https://mobile.facebook.com/BMOREHUMANE/?refid=46&__xts__%5B0%5D=12.%7B%22unit_id_click_type%22%3A%22graph_search_results_item_tapped%22%2C%22click_type%22%3A%22result%22%2C%22module_id%22%3A1%2C%22result_id%22%3A163178644527%2C%22session_id%22%3A%2271ec4d9862980ac9f93cef83dd54251a%22%2C%22module_role%22%3A%22ENTITY_PLACES%22%2C%22unit_id%22%3A%22browse_rl%3A59467fae-725e-3efc-0cf2-43b59de43d37%22%2C%22browse_result_type%22%3A%22browse_type_place%22%2C%22unit_id_result_id%22%3A163178644527%2C%22module_result_position%22%3A0%7D")
df = fb.scrape_mobile(number_of_pages, scrape_who_reacted=True, hush_params=["21:30", "07:30", 30, 30])

with open("final.csv", 'wb') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(df)
