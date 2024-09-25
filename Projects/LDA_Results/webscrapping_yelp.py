import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import time

start_time = time.time()
rating_set = {}
reviews_set = []
result_set = []
link_list = []
ratings_dict = {str(i): [] for i in range(1, 6)} 

def web_scrap(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            html_content = bs(response.content, "html.parser")
            ul = html_content.find("ul", class_="undefined list__09f24__ynIEd")
            if ul:
                div_class = ul.find_all("h3", class_="css-1agk4wl")
                for span_element in div_class:
                    span_ele = span_element.find("span", class_='css-1egxyvc')
                    link = span_element.find("a", class_="css-19v1rkv")
                    Doc_link = link.get("href")
                    link_list.append(Doc_link)
                    Doc_name = span_ele.get_text(strip=True)
                    result_set.append(Doc_name)
            else:
                print("bad request")
    except requests.RequestException as e:
        print(f"Error during web scraping: {e}")

def scrap_ratings(doctor_url, url_count):
    try:
        print("entered")
        preurl = "https://www.yelp.com"
        for i in range(0, url_count):
            if i%10 == 0:
                time.sleep(20)
            url = preurl + doctor_url[i]
            for j in range(5, 0, -1):
                com_url = url + "&rr=" + str(j)
                #print(com_url)
                response = requests.get(com_url)
                if response.status_code == 200:
                    html_content1 = bs(response.content, "html.parser")
                    res1 = html_content1.find_all("div", class_="arrange-unit__09f24__rqHTg css-v3nuob")
                    reviews_list_items = html_content1.find_all("li", class_ = "css-1q2nwpv")
                    for each_listitem in reviews_list_items:
                        div_class = each_listitem.find("div", class_ = "css-10n911v")
                        if div_class:
                            sub_div = div_class.find("div", class_="arrange-unit__09f24__rqHTg arrange-unit-fill__09f24__CUubG css-1qn0b6x")
                            if sub_div:
                                review_date = sub_div.find('span').text
                                date = int(review_date[-4:])
                                if date and date >= 2021:
                                    l = each_listitem.find('div', class_='css-9ul5p9')
                                    text_content = l.find('span', class_='raw__09f24__T4Ezm')
                                    remove_span = str(text_content)
                                    cleaned_text = remove_span.replace('<span class="raw__09f24__T4Ezm" lang="en">', '').replace('</span>', '').replace('<br/>','')
                                    #reviews_set.append(cleaned_text)
                                    if text_content:
                                        reviews_set.append(cleaned_text)
                                    else:
                                        reviews_set.append('N/A')
                    for div_element1 in res1:
                        span_elements1 = div_element1.find_all("span", class_="css-qgunke")
                        for span_element1 in span_elements1:
                            span_value1 = span_element1.get_text(strip=True)
                            #print("Span Value:", span_value1)
                            # Append span_value1 to the corresponding key in the ratings_dict
                            ratings_dict[str(j)].append(span_value1)
                else:
                    print("bad request")
            #print(reviews_set)
            #print(ratings_dict)
            if i%40 == 0:
                print(reviews_set,ratings_dict)
    except requests.RequestException as e:
        print(f"Error during rating scraping: {e}")

if __name__ == "__main__":
    url = "https://www.yelp.com/search?find_desc=Physicians&find_loc=Cleveland%2C+OH&start="
    for i in range(0, 220, 10):
        concat_url = url + str(i)
        if i%30 == 0:
            time.sleep(20)
        web_scrap(concat_url)
