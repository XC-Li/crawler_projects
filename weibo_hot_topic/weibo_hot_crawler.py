from urllib.request import urlopen
from urllib.parse import quote
from bs4 import BeautifulSoup
import time
from datetime import timedelta, datetime
import csv
import os


def transform_number(s):
    if s[-1] == '亿':
        return int(float(s[:-1])*1e8)
    elif s[-1] == '万':
        return int(float(s[:-1])*1e4)
    else:
        return int(s)


def get_read_discuss(keyword):
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
    year, month, day, hour, minute = get_time()
    hot_url = 'https://s.weibo.com/top/summary?cate=realtimehot'
    response = urlopen(hot_url,timeout=30)
    soup = BeautifulSoup(response, 'lxml')
    hot_list = []
    print('key_word,number, read, discuss')
    index = 1
    for i in soup.find_all(name='tr'):
        text = i.find('td','td-02')
        if text is not None:
            key_word = text.a.contents[0]
            # link = text.a.attrs['href']
            if text.span is not None:
                number = text.span.string
                read, discuss = get_read_discuss(key_word)
                for try_count in range(3):  # retry to get read and discuss
                    if read != -1:
                        break
                    else:
                        print('retry:', try_count + 1)
                        read, discuss = get_read_discuss(key_word)
                        time.sleep(2)
                time.sleep(2)
                print(index, year, month, day, hour, minute,key_word, number, read, discuss)
                hot_list.append([index, year, month, day, hour, minute, key_word, number, read, discuss])
                index += 1
    return hot_list


def write_csv(hot_list):
    year, month, _, _, _ = get_time()
    with open(str(year)+'-'+str(month)+'.csv', 'a') as csvFile:
        writer = csv.writer(csvFile, lineterminator='\n')
        for row in hot_list:
            writer.writerow(row)


while True:
    year, month, day, hour, minute = get_time()
    if minute in ['00', '10', '20', '30', '40', '50']:
    # if True:
        try:
            hot_list = get_hot()
            print("Writing file")
            write_csv(hot_list)
        except KeyboardInterrupt:
            print("End")
            break
        except:
            print('some error',year, month, day, hour, minute)
            time.sleep(10)

    else:
        print('Waiting',year, month, day, hour, minute)
        time.sleep(10)
        os.system('clear')

