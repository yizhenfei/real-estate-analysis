#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# 这是一个在pyspider框架中使用的脚本
# 用于抓取链家(上海)网站中的小区信息
# TODO(yizhenfei): 在索引页面中, 包含小区的板块信息, 这个数据应该进行提取

from pyspider.libs.base_handler import *
import re

class Handler(BaseHandler):
    crawl_config = {
    }
    
    # 重试策略, 为了避免偶尔的网站不可用导致抓取索引页失败, 导致阻碍整体的抓取进度
    # 前3次的重试间隔设置的较短
    retry_delay = {
        0: 5,
        1: 30,
        2: 60,
        3: 5*60,
        4: 30*60,
        5: 60*60,
        6: 12*60*60,
        '': 24*60*60
    }

    # 小区信息更新比较慢, 每小时触发一次抓取, 将来可以按照实际情况, 进一步降低该频率
    @every(minutes=60)
    def on_start(self):
        self.crawl('https://sh.lianjia.com/xiaoqu/', fetch_type='js', callback=self.index_page)
        
    def is_index_page(self, url):
        return re.match(".*/xiaoqu/[a-zA-Z]+/(pg[0-9]+/)?$", url) != None
    
    def is_detail_page(self, url):
        return re.match(".*/xiaoqu/[0-9]+/$", url) != None

    # 索引页面的age设置为与on_start触发频率相同
    @config(age=60*60)
    # 索引页面的抓取优先级低于详细页面, 先把所有已知的详情页面抓取完毕, 然后再抓取新的索引页面, 避免等待的task数量过多
    @config(priority=2)
    def index_page(self, response):
        # 找出页面中所有包含/xiaoqu/的页面
        for each in response.doc(u'a[href*="/xiaoqu/"]').items():
            url = each.attr.href
            # 根据是索引页面还是详情页面, 进一步抓取
            if self.is_index_page(url):
                self.crawl(url, fetch_type='js', callback=self.index_page)
            elif self.is_detail_page(url):
                self.crawl(url, fetch_type='js', callback=self.detail_page)

    @config(priority=1)
    def detail_page(self, response):
        id = re.match(".*/xiaoqu/([0-9]+)/$", response.url).group(1)
        name = response.doc('h1[class="detailTitle"]').text()
        address = response.doc('div[class="detailDesc"]').text()
        year_built = response.doc(u'span:contains("建筑年代")').siblings('span:first').text()
        building_num = response.doc(u'span:contains("楼栋总数")').siblings('span:first').text()
        home_num = response.doc(u'span:contains("房屋总数")').siblings('span:first').text()
        
        return {
            "type": "lianjia-sh-community", # 数据类型
            "version": 1, # 数据格式版本号
            "url": response.url,
            "id": id,
            "name": name,
            "address": address,
            "year_built": year_built,
            "building_num": building_num,
            "home_num": home_num,
        }
