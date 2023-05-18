import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def asiae_search(search_word="아시아경제") :
    # 창 숨기는 옵션 추가 ----------------------
    op = webdriver.ChromeOptions()
    op.add_argument("headless")
    #----------------------------------------
    driver = webdriver.Chrome('chromedriver_110.exe',options=op)
    driver.get("https://www.asiae.co.kr/list/finance")

    htmlstr = driver.page_source
    soup = BeautifulSoup(htmlstr, features="html.parser")
    div_list = soup.select("#container > div.content > div.cont_listarea > div.cont_list > div")
    news_list = []
    for div in div_list[:5]:
        url = div.select_one("div > a").get('href')
        title = div.select_one("div > a").get('title')
        img = div.select_one("div > a > img").get('src')
        des = div.select_one("p").text
        print(title, url, img)
        news_list.append([title, url, img,des])

    print(len(news_list))
    df = pd.DataFrame(news_list, columns=["title", "url", "img",'des'])
    print(df.head(1))
    print(df.info())
    df.to_csv("news_sel_res.csv", index=False)
    return news_list
asiae_search(search_word="아시아경제")