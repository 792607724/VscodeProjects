# coding = utf8

import re   # 正则表达式库
import collections  # 词频统计库
import numpy as np  # numpy数据处理库
import jieba    # 结巴分词
import wordcloud    # 词云展示库
from PIL import Image   # 图像处理库
import matplotlib.pyplot as plt # 图像展示库

'''
    创建词云图
'''

class csv2Wordcloud():

    with open("/Users/cgt/VscodeProjects/xiaoxin_Project/reptile/output/new.txt", "r", encoding='utf-8-sig') as file2Cloud:
        string_Data = file2Cloud.read()
        seg_List_exact = jieba.cut(string_Data, cut_all= False)
        mask = np.array(Image.open("/Users/cgt/VscodeProjects/xiaoxin_Project/reptile/py/hanxin.jpg"))
        wc = wordcloud.WordCloud(
            background_color='white', # 设置背景颜色
            font_path='/System/Library/Fonts/Hiragino Sans GB.ttc', # 设置字体格式
            mask=mask, # 设置背景图
            max_words=500, # 最多显示词数
            max_font_size=120 , # 字体最大值
            scale=48  # 调整图片清晰度，值越大越清楚
        )

    # 文本预处理
    pattern = re.compile(u'\t|\n|\.|-|:|;|\)|\(|\?|"') # 定义正则表达式匹配模式
    string_Data = re.sub(pattern, '', string_Data) # 将符合模式的字符去除

    # 文本分词
    seg_list_exact = jieba.cut(string_Data, cut_all = False) # 精确模式分词
    object_list = []
    remove_words = [u'的', u'，',u'和', u'是', u'随着', u'对于',u'对',u'等',u'能',u'都',u'。',
    u' ',u'、',u'中',u'在',u'了',u'通常',u'如果',u'我们',u'需要', u'教育'] # 自定义去除词库

    for word in seg_list_exact: # 循环读出每个分词
        if word not in remove_words: # 如果不在去除词库中
            object_list.append(word) # 分词追加到列表

    # 词频统计
    word_counts = collections.Counter(object_list) # 对分词做词频统计
    word_counts_top10 = word_counts.most_common(10) # 获取前10最高频的词
    print (word_counts_top10) # 输出检查

    # 词频展示
    mask = np.array(Image.open('/Users/cgt/VscodeProjects/xiaoxin_Project/reptile/py/hanxin.jpg')) # 定义词频背景
    wc = wordcloud.WordCloud(
        background_color='white', # 设置背景颜色
        font_path='/System/Library/Fonts/Hiragino Sans GB.ttc', # 设置字体格式
        mask=mask, # 设置背景图
        max_words=500, # 最多显示词数
        max_font_size=120 , # 字体最大值
        scale=48  # 调整图片清晰度，值越大越清楚
    )

    wc.generate_from_frequencies(word_counts) # 从字典生成词云
    image_colors = wordcloud.ImageColorGenerator(mask) # 从背景图建立颜色方案
    wc.recolor(color_func=image_colors) # 将词云颜色设置为背景图方案
    wc.to_file("/Users/cgt/VscodeProjects/xiaoxin_Project/reptile/py/temp.jpg") # 将图片输出为文件
    plt.imshow(wc) # 显示词云
    plt.axis('off') # 关闭坐标轴qq
    plt.show() # 显示图像
