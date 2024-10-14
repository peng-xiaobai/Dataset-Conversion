# 作者：CSDN-笑脸惹桃花
# github:peng-xiaobai
import os
import cv2
import numpy as np

'''xml文件格式'''
out0 = '''<annotation>
    <folder>%(folder)s</folder>
    <filename>%(name)s</filename>
    <path>%(path)s</path>
    <source>
        <database>None</database>
    </source>
    <size>
        <width>%(width)d</width>
        <height>%(height)d</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
'''
out1 = '''    <object>
        <name>%(class)s</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>%(xmin)d</xmin>
            <ymin>%(ymin)d</ymin>
            <xmax>%(xmax)d</xmax>
            <ymax>%(ymax)d</ymax>
        </bndbox>
    </object>
'''

out2 = '''</annotation>
'''

def upp2low(directory):
    converted_count = 0
    # 检查目录是否存在
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} does not exist.")
    # 遍历文件夹中的所有文件
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # 仅处理文件
        if os.path.isfile(file_path):
            # 拆分文件名和后缀
            name, extension = os.path.splitext(filename)
            # 检查后缀是否为大写
            if extension.isupper():
                new_filename = name + extension.lower()
                new_file_path = os.path.join(directory, new_filename)
                # 重命名文件
                os.rename(file_path, new_file_path)
                converted_count += 1
                print(f"Renamed: {filename} -> {new_filename}")
    print(f"All file suffixes in the folder are lowercase, and a total of {converted_count} files have been processed")
    return converted_count

def yolo2voc(dir1,dir2,dir3,Class):
    file = os.listdir(dir1)

    source = {}
    label = {}
    for img in file:
        print(img)
        if img.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif')):
            img1 = os.path.join(dir1, img)
            image = cv2.imread(img1)  # 路径不能有中文
            h, w, _ = image.shape  # 图片大小
            name, extension = os.path.splitext(img)
            name1 = name + '.xml'
            name2 = name + '.txt'
            fxml = os.path.join(dir2, name1)
            txt = os.path.join(dir3, name2)
            if not os.path.exists(txt):
                print(f"{name2}未找到，已跳过")
                continue

            fxml = open(fxml, 'w')
            source['name'] = img
            source['path'] = img1
            source['folder'] = os.path.basename(dir1)
            source['width'] = w
            source['height'] = h

            fxml.write(out0 % source)
            lines = np.loadtxt(txt)
            for box in lines:
                if box.shape != (5,):
                    box = lines
                '''把txt上的第一列（类别）转成xml上的类别'''
                box_index = int(box[0])
                label['class'] = Class[box_index] # 类别索引从1开始
                '''把txt上的数字（归一化）转成xml上框的坐标'''
                xmin = float(box[1] - 0.5 * box[3]) * w
                ymin = float(box[2] - 0.5 * box[4]) * h
                xmax = float(xmin + box[3] * w)
                ymax = float(ymin + box[4] * h)
                label['xmin'] = xmin
                label['ymin'] = ymin
                label['xmax'] = xmax
                label['ymax'] = ymax
                keys = ['xmin', 'ymin', 'xmax', 'ymax']
                limits = [w, h, w, h]
                for i, key in enumerate(keys):
                    if label[key] >= limits[i]:
                        label[key] = limits[i]
                    elif label[key] < 0:
                        label[key] = 0

                fxml.write(out1 % label)
            fxml.write(out2)


if __name__ == '__main__':
    l = ["hat","nohat"] #所有类别
    file_dir1 = r' ' #图像文件夹
    file_dir2 = r' '  #xml存放文件夹
    file_dir3 = r' '  #txt存放文件夹
    if not os.path.exists(file_dir2):
        os.makedirs(file_dir2)
    upp2low(file_dir1)
    yolo2voc(file_dir1,file_dir2,file_dir3,l)
    print('Conversion has ended!')
