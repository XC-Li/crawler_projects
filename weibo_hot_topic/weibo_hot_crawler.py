"""
Web Crawler for Weibo (Chinese version of twitter) Hot Words(微博热搜）
Designed By: Xiaochi (George) Li

This program fetches the hot words and heat index from Hot Weibo(热搜榜） (https://s.weibo.com/top/summary?cate=realtimehot),
read count and discussion count from Weibo Search（关键词搜索）(https://s.weibo.com/weibo?q) every 10 minutes
It then stores the information into a CSV file.

Defined in get_hot()
CSV contains: 10 columns(index, year, month, day, hour, minute, key_word, number, read, discuss)
index（序号）: the current rank of the key_word
key_word（关键词）: the hot word (in chinese, encoding: utf-8)
number（热搜指数）: the heat index
read(阅读）: the read count
discussion（讨论）: the discussion count
"""

from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import time
from datetime import timedelta, datetime
import csv
import os


def transform_number(s):
    """Transfer number with chinese unit into real number"""
    if s[-1] == '亿':
        return int(float(s[:-1])*1e8)
    elif s[-1] == '万':
        return int(float(s[:-1])*1e4)
    else:
        return int(s)


def get_read_discuss(keyword):
    """get read count and discussion count
    :parameter
        keyword: keyword in chinese, encoding: utf-8
    :return
        read, discuss float
    :except
        return -1, -1"""
    link = quote('#'+keyword+'#')
    url = 'https://s.weibo.com/weibo?q='+link
    try:
        response = urlopen(url, timeout=30)
        soup = BeautifulSoup(response, 'lxml')
        text = soup.find('div', 'total')
        read = transform_number(text.find_all('span')[0].string[2:])
        discuss = transform_number(text.find_all('span')[1].string[2:])
        return read, discuss

    except:
        return -1, -1


def get_time():
    """return date and time in tuple"""
    if time.localtime(time.time()).tm_isdst == 0:
        dt = str(datetime.now() + timedelta(hours=13))
    else:
        dt = str(datetime.now() + timedelta(hours=12))
    year = dt[0:4]
    month = dt[5:7]
    day = dt[8:10]
    hour = dt[11:13]
    minute = dt[14:16]

    return year, month, day, hour, minute


def get_hot():
    """get hot words
    :return
        hot_list contain 10 columns
        (index:int, year:str, month:str, day:str, hour:str, minute:str,
        key_word:str, number:int, read:float, discuss:float)
    """
    year, month, day, hour, minute = get_time()
    hot_url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    response = urlopen(hot_url,timeout=30)
    soup = BeautifulSoup(response, 'lxml')
    hot_list = []
    print('key_word,number, read, discuss')
    index = 1
    for i in soup.find_all(name='tr'):
        text = i.find('td', 'td-02')
        if text is not None:
            key_word = text.a.contents[0]
            # link = text.a.attrs['href']
            if text.span is not None:
                number = text.span.string
                read, discuss = get_read_discuss(key_word)
                for try_count in range(5):  # More Stable: retry to get read and discuss
                    if read != -1:
                        break
                    else:
                        print('retry:', try_count + 1)
                        read, discuss = get_read_discuss(key_word)
                        time.sleep(try_count + 2)
                time.sleep(2)
                print(index, year, month, day, hour, minute,key_word, number, read, discuss)
                hot_list.append([index, year, month, day, hour, minute, key_word, number, read, discuss])
                index += 1
    return hot_list


def write_csv(hot_list):
    """write to csv
    :parameter
        hot_list, 2d list"""
    year, month, _, _, _ = get_time()
    with open(str(year)+'-'+str(month)+'.csv', 'a') as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n')
        for row in hot_list:
            writer.writerow(row)


"""Main Function"""
while True:
    year, month, day, hour, minute = get_time()
    if minute in ['00', '10', '20', '30', '40', '50']:
    # if True:  # For Debug
        try:
            hot_list = get_hot()
            print("Writing file")
            write_csv(hot_list)
        except KeyboardInterrupt:
            print("End")
            break
        except:
            print('some error', year, month, day, hour, minute)
            time.sleep(10)

    else:
        print('Waiting', year, month, day, hour, minute)
        time.sleep(10)
        os.system('clear')

