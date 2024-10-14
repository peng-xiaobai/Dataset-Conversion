import os
import json
import base64
import io
from PIL import Image, ImageDraw

# 定义JSON文件夹路径、输出图像文件夹路径和输出txt文件夹路径
json_folder = r'f:\111' #json文件夹
output_folder = r'f:\222' #输出图片文件夹
output_txt_folder = r'f:\333' #输出txt文件夹

# 类别列表
category_list = ["Tailings Ponds", "Bare Land", "Water Reservoir"] 
# 如果输出图像文件夹不存在，则创建
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# 如果输出txt文件夹不存在，则创建
if not os.path.exists(output_txt_folder):
    os.makedirs(output_txt_folder)

# 列出文件夹中的所有JSON文件
json_files = [f for f in os.listdir(json_folder) if f.endswith('.json')]
# 遍历每个JSON文件
for json_file in json_files:
    # 读取JSON文件
    with open(os.path.join(json_folder, json_file), 'r') as f:
        data = json.load(f)
    # 解码base64编码的图像数据
    image_data = base64.b64decode(data['imageData'])
    # 创建Image对象
    image = Image.open(io.BytesIO(image_data))
    # 图像的宽度和高度
    image_width, image_height = image.size
    # 创建绘图对象
    draw = ImageDraw.Draw(image)
    # 存储当前JSON文件中所有物体的边界框坐标和类别
    all_boxes = []

    # 遍历每个label
    for shape in data['shapes']:
        # 提取当前label下的所有坐标点
        points = shape['points']

        # 找到当前label下所有坐标点的最小和最大值
        x_values = [point[0] for point in points]
        y_values = [point[1] for point in points]
        x_min = min(x_values)
        x_max = max(x_values)
        y_min = min(y_values)
        y_max = max(y_values)
        # 获取标签名和类别
        label = shape['label']
        category = category_list.index(label)
        # 计算中心点和宽高
        x_center = max(0, (x_min + x_max) / 2.0 / image_width)
        y_center = max(0, (y_min + y_max) / 2.0 / image_height)
        width = max(0, (x_max - x_min) / image_width)
        height = max(0, (y_max - y_min) / image_height)
        # 将归一化后的中心点和宽高存储到列表中
        all_boxes.append({'category': category, 'x_center': x_center, 'y_center': y_center, 'width': width, 'height': height})
    # 构造输出txt文件路径
    output_txt_path = os.path.join(output_txt_folder, json_file.replace('.json', '.txt'))
    image.save(os.path.join(output_folder, json_file.replace('.json', '.jpg')))

    # 将归一化后的中心点和宽高保存到txt文件中
    with open(output_txt_path, 'w') as txt_file:
        for box_info in all_boxes:
            category = box_info['category']
            x_center = box_info['x_center']
            y_center = box_info['y_center']
            width = box_info['width']
            height = box_info['height']

            # 将类别和归一化后的中心点和宽高写入txt文件中
            txt_file.write(f"{category} {x_center} {y_center} {width} {height}\n")

    print(f"Saved normalized coordinates to: {output_txt_path}")
