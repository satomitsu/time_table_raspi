#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import requests
import re
from bs4 import BeautifulSoup
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
import datetime
import jpholiday

import logging
from waveshare_epd import epd2in13_V3
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)



try:
    logging.info("epd2in13_V3 Demo")
    
    epd = epd2in13_V3.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    # Drawing on the image
    font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
    font20 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    
    logging.info("1.Drawing on the image...")
    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame    
    draw = ImageDraw.Draw(image)
    # 現在時刻の取得
    dt_now = datetime.datetime.now()
    #アクセスするURL：Tokyoをセット
    url_shinjuku_weekday = 'https://transit.yahoo.co.jp/timetable/22929/3090?kind=1'
    url_shinjuku_weekend = 'https://transit.yahoo.co.jp/timetable/22929/3090?kind=2'
    url_atsugi_weekday = 'https://transit.yahoo.co.jp/timetable/22929/3091?kind=1'
    url_atsugi_weekend = 'https://transit.yahoo.co.jp/timetable/22929/3091?kind=2'
    url_tokyo_weather = 'https://weather.yahoo.co.jp/weather/jp/13/4410.html'
    # 今日が祝日かどうか判定する
    # holiday = jpholiday.is_holiday(datetime.date(2023, 3, 25))
    # print(holiday)
    if datetime.date.today().weekday() >= 5 or jpholiday.is_holiday(datetime.date.today()):
        holiday = 1
    else:
        holiday = 0
    #URLにアクセスする：アクセス結果は「resp」に帰ってくる
    if holiday == 1:
        resp_transit_shinjuku = requests.get(url_shinjuku_weekend)
        resp_transit_atsugi = requests.get(url_atsugi_weekend)
    else:
        resp_transit_shinjuku = requests.get(url_shinjuku_weekday)
        resp_transit_atsugi = requests.get(url_atsugi_weekday)
    resp_weather = requests.get(url_tokyo_weather)
    
    #「resp」らHTMLを取り出して、BeautifulSoupで扱えるようにパースする
    soup_transit_shinjuku = BeautifulSoup(resp_transit_shinjuku.text, "html.parser")
    soup_transit_atsugi = BeautifulSoup(resp_transit_atsugi.text, "html.parser")
    soup_weather = BeautifulSoup(resp_weather.text, "html.parser")
    #以下、CSSセレクターでHTMLからテキストを取得
    #今日の日付
    today_date = soup_weather.select_one('#main > div.forecastCity > table > tr > td > div > p.date')
    #今日の天気
    tenki_today = soup_weather.select_one('#main > div.forecastCity > table > tr > td > div > p.pict')
    #今日の最高気温
    high_today = soup_weather.select_one('#main > div.forecastCity > table > tr > td > div > ul > li.high')
    #今日の最低気温
    low_today = soup_weather.select_one('#main > div.forecastCity > table > tr > td > div > ul > li.low')
    #明日の天気
    tenki_tomorrow = soup_weather.select_one('#main > div.forecastCity > table > tr > td + td > div > p.pict')
    #電車時刻表示
    # transit = soup_transit.find_all(href=re.compile("/timetable/22929/3090"))
    transit_shinjuku = soup_transit_shinjuku.find_all("dt")
    transit_atsugi = soup_transit_atsugi.find_all("dt")
    #天気の表示
    print (today_date.text.replace('\n','')+"の天気")
    print ("今日の天気は"+tenki_today.text.replace('\n',''))
    print ("今日の最高気温は"+high_today.text)
    print ("今日の最低気温は"+low_today.text)
    print ("明日の天気は"+tenki_tomorrow.text.replace('\n','')) 
    transit_time_shinjuku_min = []
    transit_time_atsugi_min = []
    for i in range(len(transit_shinjuku)-1):
        if "hour" in str(transit_shinjuku[i]):
            if int(transit_shinjuku[i].contents[0]) == 0:
                transit_time_shinjuku_H_min = 24*60
                # print (transit_time_H_min)
            else:
                transit_time_shinjuku_H_min = int(transit_shinjuku[i].contents[0])*60
                # print (transit_time_H_min)
            # print (transit[i].contents[0])            
        else:
            transit_time_shinjuku_min.append(transit_time_shinjuku_H_min + int(transit_shinjuku[i].contents[1]))
    for l in range(len(transit_atsugi)-1):
        if "hour" in str(transit_atsugi[l]):
            if int(transit_atsugi[l].contents[0]) == 0:
                transit_time_atsugi_H_min = 24*60
            else:
                transit_time_atsugi_H_min = int(transit_atsugi[l].contents[0])*60        
        else:
            transit_time_atsugi_min.append(transit_time_atsugi_H_min + int(transit_atsugi[l].contents[1]))
    dt_now_min = int(dt_now.hour)*60 + dt_now.minute
    for j in range(len(transit_time_shinjuku_min)-3):
        if dt_now_min <= transit_time_shinjuku_min[j]:
            transit_time_shinjuku_min_now_1 = transit_time_shinjuku_min[j] % 60
            transit_time_shinjuku_min_now_2 = transit_time_shinjuku_min[j+1] % 60
            transit_time_shinjuku_min_now_3 = transit_time_shinjuku_min[j+2] % 60
            break
    for k in range(len(transit_time_atsugi_min)-3):
        if dt_now_min <= transit_time_atsugi_min[k]:
            transit_time_atsugi_min_now_1 = transit_time_atsugi_min[k] % 60
            transit_time_atsugi_min_now_2 = transit_time_atsugi_min[k+1] % 60
            transit_time_atsugi_min_now_3 = transit_time_atsugi_min[k+2] % 60
            break

    draw.text((10, 0), today_date.text, font = font15, fill = 0)
#    draw.text((20, 20), "Weather:", font = font15, fill = 0)
#    draw.text((150, 0), tenki_today.text, font = font15, fill = 0) 
#    draw.text((20, 40), "Temp_high:", font = font15, fill = 0)
    # draw.text((150, 40), high_today.text, font = font15, fill = 0)  
    draw.text((20, 50), "新宿:", font = font20, fill = 0)
    draw.text((80, 50), str(dt_now.hour), font = font20, fill = 0)
    draw.text((110, 50), str(transit_time_shinjuku_min_now_1), font = font20, fill = 0)
    draw.text((140, 50), str(transit_time_shinjuku_min_now_2), font = font20, fill = 0)
    draw.text((170, 50), str(transit_time_shinjuku_min_now_3), font = font20, fill = 0)
    draw.text((20, 80), "本厚木:", font = font20, fill = 0)
    draw.text((80, 80), str(dt_now.hour), font = font20, fill = 0)
    draw.text((110, 80), str(transit_time_atsugi_min_now_1), font = font20, fill = 0)
    draw.text((140, 80), str(transit_time_atsugi_min_now_2), font = font20, fill = 0)
    draw.text((170, 80), str(transit_time_atsugi_min_now_3), font = font20, fill = 0)
    image = image.rotate(180) # rotate
    epd.display(epd.getbuffer(image))
    time.sleep(64800)
    
    # read bmp file 
    logging.info("2.read bmp file...")
    image = Image.open(os.path.join(picdir, '2in13.bmp'))
    epd.display(epd.getbuffer(image))
    time.sleep(20)
    
    epd.displayPartBaseImage(epd.getbuffer(time_image))
    logging.info("Clear...")
    epd.init()
    epd.Clear(0xFF)
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in13_V3.epdconfig.module_exit()
    exit()