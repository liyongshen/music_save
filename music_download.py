import json
import os
import threading

import eyed3
import requests

web_url = 'https://www.sunweihu.com/sou-music/'
header = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}


def search_music(name, artist):
    data = {
        "input": f"{name} {artist}",
        "filter": "name",
        "type": "netease",  # {"netease": "网易云", "qq": "QQ","kugou": "酷狗", "kuwo": "酷我", "xiami": "虾米"}
        "page": 1
    }
    resp = requests.post(web_url, data=data, headers=header)
    data_dict = json.loads(resp.content.decode('utf-8'))
    # print(data_dict)
    if data_dict["code"] != 200:
        print("服务器出现问题或域名已更改")
        return
    if not artist:
        return data_dict["data"][0]["url"]
    for i in data_dict["data"]:
        if i["author"] == artist and i["title"] == name:
            return i["url"]
    print("歌曲不存在")


def download_music(url):
    resp = requests.get(url)
    full_name = url.split('/')[-1]
    # eyed3不支持读取含有中文的文件
    with open(full_name, 'wb') as f:
        f.write(resp.content)
    # logging.info("下载成功")
    print("下载成功")
    return full_name


def rewrite_msg(music_path, artist, title):
    # 网易云音乐下载的歌曲信息乱码
    music_obj = eyed3.load(music_path)
    music_obj.tag.artist = artist
    music_obj.tag.title = title
    music_obj.tag.save()
    if artist:
        os.rename(music_path, f"{title}-{artist}.mp3")
    else:
        os.rename(music_path, f"{title}.mp3")


def main(name, artist=''):
    url = search_music(name, artist)
    if url:
        music_path = download_music(url)
        rewrite_msg(music_path, artist, name)


def start(song):
    # 高并发，封ip
    if isinstance(song[0], tuple):
        for i, j in song:
            t = threading.Thread(target=main, args=(i, j))
            t.start()
    else:
        for i in song:
            t = threading.Thread(target=main, args=(i,))
            t.start()


if __name__ == '__main__':
    # 指定歌手
    music = [("春夏秋冬", "张国荣")]
    # 非指定歌手
    # music = ["让我照顾你"]
    start(music)
