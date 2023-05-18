from flask import Flask, render_template, make_response, jsonify, request, redirect, url_for

import numpy as np
import pandas as pd

import folium
from folium.plugins import MarkerCluster

import geopandas as gpd

from youtubesearchpython import VideosSearch
import json

import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import os

app = Flask(__name__)

def my_youtube_search(search_str='소비패턴', nrows=5):
	videosSearch = VideosSearch(search_str, limit=nrows)
	json_res = videosSearch.result()

	movie_list = json_res['result']
	# print(json.dumps(movie_list, sort_keys=True, indent=4))

	tot_list = []
	for movie in movie_list:
		dict = {}

		dict["title"] 	 = movie['title']
		try :
			dict["movie"] = movie['richThumbnail']['url']
		except :
			dict["movie"] = movie['thumbnails'][0]['url']
		dict["img"] 	 = movie['thumbnails'][0]['url']
		dict["duration"] = movie['duration']
		dict["url"] 	 = movie['link']
		dict["rdate"] 	 = movie['publishedTime']
		dict["cnt"]  = movie['viewCount']['text']
		tot_list.append(dict)
	return tot_list

def make_map(gubun, width, height, colors='Reds'):
    # 지도 관련
    state_geo = gpd.read_file('./data/seoul_geo_sigugun.json')
    df = pd.read_csv('./data/집계구별 일별소비지역별 카드소비패턴.csv', encoding='cp949')
    df = df.dropna()

    df2 = pd.read_csv('./data/mean_data.csv')
    df2 = pd.read_csv('./data/mean_data.csv', sep="/")
    df2.rename(columns={'Unnamed: 0': '가맹점주소시군구(SGG)', '0': '인구수'}, inplace=True)

    state_list = state_geo['name'].values.tolist()
    if gubun == "금액":
        gdf = df[df['가맹점주소시군구(SGG)'].isin(state_list)].groupby('가맹점주소시군구(SGG)')['카드이용금액계(AMT_CORR)'].sum()
        col_list = ['가맹점주소시군구(SGG)', '카드이용금액계(AMT_CORR)']
    elif gubun == "건수":
        gdf = df[df['가맹점주소시군구(SGG)'].isin(state_list)].groupby('가맹점주소시군구(SGG)')['카드이용건수계(USECT_CORR)'].sum()
        col_list = ['가맹점주소시군구(SGG)', '카드이용건수계(USECT_CORR)']
    else:
        gdf = df2
        col_list = ['가맹점주소시군구(SGG)', '인구수']


    gdf = gdf.reset_index()

    map = folium.Map(location=[37.562225, 126.978555], tiles="OpenStreetMap", zoom_start=10)

    map.choropleth(
        geo_data=state_geo,
        name='인구밀도',
        data=gdf,
        columns=col_list,
        key_on='feature.properties.name',
        fill_color=colors,  # if state_geo["code"].str == '11250' else 'Reds',      # 'Blues',
        fill_opacity=0.7,
        line_opacity=0.3,
        color='gray',
        legend_name='income'
    )

    folium.plugins.MousePosition().add_to(map)

    map.get_root().width = width
    map.get_root().height = height
    html_str = map.get_root()._repr_html_()

    return html_str

# def asiae_search(search_word="아시아경제"):
#     op = webdriver.ChromeOptions()
#     op.add_argument("headless")
#
#     driver = webdriver.Chrome('chromedriver_110.exe', options=op)
#
#     driver.get("https://www.asiae.co.kr/list/finance")
#     htmlstr = driver.page_source
#
#     soup = BeautifulSoup(htmlstr, features="html.parser")
#     div_list = soup.select("#container > div.content > div.cont_listarea > div.cont_list > div")
#     news_list = []
#     for div in div_list[:5]:
#         url = div.select_one("div > a").get('href')
#         title = div.select_one("div > a").get('title')
#         img = div.select_one("div > a > img").get('src')
#         des = div.select_one("p").text
#         print(title, url, img)
#         news_list.append({'title':title, 'url':url, 'img':img, 'des':des})
#
#     # print(len(news_list))
#     # df = pd.DataFrame(news_list, columns=["title", "url", "img",'des'])
#     # print(df.head(1))
#     # print(df.info())
#     # df.to_csv("news_sel_res.csv", index=False)
#     return news_list


@app.route('/')
def index():
    # 지도 관련
    html_str = make_map("금액", "550px", "400px")

    # 유튜브 관련
    tot_list = my_youtube_search('소비패턴', 5)
    # df = pd.DataFrame(tot_list)
    # print(df.head())

    # 뉴스 관련
    # news_list = asiae_search("아시아경제")
    new_df = pd.read_csv('./data/news_sel_res.csv')
    news_list = new_df.values.tolist()

    return render_template('index.html', KEY_MAP=html_str, YTB_DIC = tot_list, NEWS_DIC = news_list)

@app.route('/gen_age_page')
def gen_age_page():
    return render_template('gen_age_page.html')

@app.route('/year_month_page')
def year_month_page():
    return render_template('year_month_page.html')

@app.route('/time_page')
def time_page():
    return render_template('time_page.html')

@app.route('/region_page')
def region_page():
    html_str1 = make_map("금액", "420px", "300px")
    html_str2 = make_map("건수", "420px", "300px")
    html_str3 = make_map("인구", "420px", "300px", "Blues")
    return render_template('region_page.html', KEY_MAP1=html_str1,KEY_MAP2=html_str2,KEY_MAP3=html_str3)

@app.route('/gallary_page')
def gallary_page():
    file_list = os.listdir(".\\static\\assets\\images\\gallary")
    print(file_list)

    return render_template('gallary_page.html', IMG_NAME = file_list)

# 텍스트로 보내고, 텍스트로 받음
@app.route('/form_rest_text_text', methods=['POST'])
def form_rest_text_text():
    parm_id = request.form.get('usrid')
    print("id ", parm_id)
    html_str1 = make_map("금액", "550px", "400px")

    return jsonify({"msg":html_str1})

# 텍스트로 보내고, 텍스트로 받음
@app.route('/form_rest_text_text2', methods=['POST'])
def form_rest_text_text2():
    parm_id = request.form.get('usrid')
    print("id222 ", parm_id)

    html_str1 = make_map("건수", "550px", "400px")
    return jsonify({"msg":html_str1})

@app.route('/form_rest_text_text3', methods=['POST'])
def form_rest_text_text3():
    parm_id = request.form.get('usrid')
    print("id222 ", parm_id)

    html_str1 = make_map("인구", "550px", "400px","Blues")
    return jsonify({"msg":html_str1})


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=1115)