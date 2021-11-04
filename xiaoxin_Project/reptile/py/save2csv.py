# coding = utf8
import csv
import index

class save2csv():

    # 获得列表数据 -- OK （这里的数据是从index里获取的，从网上爬取的数据并转入Excel）
    index1 = index.index()
    data = index1.data()

    # 写入数据至excel表格
    with open(r"/Users/cgt/VscodeProjects/xiaoxin_Project/reptile/output/cgt.csv", "w", encoding='utf-8-sig') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["链接", "标题", "日期"])
        for i in data:
            for j in i:
                for list_csv in j:
                    print(list_csv)
                    csv_writer.writerow(list_csv)

        
