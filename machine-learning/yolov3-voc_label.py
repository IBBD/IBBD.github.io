# -*- coding: utf-8 -*-
#
# yolov3的voc_label.py，略有修改
# Author: alex
# Created Time: 2019年05月01日 星期三 15时23分25秒
import xml.etree.ElementTree as ET
import os
from os import getcwd

# 找到对应的代码就知道是什么意思
sets = [('helmet', 'helmet_train_utf8'), ('helmet', 'helmet_val_utf8')]
classes = ['helmet']   # 只有一个类别的目标


def convert(size, box):
    dw = 1./size[0]
    dh = 1./size[1]
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


def convert_annotation(year, image_id):
    in_file = open('VOCdevkit/VOC%s/Annotations/%s.xml'%(year, image_id))
    out_file = open('VOCdevkit/VOC%s/labels/%s.txt'%(year, image_id), 'w')
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        if bb[2] < 0.0001 and bb[3] < 0.0001:
            continue    # 注意这里，否则可能会报错
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

wd = getcwd()
for year, image_set in sets:
    if not os.path.exists('VOCdevkit/VOC%s/labels/'%(year)):
        os.makedirs('VOCdevkit/VOC%s/labels/'%(year))
    image_ids = open('VOCdevkit/VOC%s/ImageSets/Main/%s.txt'%(year, image_set), encoding='utf8').read().strip().split()
    list_file = open('%s_%s.txt'%(year, image_set), 'w')
    # print(image_ids)
    for image_id in image_ids:
        filename = '%s/VOCdevkit/VOC%s/JPEGImages/%s.jpg'%(wd, year, image_id)
        if not os.path.isfile(filename):
            continue
        print(filename)
        list_file.write(filename+"\n")
        convert_annotation(year, image_id)
    list_file.close()
