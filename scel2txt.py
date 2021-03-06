#!/usr/bin/python
# -*- coding: utf-8 -*-


import struct
import sys
import os
import logging

# 搜狗的scel词库就是保存的文本的unicode编码，每两个字节一个字符（中文汉字或者英文字母）
# 找出其每部分的偏移位置即可
# 主要两部分
# 1.全局拼音表，貌似是所有的拼音组合，字典序
#       格式为(index,len,pinyin)的列表
#       index: 两个字节的整数 代表这个拼音的索引
#       len: 两个字节的整数 拼音的字节长度
#       pinyin: 当前的拼音，每个字符两个字节，总长len
#
# 2.汉语词组表
#       格式为(same,py_table_len,py_table,{word_len,word,ext_len,ext})的一个列表
#       same: 两个字节 整数 同音词数量
#       py_table_len:  两个字节 整数
#       py_table: 整数列表，每个整数两个字节,每个整数代表一个拼音的索引
#
#       word_len:两个字节 整数 代表中文词组字节数长度
#       word: 中文词组,每个中文汉字两个字节，总长度word_len
#       ext_len: 两个字节 整数 代表扩展信息的长度，好像都是10
#       ext: 扩展信息 前两个字节是一个整数(不知道是不是词频) 后八个字节全是0
#
#      {word_len,word,ext_len,ext} 一共重复same次 同音词 相同拼音表

logging.basicConfig(filename='scel_error.log', level=logging.DEBUG)

# 拼音表偏移，
startPy = 0x1540

# 汉语词组表偏移
startChinese = 0x2628

# 全局拼音表

GPy_Table = {}

# 解析结果
# 元组(词频,拼音,中文词组)的列表
GTable = []


def byte2str(data):
    '''将原始字节码转为字符串'''

    i = 0
    length = len(data)
    ret = u''
    while i < length:
        x = data[i] + data[i + 1]
        t = unichr(struct.unpack('H', x)[0])
        i += 2
        if t == u'\r':
            ret += u'\n'
        elif t == u'\x00':
            continue
        else:
            ret += t

    return ret


# 获取拼音表
def getPyTable(data):

    if data[0:4] != "\x9d\x01\x00\x00":
        return None
    data_content = data[4:]
    pos = 0
    length = len(data_content)

    while pos < length:
        index = struct.unpack('H', data_content[pos:pos + 2])[0]
        pos += 2
        py_lenght = struct.unpack('H', data_content[pos:pos + 2])[0]
        pos += 2
        py = byte2str(data_content[pos:pos + py_lenght])
        GPy_Table[index] = py
        pos += py_lenght


# 获取一个词组的拼音
def getWordPy(data):
    pos = 0
    length = len(data)
    ret = u''

    while pos < length:

        index = struct.unpack('H', data[pos:pos + 2])[0]
        ret += GPy_Table[index]
        pos += 2

    return ret


# 获取一个词组
def getWord(data):
    pos = 0
    length = len(data)
    ret = u''
    while pos < length:

        index = struct.unpack('H', data[pos] + data[pos + 1])[0]
        ret += GPy_Table[index]
        pos += 2
    return ret


# 读取中文表
def getChinese(data):

    pos = 0
    length = len(data)

    while pos < length:
        # 同音词数量
        same = struct.unpack('H', data[pos:pos + 2])[0]

        # 拼音索引表长度
        pos += 2
        py_table_len = struct.unpack('H', data[pos:pos + 2])[0]

        if py_table_len % 2 != 0:
            return

        # 拼音索引表
        pos += 2
        try:
            py = getWordPy(data[pos:pos + py_table_len])
        except Exception as e:
            print e

        # 中文词组
        pos += py_table_len
        for i in xrange(same):
            # 中文词组长度
            c_len = struct.unpack('H', data[pos] + data[pos + 1])[0]
            pos += 2

            # 中文词组
            word = byte2str(data[pos:pos + c_len])
            pos += c_len

            # 扩展数据长度
            ext_len = struct.unpack('H', data[pos] + data[pos + 1])[0]
            pos += 2

            # 词频
            count = struct.unpack('H', data[pos] + data[pos + 1])[0]

            # 保存
            GTable.append((count, py, word))

            # 到下个词的偏移位置
            pos += ext_len


def deal(file_name):
    f = open(file_name, 'rb')
    data = f.read()
    f.close()
    status = True
    # print 'Total bytes: ', len(data)

    if data[0:12] != "\x40\x15\x00\x00\x44\x43\x53\x01\x01\x00\x00\x00":
        print '确认你选择的是搜狗(.scel)词库?'
        return file_name, False

    # print '词库名：', byte2str(data[0x130:0x338]).encode('utf-8')
    # print '词库类型：', byte2str(data[0x338:0x540]).encode('utf-8')
    # print '描述信息：', byte2str(data[0x540:0xd40]).encode('utf-8')
    # print '词库示例：', byte2str(data[0xd40:startPy]).encode('utf-8')

    try:
        getPyTable(data[startPy:startChinese])
        getChinese(data[startChinese:])
    except Exception as e:
        print e
        status = False
        return byte2str(data[0x130:0x338]).encode('utf-8'), status

    return byte2str(data[0x130:0x338]).encode('utf-8'), status


if __name__ == '__main__':

    # o = ['网络流行新词.scel']

    # for f in o:
    #     deal(f)

    for root, dirs, files in os.walk('sogou/result'):
        for file_name in files:
            GTable = []
            input_file = '%s/%s' % (root, file_name)
            dict_name, status = deal(input_file)
            dict_name = dict_name.replace('/', '_').replace('\\', '_')

            if status is False:
                logging.error(input_file)

            f = open('dicts/' + dict_name + '.txt', 'w')

            for count, py, word in GTable:
                f.write(unicode(word).encode('UTF-8'))
                f.write('\n')

            f.close()

    # 保存结果
    # f = open('sougou.txt', 'w')
    # for count, py, word in GTable:
    #     # GTable保存着结果，是一个列表，每个元素是一个元组(词频,拼音,中文词组)，有需要的话可以保存成自己需要个格式
    #     # 我没排序，所以结果是按照上面输入文件的顺序
    #     # 最终保存文件的编码，可以自给改
    #     f.write(unicode('{%(count)s}' % {'count': count} + py + ' ' + word).encode('UTF-8') )
    #     f.write('\n')
    # f.close()
