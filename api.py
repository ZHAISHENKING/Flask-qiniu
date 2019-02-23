#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
"""
上传文件至七牛云，
主要功能：
- 上传接口
- 上传并返回link
- 通过link获取文件并展示
"""

import os, random, string
import qiniu
from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)


QINIU_AK = '七牛AK'
QINIU_SK = '七牛SK'
QINIU_BUCKET = '空间名'
QINIU_DOMAIN = '七牛地址'


@app.route('/', methods=['GET', 'POST'])
def index():
    return """
         <!doctype html>
            <html>
            <body>
            <form action='upload/' method='post' enctype='multipart/form-data'>
             <input type='file' name='videofile'>
             <input type='submit' value='Upload'>
            </form>
    """


@app.route('/upload/', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        up = UpFile()
        f = request.files["videofile"]
        filename = secure_filename(f.filename)
        # f.save(filename)
        mime = filename.rsplit(".")[1]
        with open(f, "rb") as file:
            qiniu_url = up.upload_img(file, mime)

        if qiniu_url:
            up.notify("qiniu-fileup", "图片上传成功")
        else:
            up.notify("qiniu-fileup", "图片上传失败")
        return qiniu_url


class UpFile(object):
    """
    上传
    """
    # 生成5位小写字母加数字的随机文件名
    @staticmethod
    def random_name():
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))

    # 上传至七牛云
    def upload_img(self, fn, sfx):
        key = self.random_name() + "." + sfx
        q = qiniu.Auth(QINIU_AK, QINIU_SK)
        token = q.upload_token(QINIU_BUCKET, key, 3600)
        ret, info = qiniu.put_data(token, key, fn)
        if (ret is not None) and ret['key'] == key and ret['hash'] == qiniu.etag(fn):
            return QINIU_DOMAIN + key
        else:
            self.notify("qiniu-fileup", "上传七牛云失败")
            return False

    @staticmethod
    # 调用系统通知
    def notify(title, text):
        os.system("osascript -e 'display notification \"{}\" with title \"{}\"'".format(text, title))


if __name__ == '__main__':
    app.run(debug=True)
