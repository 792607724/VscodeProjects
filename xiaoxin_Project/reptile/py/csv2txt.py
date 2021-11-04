# coding = utf8
import pandas as pd
import os

'''
    将csv文件转换成txt文件
'''

# Excel的csv文件需要在此处再转成txt格式，才可用于词云图
class csv2txt():
    data = pd.read_csv("/Users/cgt/VscodeProjects/xiaoxin_Project/reptile/output/cgt.csv")
    with open("/Users/cgt/VscodeProjects/xiaoxin_Project/reptile/output/new.txt", "w", encoding='utf-8') as f:
        for line in data.values:
            f.write((str(line[0]) + "\t" + str(line[1]) + "\t" + str(line[2]) + "\n"))
            

