# !/usr/bin/python
# -*- coding: UTF-8 -*-
import pandas as pd
import csv
import glob
import os
import shutil
from logger import Logger



log = Logger('./log/data_csv.log', level='info')



def delete():                                                                                                           #清洗数据
    try:                                                                                                                #如果'./output/edition 1/'有文件的话，就复制到"csv_compare"下
        """
        跟随output文件夹下项目名称的      
        
        报错了注意看看   ！！！Path！！！  这里是不是路径[edition 1]不对
        """
        Path = './output/edition 1/'
        dir_src_1 = os.listdir(Path)
        dir_dst_1 = "csv_compare"
        for file in dir_src_1:

            if file == 'images':
                pass
            else:
                shutil.copy(Path + file, dir_dst_1)

        log.logger.info('测试数据：./output/edition 1/文件复制到csv_compare下')

    except:
        pass




    path = 'csv_compare/*.csv'                                                                                          #去除第一行index，重写写入到"csv_compare"
    files = glob.glob(path)
    x = 0
    for filename in files:
        with open(filename, 'rb') as fin:
            data = fin.read().splitlines(True)
            with open(filename, 'wb') as fout:
                fout.writelines(data[1:])
                x += 1

    dir_src = "csv_compare"
    dir_dst = "csv_compare_transfer"

    for file in os.listdir(dir_src):
        if x > 0:
            src_file = os.path.join(dir_src, file)
            dst_file = os.path.join(dir_dst, file)
            shutil.move(src_file, dst_file)
            shutil.move(dst_file, src_file)

    Path = './csv_compare/'                                                                                             #去除第一列,重新写入文件
    file = os.listdir(Path)
    try:
        os.remove(Path + '/all.csv')
    except:
        pass

    for i in file:
        df = pd.read_csv(Path + i,index_col=0)
        df.to_csv(Path + i, encoding="GBK", index=False, mode='w')
        df.to_csv(Path + '/all.csv', encoding="GBK", index=False, mode='a')                                             #把所有的文件汇总到all.csv下

    log.logger.info('测试数据处理完成重新写入文件，all.csv合成完毕')

delete()


Path = './csv_compare/'
file = os.listdir(Path)
def compa():                                                                                                            #比较数据
    for i in file:
        count = 0
        with open("csv_compare/all.csv", "r", encoding="GBK") as f:
            red = csv.reader(f)

            for r in red:
                flag = 0

                if i != 'all.csv':
                    with open(Path+i, "r", encoding="GBK") as n:
                        dat = csv.reader(n)

                        for d in dat:

                            if r == d:
                                count = count + 1
                                flag = 1
                                break

                        if flag == 0:
                            pass

        number_1 = 0
        if i != 'all.csv':
            print("文件:" + i + "相同的数据总共有：" + str(count))
            log.logger.info(str("文件:" + i + "相同的数据总共有：" + str(count)))

            with open(Path + i, "r", encoding="GBK") as Number:
                dat = csv.reader(Number)

                for d in dat:
                    number_1 = number_1 + 1
                print("原始文件：" + i + "总条数：" + str(number_1))
                log.logger.info(str("原始文件：" + i + "总条数：" + str(number_1)))

        else:
            with open(Path + i, "r", encoding="GBK") as Number:
                dat = csv.reader(Number)

                for d in dat:
                    number_1 = number_1 + 1
                print("原始文件：" + i + "总条数：" + str(number_1))
                log.logger.info(str("原始文件：" + i + "总条数：" + str(number_1)))

        if count > number_1:
            print(i + '文件,数据异常-------------------------------------------------------------------------------------')
            log.logger.info(str(i + '文件,数据异常-------------------------------------------------------------------------------------'))

compa()

