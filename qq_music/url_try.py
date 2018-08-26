import requests
from bs4 import BeautifulSoup
import re
import json

session = requests.session()

headers = {'Accept-Language': 'zh-CN,zh;q=0.8', 'Cache-Control': 'max-age=0',
           'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

# QQ_MUSIC_SINGER_URL = 'https://u.y.qq.com/cgi-bin/musicu.fcg?callback=getUCGI1986419190708677' \
#                       '&g_tk=69824246&jsonpCallback=getUCGI1986419190708677&loginUin=825393011&hostUin=0' \
#                       '&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0' \
#                       '&data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A10000%7D%2C%22singerList%22' \
#                       '%3A%7B%22module%22%3A%22Music.SingerListServer%22%2C%22method%22%3A%22' \
#                       'get_singer_list%22%2C%22param%22%3A%7B%22area%22%3A-100%2C%22sex%22%3A-100%2C%22' \
#                       'genre%22%3A-100%2C%22index%22%3A-100%2C%22sin%22%3A0%2C%22cur_page%22%3A1%7D%7D%7D'

# QQ_MUSIC_SINGER_URL = 'https://u.y.qq.com/cgi-bin/musicu.fcg?callback=getUCGI1986419190708677' \
#                       '&data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A10000%7D%2C%22singerList%22' \
#                       '%3A%7B%22module%22%3A%22Music.SingerListServer%22%2C%22method%22%3A%22' \
#                       'get_singer_list%22%2C%22param%22%3A%7B%22area%22%3A-100%2C%22sex%22%3A-100%2C%22' \
#                       'genre%22%3A-100%2C%22index%22%3A-100%2C%22sin%22%3A0%2C%22cur_page%22%3A1%7D%7D%7D'

QQ_MUSIC_SINGER_URL = 'https://u.y.qq.com/cgi-bin/musicu.fcg?callback=getUCGI1986419190708677' \
                      '&data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A10000%7D%2C%22singerList%22' \
                      '%3A%7B%22module%22%3A%22Music.SingerListServer%22%2C%22method%22%3A%22' \
                      'get_singer_list%22%2C%22param%22%3A%7B%22area%22%3A-100%2C%22sex%22%3A-100%2C%22' \
                      'genre%22%3A-100%2C%22index%22%3A-100%2C%22sin%22%3A0%2C%22cur_page%22%3A1%7D%7D%7D'


# 取得所有字母
def get_all_letter():
    # 根据url获取内容
    r = requests.get(QQ_MUSIC_SINGER_URL, headers=headers)
    print(QQ_MUSIC_SINGER_URL)
    all_content = r.content.decode('utf-8')
    print('all content is:\n{}'.format(all_content))
    # 获取内容根据条件截取后转为字典
    content_dict = eval(all_content[all_content.find("{"): len(all_content) - 1])
    print('content dict is:\n{}'.format(content_dict))
    # 从字典中获取key为singerList的值
    singerList_dict = content_dict.get('singerList')
    print('singer list dict is:\n{}'.format(singerList_dict))
    # 从singerList_dict中获取key为data的值
    data_dict = singerList_dict.get('data')
    print('data dict is:\n{}'.format(data_dict))
    # 从data_dict中获取key为tags的值
    tags_dict = data_dict.get('tags')
    print('tags dict is:\n{}'.format(tags_dict))
    # 从tags_dict中获取key为index的值
    index_list = tags_dict.get('index')
    print('index list is:\n{}'.format(index_list))
    # 遍历 index_list
    for item_dict in index_list:
        print('集合中的单个元素:{}'.format(item_dict))
        print('字典中的name值-------:{}'.format(item_dict.get('name')))


# 通过解析html方式
def get_by_html():
    url = 'https://y.qq.com/portal/singer_list.html'
    r = requests.get(url, headers=headers)
    print('获取网页内容:{}'.format(r.content))
    soup = BeautifulSoup(r.content.decode('utf-8'), 'html5lib')
    print('打印BeautifulSoup对象:{}'.format(soup))
    # 查找所有div 块中含 singer_tag__list js_area 标识的文本
    singer_tag_group = soup.find_all('div', re.compile('singer_tag__list js_area'))[0].find_all('a')
    print('singer tag group:{}'.format(singer_tag_group))
    # 查找所有div 块中含 singer_tag__list js_letter 标识的文本
    alphas_group = soup.find_all('div', re.compile('singer_tag__list js_letter'))[0].find_all('a')
    print('alphas group:{}'.format(alphas_group))


# 获取字字母分类下总歌手页数
def get_all_singer():
    # 获取字母A-Z全部歌手
    for chr_i in range(65, 91):
        key_chr = chr(chr_i)
        # 获取每个字母分类下总歌手页数
        url = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer&page=list&key=all_all_{}' \
              '&pagesize=100&pagenum={}&loginUin=0&hostUin=0&format=jsonp'.format(key_chr, 1)
        response = session.get(url, headers=headers)
        page_num = response.json()['data']['total_page']
        page_list = [x for x in range(page_num)]
        print('chr:{}, total page:{}'.format(chr_i, len(page_list)))


def main():
    # get_all_letter()
    get_by_html()
    # get_all_singer()


if __name__ == "__main__":
    main()
