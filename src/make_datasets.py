import os
import random
import shutil
from collections import defaultdict

def split_data(image_source_folder, text_source_folder, o_folders, ratios, pic_num):
    
    for folder in o_folders:
        iti_i = f'../datasets/{folder}/images'
        iti_t = f'../datasets/{folder}/labels'
        os.makedirs(iti_i, exist_ok=True)
        os.makedirs(iti_t, exist_ok=True)
    
    image_files = sorted([f for f in os.listdir(image_source_folder.format(pic_num))])
    text_files = sorted([f for f in os.listdir(text_source_folder.format(pic_num))])

    random.seed(42)
    all = list(zip(image_files, text_files))
    random.shuffle(all)
    image_files, text_files = zip(*all)

    total = len(image_files)
    group_sizes = [int(total * ratio) for ratio in ratios]

    groups = defaultdict(list)
    start = 0
    for i, size in enumerate(group_sizes):
        groups[i] = (image_files[start:start + size], text_files[start:start + size])
        start += size

    for group_index, (images, texts) in groups.items():
        for image, text in zip(images, texts):
            image_source_path = os.path.join(image_source_folder.format(pic_num), image)
            text_source_path = os.path.join(text_source_folder.format(pic_num), text)

            image_output_folder = o_folders[group_index]
            text_output_folder = o_folders[group_index]

            image_target_path = os.path.join(f'../datasets/{image_output_folder}/images', str(pic_num)+image)
            text_target_path = os.path.join(f'../datasets/{text_output_folder}/labels', str(pic_num)+text)

            shutil.copy(image_source_path, image_target_path)
            shutil.copy(text_source_path, text_target_path)

# dir name
images = "../datasets/org/pic{}/images"
labels = "../datasets/org/pic{}/labels"
o_folders = ["test", "val", "train"]
# 1:1:8 ratio
ratios = [1/10, 1/10, 8/10]
pic_nums = 3

# for i in range(pic_nums):
split_data(images, labels, o_folders, ratios, 3)
split_data(images, labels, o_folders, ratios, 4)
