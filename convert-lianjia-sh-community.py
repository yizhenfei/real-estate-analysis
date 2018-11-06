#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# 功能: 将crawl-lianjia-sh-community.py脚本抓取到的原始数据转换为更容易处理的格式,
# 包括但不限于: 去除多余的字符, 单位转换, 数据计算等
# 在转换的过程中, 会对源数据进行检查, 不符合要求的源数据会进行报错处理
#

import argparse
import json
import re
import sys

def convert(line):
    # 准备结果对象
    result = {}
    # 加载json对象
    raw_record = json.loads(line)
    raw_data = raw_record["result"]
    
    # 处理数据
    result["name"] = raw_data["name"]
    result["address"] = raw_data["address"]

    # 处理建成年份
    if raw_data["year_built"] == u"暂无信息":
        # 如果没有建成年份, 则不在结果中存储该字段, 后续读取者作为None处理
        pass
    else:
        match = re.match(u"^([0-9]+)年建成$", raw_data["year_built"])
        if match == None:
            print("未知建成年份信息(%s), 小区ID(%s)" % (raw_data["year_built"], raw_data["id"]))
            return
        else:
            result["year_built"] = match.group(1)
    result["building_num"] = re.match(u"^([0-9]+)栋$", raw_data["building_num"]).group(1)
    result["home_num"] = re.match(u"^([0-9]+)户$", raw_data["home_num"]).group(1)

    # 转换为文本并返回
    return json.dumps(result, ensure_ascii=False)

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='Wash and convert raw data from lianjia-sh.')
    parser.add_argument('--input', help='input file in JSON format', required=True)
    parser.add_argument('--output', help='output file in JSON format', required=True)

    # 解析命令行参数
    args = parser.parse_args()

    # 打开文件
    input = open(args.input)
    output = open(args.output, 'w')

    # 逐条处理记录
    for line in input:
        output.write(convert(line).encode("utf-8"))
        output.write('\n')

    # 结束
    return
    
if __name__ == "__main__":
    main()
