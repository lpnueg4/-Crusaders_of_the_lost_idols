# coding:u8

from pprint import pprint
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
import re
import glob
import os

import shutil

import zipfile

DES_FILE = 'D:\PY\plot\data.zip'

def get_data():
    '''
        从html里面读取数据
    '''
    fn = "%s/%s" % (DES_FILE + "_files", "index.html")

    with open(fn, "rb") as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser', from_encoding='utf-8')

    ll = []
    for child in soup.tbody.children:
        if child == "\n":
            continue

        title = []
        for c in child.children:
            if c == "\n":
                continue
            for s in c.strings:
                s = s.encode('u8')
                title.append(s)

        if len(title) > 0:
            ll.append(title)

    return ll


def format_data():
    '''
        处理数据
    '''
    data = get_data()

    title = data.pop(0)

    dd = {}
    mark = {}
    mn = -1 # X 轴的位置
    for index1, i in enumerate(data):
        if len(i) < len(title):
            # key, 特殊标记的位置 X坐标+0.5 位于2个条形之间
            # i, 是一行的值, 数组, 只包含存在的值
            mark['%s' % (mn+0.5)] = i
            continue
        else:
            mn = mn + 1

        for index2, ii in enumerate(i):
            dd.setdefault(title[index2], [])

            if title[index2] == 'all':
                dd[title[index2]].append(int(ii))
            else:
                dd[title[index2]].append(ii)

    # pprint(dd)
    # pprint(mark)
    # exit()

    return (dd, mark)


def get_top_num_and_index(input_list, num, flag='max', space=0):
    '''
        获取数组 最大or最小 的前N个
    '''
    time = {}
    for index,i in enumerate(input_list):
        time[index] = float(i)*1000

    if flag == 'max':
        f = True
    elif flag == 'min':
        f = False

    sort_list = sorted(time.items(), key=lambda item: item[1], reverse=f)
    ret_list = sort_list[:num]

    # pprint(ret_list)

    return ret_list


def save(plt):
    '''
        保存图片
    '''

    #---- rename
    # file_list = glob.glob('./crusader/*.png')
    # for i in file_list:
    #     # print i
    #     path = os.path.dirname(i)
    #     name = os.path.basename(i)

    #     g = re.search(r'\((\d+)\)', i)
    #     if g:
    #         num = g.group(1)
    #         os.renames(i, path + os.sep + "%s.png" % num)

    prefix = 'big'

    #---- save to png
    file_list = glob.glob('./crusader/%s_*.png' % prefix)
    num_list = []
    path = None
    for i in file_list:
        if not path:
            path = os.path.dirname(i)
        num = re.search(r'%s_(\d+)' % prefix, i).group(1)
        num_list.append(int(num))

    new_num = max(num_list) + 1
    plt.savefig(path + os.sep + "%s_%s.png" % (prefix, new_num))


