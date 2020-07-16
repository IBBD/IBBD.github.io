import xml.etree.ElementTree as ET
import os
import shutil

# 将项目相关的都放到同一个目录
root_path = 'projects/windows-video-monitor/'    # 相对于darknet的路径
sets = [('train', 'password_train'), ('val', 'password_val'),
        ('train', 'system_train'), ('val', 'system_val')]
classes = ['password', 'system']


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
    return (x, y, w, h)


def convert_annotation(image_id):
    in_file = open('Annotations/%s.xml' % (image_id))
    out_file = open('labels/%s.txt' % (image_id), 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult) == 1:
            print(cls)
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
             float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w, h), b)
        if bb[2] < 0.0001 and bb[3] < 0.0001:
            print(image_id, bb)
            continue
        out_file.write(str(cls_id) + " " +
                       " ".join([str(a) for a in bb]) + '\n')


# 先清除旧文件
if os.path.exists('labels/'):
    shutil.rmtree('labels/')
for txt_filename, _ in sets:
    filename = '%s.txt' % txt_filename
    if os.path.isfile(filename):
        os.remove(filename)

os.makedirs('labels/')
for txt_filename, image_set in sets:
    image_ids = open('ImageSets/Main/%s.txt' % (image_set),
                     encoding='utf8').read().strip().split("\n")
    image_ids = [s.strip() for s in image_ids]
    image_ids = [s.split(' ')[0] for s in image_ids if len(s) > 1]
    # print(image_set, len(image_ids), image_ids[0], image_ids[-1])
    list_file = open('%s.txt' % txt_filename, 'w+')
    # print(image_ids)
    for image_id in image_ids:
        filename = 'JPEGImages/%s' % (image_id)
        if not os.path.isfile(filename):
            print(filename, ' is not exists!')
            continue
        # print(filename)
        list_file.write(root_path+filename+"\n")
        # print(image_id, image_id.replace('.jpg', ''))
        convert_annotation(image_id.replace('.jpg', ''))
    list_file.close()
