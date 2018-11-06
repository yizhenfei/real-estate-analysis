#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# 功能: 将已经通过工具转换好的小区信息json文件导入到指定的mysql数据库中
#

import argparse
import json
import mysql.connector

def import_line(line, my):
    cursor = my.cursor()

    # 加载json
    record = json.loads(line)

    # 处理None字段
    record["year_built"] = record.get("year_built", None)
    
    # 查询该小区是否已经存在
    cursor.execute(u'SELECT id FROM community WHERE `name` = %s', (record["name"],))
    cursor.fetchall()

    # 如果已存在, 返回
    if cursor.rowcount != 0:
        print(u"小区(%s)已存在于数据库中(%d), 跳过" % (record["name"], cursor.rowcount))
        return

    # 插入新小区
    cursor.execute(u'INSERT INTO community (`name`, address, year_built, building_num, home_num) '
                   u'VALUES (%(name)s, %(address)s, %(year_built)s, %(building_num)s, %(home_num)s)',
                   record)

    # 关闭并提交
    cursor.close()
    my.commit()

def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='Import community data to mysql.')
    parser.add_argument('--input', help='input file in JSON format', required=True)
    parser.add_argument('--host', help='mysql host', default="localhost")
    parser.add_argument('--port', help='mysql port', default=3306, type=int)
    parser.add_argument('--user', help='mysql user', default="root")
    parser.add_argument('--password', help='mysql password', default="")
    parser.add_argument('--database', help='mysql database', default="real_estate_analysis")

    # 解析命令行参数
    args = parser.parse_args()

    # 连接至mysql
    my = mysql.connector.connect(user=args.user, password=args.password,
                                 host=args.host, port=args.port,
                                 database=args.database)

    # 打开输入文件
    input = open(args.input)

    # 逐条处理记录
    for line in input:
        import_line(line, my)

    # 结束
    return

if __name__ == "__main__":
    main()