def plot():

    # 数据, 特殊标记(有空列的行)
    data, make = format_data()

    # plt.figure(figsize=(28,14), dpi=80)
    plt.figure(figsize=(28,11), dpi=80)
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['font.serif'] = ['consola']

    #---------------------------------------------------------
    # idols 总数

    l_idol, = plt.plot(data['all'], marker='o', label="idol")
    # l_idol, = plt.plot(data['all'], marker=None, label="idol")

    # top 5
    top_idols = get_top_num_and_index(data['all'], 5)

    space_flag = 0

    for i in top_idols:

        # 防止2个大值靠的太近. 重叠
        if i[0]>space_flag+3 or i[0]<space_flag-3:
            # print data['all'][i[0]]
            plt.text(i[0],
                data['all'][i[0]]+1500,
                '%.0f' % float(data['all'][i[0]]),
                ha='center',
                va='bottom')
            # i[0] 是 x轴
            space_flag = i[0]

    #---------------------------------------------------------
    # boss奖励idols
    boss = []
    boss_not_zero = []
    for index,i in enumerate(data['idol_boss']):
        if re.search(r'^\d+$', i):
            boss.append(int(i))
            if int(i) == 0:
                # 为了从 boss_not_zero 中取最小的, 且不是0的. 把0变成9999999.
                boss_not_zero.append(9999999)
            else:
                boss_not_zero.append(int(i))
        else:
            boss.append(0)

        # 没有写满的行, 都会加入make, 取的第一个存在的列, 并不是第一列
        if re.search(r'ms', i):
            # 是以level列的值, 做的标记
            # 把 level 行替换成ms, 标识任务flag
            data['level'][index] = 'ms'

    # for index,i in enumerate(boss):
    #     if i>20000:
    #         plt.bar(index, i, facecolor='#A108CD')
    #     else:
    #         plt.bar(index, i, facecolor='#1F77B4')

    color = [
        [0,      20000, '#A108CD'],
        [20001,  30000, '#1F77B4'],
        [30001,  60000, '#FFC90E'],
        # [40001,  60000, '#FFC90E'],
        [60001,  80000, '#ED1C24'],
    ]

    for index,i in enumerate(boss):
        for c in color:
            if c[0] <= i <= c[1]:
                plt.bar(index, i, facecolor=c[2])

    color_legend_boss = []
    for c in color:
        tmp, = plt.plot([], linewidth=8, color=c[2], label="%s-%s" % (c[0], c[1]), alpha=1)
        color_legend_boss.append(tmp)

    max_boss = boss.index(max(boss))
    min_boss = boss_not_zero.index(min(boss_not_zero))

    plt.text(max_boss,
        boss[max_boss]+3500,
        '%s' % (boss[max_boss]),
        ha='center', va='top', fontsize=8)
    plt.text(min_boss,
        boss_not_zero[min_boss]+3500,
        '%s' % (boss_not_zero[min_boss]),
        ha='center', va='top', fontsize=8)

    #---------------------------------------------------------
    # map
    map_data = []

    # 数据太小, 扩大比例
    plus = -25

    for i in data['map']:
        map_data.append(int(i) * plus)

    max_map = map_data.index(min(map_data))
    min_map = map_data.index(max(map_data))

    show_data = []
    for i in map_data:
        show_data.append(int(i) - map_data[min_map] - 2000)

    color = [
        [0,     1000, '#FFE899'],
        [1001,  1100, '#AA99FF'],
        [1101,  1200, '#FF9999'],
        [1201,  1300, '#7BA975'],
        # [1301,  1400, '#FFC90E'],
        [1301,  1400, '#99D9EA'],
    ]

    for index,i in enumerate(map_data):
        for c in color:
            if c[0] <= (i/plus) <= c[1]:
                tmp = plt.bar(index, show_data[index], facecolor=c[2])

    # for legend, 绘制没有点的线, 为了让图例中显示出bar的颜色
    color_legend = []
    for c in color:
        tmp, = plt.plot([], linewidth=8, color=c[2], label="%s-%s" % (c[0], c[1]), alpha=1)
        color_legend.append(tmp)

    plt.text(max_map,
        show_data[max_map]-1000,
        '%s' % (map_data[max_map] / plus),
        ha='center', va='top', fontsize=8)
    plt.text(min_map,
        show_data[min_map]-1000,
        '%s' % (map_data[min_map] / plus),
        ha='center',va='top', fontsize=8)

    #---------------------------------------------------------
    # X轴 make

    # 根据数据数量控制x轴位置
    # this_x = -(len(data['all'])-101)/2
    this_x = -(len(data['all'])*0.05+3)

    plt.axhline(60000, ls="--", c="r", alpha=0.2)
    #          x     y
    plt.text(this_x, 60000, '60000',  color='r', fontsize=10, ha='center', va='center', alpha=0.7)

    plt.axhline(40000, ls="--", c="g", alpha=0.2)
    plt.text(this_x, 40000, '40000',  color='g', fontsize=10, ha='center', va='center', alpha=0.7)

    plt.axhline(100000, ls="--", c="g", alpha=0.2)
    # plt.text(this_x, 100000, '100000',  color='b', fontsize=10, ha='center', va='center', alpha=0.7)

    # 24h line
    plt.axhline(170000, ls="--", c="y", alpha=0.3)
    plt.text(this_x, 170000, 'time 0',  color='y', fontsize=10, ha='center', va='center', alpha=0.7)

    # 20000 line
    # plt.axhline(20000, ls="--", c="b", alpha=0.1)

    # 0 line
    plt.axhline(0, ls="-", c="k", linewidth=0.5)

    #---------------------------------------------------------
    # Y轴 make, buff name
    bl = 270000
    for k,v in make.iteritems():
        if len(v) > 1:
            s = v[0] + "\n" + v[1] # 使用的是第一个值, 第二个值
        else:
            s = v[0] # 使用第一个非空值

        if re.search(r'\*2', s):
            plt.axvline(float(k), ls="-", c="r", marker='o', markersize = 25, alpha=0.5)
            plt.text(float(k), bl+1000, s, fontsize=10, color='r', ha='center', va='bottom', alpha=0.5)
        else:
            plt.axvline(float(k), ls="--", c="gray", alpha=0.4)
            plt.text(float(k), bl+1000, s, fontsize=10, color='gray', ha='center', va='bottom', alpha=0.5)

    #---------------------------------------------------------
    # idols 最大值, 最小值
    # max_indx = data['all'].index(max(data['all']))
    # plt.plot(max_indx, data['all'][max_indx],'ro')

    #---------------------------------------------------------
    # event, challenge
    for index, i in enumerate(data['level']):
        if re.search('cg', i):
            plt.plot(index, data['all'][index],'o', c="#FE7314")
        if re.search('et', i):
            plt.plot(index, data['all'][index],'o', c="#0FC20F")
        if re.search('ms', i):
            plt.plot(index, data['all'][index],'s', c="r")

    #---------------------------------------------------------
    # not 25%
    for index, i in enumerate(data['idol_buff']):
        if int(i[:-1]) == 0:
            plt.plot(index, data['all'][index],'rx', markersize=8)

    #---------------------------------------------------------
    # time
    time = []
    baseline = 170000
    for i in data['time(h)']:
        time.append(baseline+float(i)*1000)
    l_time, = plt.plot(time, marker='o', label="time")

    # time text
    # for index,i in enumerate(data['time(h)']):
        # plt.text(index+0.4, baseline+float(i)*1000+1000, '%.2f' % float(i), ha='center', va='bottom')
        # plt.text(index+0.4, baseline+float(i)*1000+1000, '%.2f' % float(i))

    max_time = time.index(max(time))
    min_time = time.index(min(time))

    top_time = get_top_num_and_index(time, 5)
    below_time = get_top_num_and_index(time, 1, flag='min')

    for i in top_time:
        plt.text(i[0],
            time[i[0]]+1500,
            '%.2f' % float(data['time(h)'][i[0]]),
            ha='center',
            va='bottom')

    for i in below_time:
        plt.text(i[0],
            time[i[0]]-3000,
            '%.2f' % float(data['time(h)'][i[0]]),
            ha='center',
            va='top')

    # plt.text(min_time,
    #     time[min_time]-2000,
    #     '%.2f' % float(data['time(h)'][min_time]),
    #     ha='center',
    #     va='top')

    # print data['time(h)']
    # print max(data['time(h)'])

    #---------------------------------------------------------
    # text

    #---------------------------------------------------------
    # legend

    # myfont = matplotlib.font_manager.FontProperties(fname='C:/Windows/Fonts/consola.ttf', size=11)

    # boss奖励, 图例
    second_legend = plt.legend(handles=color_legend_boss, loc=3, shadow=True,
        bbox_to_anchor=(0, -0.08),
        handletextpad=1,    # text padding
        handlelength=4,     # line length
        borderpad=0.8,      # border padding
        ncol=5,
        # title='map',
        )
    plt.gca().add_artist(second_legend)

    # 图例, 两个主线
    first_legend = plt.legend(handles=[l_time, l_idol], loc=2,
        bbox_to_anchor=(0, 0.99),
        shadow=True,
        handlelength=5,
        # prop=myfont,
        )

    # 多图例写法
    plt.gca().add_artist(first_legend)

    # plt.legend(handles=color_legend, bbox_to_anchor=(1, 1))
    # plt.legend(handles=color_legend, loc=2, fontsize='small')

    # 地图, 图例
    # bbox_to_anchor(x[百分比位置], y[百分比位置]),
    # x 大于 1 时候, 将出现在x轴右侧
    # y 小于 1 时候, 将出现在y轴下侧
    plt.legend(handles=color_legend, loc=3, shadow=True,
        bbox_to_anchor=(0, -0.135),
        handletextpad=1,    # text padding
        handlelength=4,     # line length
        borderpad=0.8,      # border padding
        ncol=5,
        # title='map',
        )

    #---------------------------------------------------------

    top = baseline + 100000

    # y轴下限, 想把图例放在图标内部, 需要提高下限
    plt.ylim(-40000, top)

    # plt.show()  #显示画布

    save(plt)

    print "plot over."

    #TODO, 拆分成小方法


def copy():
    src = 'D:\Documents\My Knowledge\Data\lpnueg@163.com\Game\Crusaders of the Lost Idols\idols 计算.ziw'.decode('u8')
    DES_FILE = 'D:\PY\plot\data.zip'
    try:
        shutil.copy(src, DES_FILE)
    except Exception, e:
        print e
    print "copy over."

def unzip():
    zip_file = zipfile.ZipFile(DES_FILE)

    if os.path.isdir(DES_FILE + "_files"):
        pass
    else:
        os.mkdir(DES_FILE + "_files")

    for names in zip_file.namelist():
        zip_file.extract(names, DES_FILE + "_files")

    zip_file.close()
    print "unzip over."

if __name__ == "__main__":

    copy()
    unzip()
    plot()
