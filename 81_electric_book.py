import asyncio
import aiohttp
import requests
import json
from lxml import etree
import re
import aiofiles
import os
import time
import random

book_name = ""

#第三百五十四章 黑铁之体大成！（为书友‘洛沉\’加更）
#title含有\所以cannot
#-------------已解决：增加特判
#已知访问次数过多会造成网页打不开 预估为卡掉ip
#-------------已解决：增加代理池


def get_ua():
    ua_list = [
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
        'User-Agent:Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'
    ]
    return random.choice(ua_list)



#增加代理即可
def get_ip():
    #每次使用时，需更新代理池，已知3个代理可下载5k章左右小说，推荐增加到10个代理ip
    proxy_list = [
        "http://223.96.90.216:8085", "http://112.6.117.178:8085","http://116.113.68.130:9091"
    ]
    # 随机选择一个代理
    return random.choice(proxy_list)


async def getCatalog(url):
    resp = requests.get(url)
    dic = resp.text
    resp.close()
    #print(dic)
    tasks = []
    obj = re.compile(r'<dd>.*?"(?P<content>.*?)".*?>(?P<name>.*?)<', re.S)
    result = obj.finditer(dic)
    for i in result:
        #http://www.81xs.com/
        name = i.group('name')
        """with open("D:\\Program\\python\\xinfadi.txt",
                  mode="a+",
                  encoding="utf-8") as f:
            now = i.group('content')
            #print("now is {num}")
            f.write("\n" + now)
        f.close()"""
        content = "http://www.81xs.com" + i.group('content')
        tasks.append(asyncio.create_task(aiodownload(name, content)))
    await asyncio.wait(tasks)


async def aiodownload(name, content):
    global book_name
    name = name.replace("?", "")
    name = name.replace("/", "")
    name = name.replace("\\", "")
    url = content
    obj_title = re.compile(r'showtxt.*?>(?P<title>.*?)<', re.S)
    obj = re.compile(r'br.*?>(?P<content>.*?)<', re.S)
    async with aiohttp.ClientSession() as session:
        headers = {'User-Agent': get_ua()}
        #f = 0
        async with session.get(url, headers=headers, proxy=get_ip()) as resp:
            try:  #尝试gbk解码
                txt = await resp.text(encoding='gbk')
                resp.close()
                ans = ""
                result_title = obj_title.finditer(txt)
                result = obj.finditer(txt)
                for i in result_title:
                    res = i.group('title')
                    res = res.replace(
                        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;",
                        "\n  ")
                    res = res.replace("\r", "")
                    ans = ans + res
                for i in result:
                    res = i.group('content')
                    res = res.replace(
                        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;",
                        "\n  ")
                    res = res.replace("\r", "")
                    ans = ans + res
                ans = ans.replace("&nbsp", "")
                with open(f"F:\\book\\{book_name}\\{name}.txt",
                          mode="w",
                          encoding='gbk') as f:
                    f.write(ans)
                f.close()
                #break
            except:  #gbk不可以 应正文含有生僻字 应换gb18030
                try:
                    txt = await resp.text(encoding='gb18030')
                    resp.close()
                    ans = ""
                    result_title = obj_title.finditer(txt)
                    result = obj.finditer(txt)
                    for i in result_title:
                        res = i.group('title')
                        res = res.replace(
                            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;",
                            "\n  ")
                        res = res.replace("\r", "")
                        ans = ans + res
                    for i in result:
                        res = i.group('content')
                        res = res.replace(
                            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;",
                            "\n  ")
                        res = res.replace("\r", "")
                        ans = ans + res
                    ans = ans.replace("&nbsp", "")
                    with open(f"F:\\book\\{book_name}\\{name}.txt",
                              mode="w",
                              encoding='gb18030') as f:
                        f.write(ans)
                    f.close()
                    #break
                except:  #出现bug 进行调试
                    """print(f"{f}")
                    txt = await resp.text(encoding='gbk')
                    resp.close()
                    result_title = obj_title.findall(txt)
                    result = obj.findall(txt)
                    
                    for i in range(result.__len__()):
                        result[i]=result[i].replace("\r","")
                    for i in range(result_title.__len__()):
                        result_title[i]=result_title[i].replace("\r","")   
                    ans = ""
                    for i in range(result_title.__len__()):
                        result_title[i]=result_title[i].replace(
                            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;",
                            "\n  ")
                        ans = ans + result_title[i]
                    #print("result_titile is not problem")
                    for i in range(result.__len__()):
                        result[i]=result[i].replace(
                            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;",
                            "\n  ")
                        ans = ans + result[i]
                    ans = ans.replace("&nbsp", "")
                    
                    print(type(ans))
                    with open(f"D:\\Program\\python\\text.txt",
                                mode="w",
                                encoding='gbk') as f:
                        f.write(ans)
                    f.close()
                    print("is not promble")
                    time.sleep(2)"""
                    #正则表达式爬取出\r的debug过程
                    print(f"{name} is cannot")


def find_book(name):
    url = f'http://www.81xs.com/s.php?ie=gbk&q={name}'
    resp = requests.get(url)
    txt = resp.text
    #print(txt)
    resp.close()
    obj_href = re.compile(
        r'<div class="bookbox">.*?a href="/book/(?P<href>.*?)/', re.S)
    obj_author = re.compile(r'<div class="author">(?P<author>.*?)</div>', re.S)
    obj_name = re.compile(r'class="bookname">.*?>(?P<name>.*?)<', re.S)
    result_href = obj_href.findall(txt)
    result_author = obj_author.findall(txt)
    result_name = obj_name.findall(txt)
    href = {}
    b_name = {}
    for i in range(result_name.__len__()):
        key = i
        result_author[i].replace("作者：", "")
        href[key] = result_href[i]
        b_name[key] = f'{result_name[i]} {result_author[i]}'
        print(f'书名：{result_name[i]} 作者：{result_author[i]} 下载标记：{key}')
    global book_name
    index = input("请输入你要下载的书的下载标记:")
    book_name = result_name[i]
    try:
        os.mkdir(f'F:\\book\\{book_name}')
    except:
        pass
    index = int(index)
    return href[index]


if __name__ == '__main__':
    name = input("请输入你要下载的书:")

    b_id = find_book(name)
    url = f'http://www.81xs.com/book/{b_id}/'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getCatalog(url))

    print("all over!")
