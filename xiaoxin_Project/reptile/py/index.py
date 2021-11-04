# coding = utf8
import requests
from lxml import etree

'''
    Crate by xxx
    Date：
    Summary：Catch some information from below url and sort it.
    Url：https://cjy.ctbu.edu.cn/
    Step：
        1、明确目的
        2、找到数据对应网页
        3、分析网页结构找到数据所在的标签位置
        4、模拟HTTP请求，向服务器发送这个请求，获取到服务器返回给我们的HTML
        5、用正则表达式提取我们需要的数据（主页动态、通知公告）
'''

class index():
    print("爬虫抓取")
    
    def __init__(self):
        # 采用固定地址+不同页码的方法来爬去分页的所有动态
        # 学院动态
        # https://cjy.ctbu.edu.cn/index/xydt.htm    -- 学院动态首页xydt.htm   (htm)
        # https://cjy.ctbu.edu.cn/index/xydt/19.htm -- 学院动态分页xydt/x.htm  (19~1)
        self.dynamic_Url = "https://cjy.ctbu.edu.cn/index/xydt.htm"
        # dynamic_Url_NextPage = "https://cjy.ctbu.edu.cn/index/xydt/19.htm"  #(从19 ~ 1)

        # 重要通知
        # https://cjy.ctbu.edu.cn/index/zytz.htm -- 重要通知首页zytz.htm   (htm)
        # https://cjy.ctbu.edu.cn/index/zytz/4.htm -- 重要通知分页zytz/x.htm   (3~1)
        self.important_Url = "https://cjy.ctbu.edu.cn/index/zytz.htm"
        # important_Url_NextPage = "https://cjy.ctbu.edu.cn/index/zytz/3.htm"  #(从3 ~ 1)

    '''
        获取Html内容，并进行爬取
    '''
    def fectch_Content(self, url):
        html = requests.get(url)
        html.encoding = "utf-8"
        html = html.text
        list = etree.HTML(html)
        # 获取每一个动态的正则表达式
        regular_Expression = '//ul[@class="global_tx_list4"]/div/li'
        url_List = list.xpath(regular_Expression)

        all_item_list = []

        for selector in url_List:
            href = selector.xpath('a/@href')[1]
            title = selector.xpath('a/@title')[0]
            time = selector.xpath('span[@class="box_r"]/text()')[0]
            all_list = [href, title, time]
            all_item_list.append(all_list)
        
        return all_item_list

    # 整理 “学院动态” 数据
    def university_Dynamic(self):
        all_page_List = []
        # First special page
        first_Page_List = self.fectch_Content(self.dynamic_Url)
        # Other page
        next_Page_List = []
        for i in range(19):
            next_Page = "https://cjy.ctbu.edu.cn/index/xydt/%s.htm" % (i + 1)
            temp_List = self.fectch_Content(next_Page)
            next_Page_List.append(temp_List)

            if i == 19:
                next_Page_List.append(first_Page_List)

        all_page_List = next_Page_List
        return all_page_List


    # 整理 ”重要通知“ 数据
    def important_Notification(self):
        all_page_List = []
        # First special page
        first_Page_List = self.fectch_Content(self.important_Url)
        # Other page
        next_Page_List = []
        for i in range(3):
            next_Page = "https://cjy.ctbu.edu.cn/index/zytz/%s.htm" % (i + 1)
            temp_List = self.fectch_Content(next_Page)
            next_Page_List.append(temp_List)

            if i == 3:
                next_Page_List.append(first_Page_List)

        all_page_List = next_Page_List
        return all_page_List

    def data(self):
        university_Dynamic_List = self.university_Dynamic()
        import_Notification_List = self.important_Notification()
        data = [university_Dynamic_List, "这里是分界线", import_Notification_List]
        return data



