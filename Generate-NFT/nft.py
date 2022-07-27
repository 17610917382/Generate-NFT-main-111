# !/usr/bin/python
# -*- coding: UTF-8 -*-
from PIL import Image
import pandas as pd
import numpy as np
import time
import os
import random
import warnings
from logger import Logger
import sys
import check_asset
import yaml



global zfill_count
zfill_count = 0

global all_traits_rarities
all_traits_rarities = {}

# warnings.simplefilter(action='ignore', category=FutureWarning)
strimage_name = str(input('请输入图片系列(可为空)：'))

def set_config(filename):                                                                                        #次函数返回config.yaml所有数据
    with open(filename, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def parse_config():                                                                                              #权重校验   权重生成数据处理
    assets_path = 'assets'
    for layer in CONFIG:

        layer_path = os.path.join(assets_path, layer['directory'])                                               #获取素材路径

        traits = sorted([trait for trait in os.listdir(layer_path) if trait[0] != '.'])                          #获取所有素材组成一个列表

        check_asset.state(traits,log)                                                                     #检查合规#调用./check_asset.py       目的：检查素材是否都为PNG格式

        if not layer['required']:                                                                                #如果./config.yaml    required字段为空：自动替换None
            traits = [None] + traits

        if layer['rarity_weights'] == 'None':                                                                    #如果./config.yaml    rarity_weights字段为None：平均分配给每一个PNG权重
            rarities = [1 for x in traits]

        elif layer['rarity_weights'] == 'random':                                                                #如果./config.yaml    rarity_weights字段为random：随机分配给每一个PNG权重
            rarities = [random.random() for x in traits]

        elif type(layer['rarity_weights']) == list:                                                              #如果./config.yaml    rarity_weights字段为[1,2,3]：一张图只能设置一个权重
            assert len(traits) == len(layer['rarity_weights']), f"确保您(图片数:{len(traits)},权重数:{len(layer['rarity_weights'])},应将config.yaml其中设置相同)"
            if len(traits) != len(layer['rarity_weights']):
                Logger('./log/error.log', level='error').logger.error(f"确保您拥有当前数量的稀有权重(图片数:{len(traits)},权重数:{len(layer['rarity_weights'])},应将config.yaml其中设置相同)")
                sys.exit()#抛出异常退出程序
            rarities = layer['rarity_weights']

        else:                                                                                                    #如果./config.yaml    rarity_weights字段不属于上述五种,判定无效
            Logger('./log/error.log', level='error').logger.error("无效稀有权重")
            sys.exit()

        rarities = get_weighted_rarities(rarities)                                                          #生成权重并赋值#调用get_weighted_rarities函数平均计算出每个图片所占的权重@003

        layer['rarity_weights'] = rarities

        layer['cum_rarity_weights'] = np.cumsum(rarities)

        layer['traits'] = traits


        layer_rarities = []                                                                                 #就算出的权重循环写入layer_rarities=[]列表
        for x,y in zip(layer['traits'],layer['rarity_weights']):
            layer_rarities.append([x,y])

        all_traits_rarities[layer['directory']] = layer_rarities



def get_weighted_rarities(arr):                                                                             #函数代号003     ctrl+f搜索003可找到使用位置
    return np.array(arr)/ sum(arr)











def generate_single_image(filepaths, output_filename=None):                                                 #图片生成函数
    bg = Image.open(os.path.join('assets', filepaths[0]))                                                   #获取每张图片的信息

    for filepath in filepaths[1:]:                                                                          #获取图片路径和信息
        img = Image.open(os.path.join('assets', filepath)).convert("RGBA")
        bg.paste(img, (0, 0), img)


    if output_filename is not None:                                                                         #不为空的话保存
        bg.save(output_filename, fromat='png')

    else:                                                                                                   #为空的话保存在single_images中
        if not os.path.exists(os.path.join('output', 'single_images')):
            os.makedirs(os.path.join('output', 'single_images'))
        bg.save(os.path.join('output', 'single_images', str(int(time.time())) + '.png'))

def get_total_combinations():                                                                               #计算可合成总和
    total = 1
    for layer in CONFIG:
        total = total * len(layer['traits'])
    return total


def select_index(cum_rarities, rand):
    cum_rarities = [0] + list(cum_rarities)
    for i in range(len(cum_rarities) - 1):
        if rand >= cum_rarities[i] and rand <= cum_rarities[i+1]:
            return i
    return None


def generate_trait_set_from_config():                                                                        #生成config.yaml特征的列表
    trait_set = []
    trait_paths = []
    for layer in CONFIG:
        traits, cum_rarities = layer['traits'], layer['cum_rarity_weights']
        rand_num = random.random()
        idx = select_index(cum_rarities, rand_num)
        trait_set.append(traits[idx])

        if traits[idx] is not None:

            trait_path = os.path.join(layer['directory'], traits[idx])

            trait_paths.append(trait_path)
    return trait_set, trait_paths


def generate_images(edition, count, drop_dup=True):                                                        #校验图片重复
    rarity_table = {}

    for layer in CONFIG:                                                                                    #检查文件路径    output/edition XXX/images
        rarity_table[layer['name']] = []
    op_path = os.path.join('output', 'edition ' + str(edition), 'images')


    zfill_count = len(str(count - 1))
    if not os.path.exists(op_path):                                                                         #没有这个路径的话，创建这个路径
        os.makedirs(op_path)
    for n in range(count):

        image_name = strimage_name + str(n).zfill(zfill_count) + '.png'                                     #合成的图片名称

        trait_sets, trait_paths = generate_trait_set_from_config()                                          #生成特征列表

        generate_single_image(trait_paths, os.path.join(op_path, image_name))                               #根据特征生成图片

        for idx, trait in enumerate(trait_sets):
            if trait is not None:
                rarity_table[CONFIG[idx]['name']].append(trait[: -1 * len('.png')])
            else:
                rarity_table[CONFIG[idx]['name']].append('none')

    rarity_table = pd.DataFrame(rarity_table).drop_duplicates()                                             #去重重复行数

    log.logger.info("生成第 %i 张图片, %i张不同" % (count, rarity_table.shape[0]))                             #count    自己输入的图片生成数量，rarity_table:去重之后的行数   要写进csv中



    if drop_dup:
        img_tb_removed = sorted(list(set(range(count)) - set(rarity_table.index)))
        log.logger.info("移除 %i 张图片..." % (len(img_tb_removed)))
        for i in img_tb_removed:
            os.remove(os.path.join(op_path, strimage_name + str(i).zfill(zfill_count) + '.png'))                  #找出对应图片的名称删除图片

        # for idx, img in enumerate(sorted(os.listdir(op_path))):                                                   #给图片重新编写名称下标
        #     os.rename(os.path.join(op_path, img), os.path.join(op_path, strimage_name + str(idx).zfill(zfill_count) + '.png'))

    rarity_table = rarity_table.reset_index()                                                                     #将数据写入表格形式
    rarity_table = rarity_table.drop('index', axis=1)                                                             #删除第二行

    return rarity_table

def main():
    global log
    folder_path = "./log"
    if not os.path.exists(folder_path):                                                                           #判断log文件夹创建日志
        os.makedirs(folder_path)
    log = Logger('./log/all.log', level='info')
    log.logger.info('检查配置...')

    filename = './config.yaml'                                                                                    #读取config.yaml文件
    global CONFIG
    config = set_config(filename)
    CONFIG = config["CONFIG"]

    log.logger.info(filename)
    log.logger.info(config)

    log.logger.info('检查素材...')
    parse_config()                                                                                                #计算素材可合成总和
    tot_comb = get_total_combinations()
    log.logger.info("您可以创建总共%i个不同的NFT" % (tot_comb))

    log.logger.info("您希望创建多少个NFT？输入一个大于0的数字:")
    while True:
        num_avatars = int(input())
        if num_avatars > 0:
            break

    log.logger.info(f"创建{num_avatars}个NFT")
    log.logger.info("您想把该NFT项目命名为:")
    edition_name = input()

    log.logger.info(f"存储NFT文件夹名:{edition_name}")
    log.logger.info("开始生成...")
    rt = generate_images(edition_name, num_avatars,config["drop_dup"])
    log.logger.info("保存元数据...")

    rt.to_csv(os.path.join('output', 'edition ' + str(edition_name), strimage_name + '.csv'))
    log.logger.info(strimage_name + '.csv生成成功!')
    log.logger.info("--------------------------------------------------------------------------------------------")
main()




