import math
import requests
from sqlalchemy_conn import db_conn
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from music_model import Song

# 创建请求头和会话
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'}
"""
创建一个session对象
requests库的session对象能够帮我们跨请求保持某些参数，也会在同一个session实例发出的所有请求之间保持cookies。
session对象还能为我们提供请求方法的缺省数据，通过设置session对象的属性来实现。
"""
session = requests.session()


# 下载歌曲
def download_music(song_mid, song_name):
    try:
        print('begin download--------------------------------------')
        file_name = 'C400' + song_mid
        """
        获取vkey
        原生地址：
        https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?g_tk=5381&
        jsonpCallback=MusicJsonCallback8359183970915902&loginUin=0&hostUin=0&
        format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&
        cid=205361747&callback=MusicJsonCallback8359183970915902&uin=0&songmid=002AOwqK2rwcrb&
        filename=C400002AOwqK2rwcrb.m4a&guid=3192684595
        优化后地址：
        https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?loginUin=0&hostUin=0&
        cid=205361747&uin=0&songmid=002AOwqK2rwcrb&filename=C400002AOwqK2rwcrb.m4a&guid=0
        """
        vkey_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?loginUin=0&hostUin=0' \
                   '&cid=205361747&uin=0&songmid={}&filename={}.m4a&guid=0'.format(song_mid, file_name)
        vkey_response = session.get(vkey_url, headers=headers)
        vkey = vkey_response.json()['data']['items'][0]['vkey']
        # 下载歌曲
        url = 'http://dl.stream.qqmusic.qq.com/{}.m4a?vkey={}&guid=0&uin=0&fromtag=66'.format(file_name, vkey)
        response = session.get(url, headers=headers)
        music_download_path = 'D:/music_download/{}.m4a'.format(song_name)
        with open(music_download_path, 'wb') as f_write:
            f_write.write(response.content)
    except Exception as ex:
        print('download error:{}'.format(ex))
        raise Exception


# 获取歌手的全部歌曲
def get_singer_songs(singer_mid):
    """
    获取歌手姓名和歌曲总数
    原生地址形式：
    https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?g_tk=5381&
    jsonpCallback=MusicJsonCallbacksinger_track&loginUin=0&hostUin=0&
    format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&
    needNewCode=0&singermid=003oUwJ54CMqTT&order=listen&begin=0&num=30&songstatus=1
    优化后地址形式：
    https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?loginUin=0&hostUin=0&
    singermid=003oUwJ54CMqTT&order=listen&begin=0&num=30&songstatus=1
    """
    url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?loginUin=0&hostUin=0&singermid={}' \
          '&order=listen&begin=0&num=30&songstatus=1'.format(singer_mid)
    r = session.get(url)
    """
    """
    # 获取歌手姓名
    song_singer = r.json()['data']['singer_name']
    # 获取歌曲总数
    song_count = r.json()['data']['total']
    # 根据歌曲总数计算总页数
    page_count = int(math.ceil(int(song_count) / 30))
    print('singer:{}, song count:{}'.format(song_singer, song_count))
    # 循环页数，获取每一页歌曲信息
    for page_num in range(page_count):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?loginUin=0&hostUin=0&singermid={}' \
              '&order=listen&begin={}&num=30&songstatus=1'.format(singer_mid, page_num * 30)
        r = session.get(url)
        # 得到每页的歌曲信息
        music_data = r.json()['data']['list']
        # songname-歌名，ablum-专辑，interval-时长，songmid歌曲id，用于下载音频文件
        down_num = 0
        for i in music_data:
            song_name = i['musicData']['songname']
            song_ablum = i['musicData']['albumname']
            song_interval = i['musicData']['interval']
            song_songmid = i['musicData']['songmid']
            # 下载歌曲
            download_music(song_songmid, song_name)
            # 入库处理
            song_obj = Song(song_name=song_name, song_ablum=song_ablum, song_interval=song_interval,
                            song_songmid=song_songmid, song_singer=song_singer)
            session_db = db_conn()
            session_db.add(song_obj)
            session_db.commit()
            session_db.close()
            down_num += 1
            # 为演示使用，此处示例下载5首歌曲
            if down_num > 5:
                break


# 获取当前字母下全部歌手
def get_alphabet_singer(alphabet, page_list):
    for page_num in page_list:
        url = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer&page=list&key=all_all_{}' \
              '&pagesize=100&pagenum={}&loginUin=0&hostUin=0&format=jsonp'.format(alphabet, page_num + 1)
        response = session.get(url)
        # 循环每一个歌手
        for k in response.json()['data']['list']:
            singer_mid = k['Fsinger_mid']
            get_singer_songs(singer_mid)


# 多线程
def multi_threading(alphabet):
    # 每个字母分类的歌手列表页数
    url = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer&page=list&' \
          'key=all_all_{}&pagesize=100&pagenum={}&loginUin=0&hostUin=0&format=jsonp'.format(alphabet, 1)
    response = session.get(url, headers=headers)
    page_num = response.json()['data']['total_page']
    page_list = [x for x in range(page_num)]
    thread_num = 5
    # 将每个分类总页数平均分给线程数
    per_thread_page = math.ceil(page_num / thread_num)
    # 设置线程对象
    thread_obj = ThreadPoolExecutor(max_workers=thread_num)
    for thread_order in range(thread_num):
        # 计算每条线程应执行的页数
        start_num = per_thread_page * thread_order
        if per_thread_page * (thread_order + 1) <= page_num:
            end_num = per_thread_page * (thread_order + 1)
        else:
            end_num = page_num
        # 每个线程各自执行不同的歌手列表页数
        thread_obj.submit(get_alphabet_singer, alphabet, page_list[start_num: end_num])


# 多进程
def execute_process():
    with ProcessPoolExecutor(max_workers=2) as executor:
        for i in range(65, 91):
            # 创建26个线程，分别执行A-Z分类
            executor.submit(multi_threading, chr(i))


if __name__ == '__main__':
    # 执行多进程多线程
    execute_process()
