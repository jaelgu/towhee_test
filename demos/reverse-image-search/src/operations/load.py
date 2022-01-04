import sys
import os
import numpy
from numpy import linalg as LA
from diskcache import Cache
from PIL import Image

sys.path.append("..")
from config import PC_PREVIEW, MOBILE_PREVIEW
from logs import LOGGER

# Get the paths to the image [original, pc_preview, mobile_preview]
def get_paths(dir, pc_dir, mobile_dir):
    original_paths = []
    pc_paths = []
    mobile_paths = []
    for f in os.listdir(dir):
        if ((f.endswith(extension) for extension in
             ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']) and not f.startswith('.DS_Store')):
            origin = os.path.join(dir, f)
            pc = os.path.join(pc_dir, f)
            mobile = os.path.join(mobile_dir, f)
            original_paths.append(origin)
            pc_paths.append(pc)
            mobile_paths.append(mobile)
    return original_paths, pc_paths, mobile_paths

def get_sizes(path_list, pc_dir, mobile_dir):
    original_sizes = []
    pc_sizes = []
    mobile_sizes = []
    for x in path_list:
        name = os.path.basename(x)

        pc_path = os.path.join(pc_dir, name)
        mobile_path = os.path.join(mobile_dir, name)

        img = Image.open(x)
        pc_img = Image.open(pc_path)
        mobile_img = Image.open(mobile_path)

        w, h = img.size
        w_pc, h_pc = pc_img.size
        w_mobile, h_mobile = mobile_img.size

        orig_size = str(w) + 'x' + str(h)
        pc_size = str(w_pc) + 'x' + str(h_pc)
        mobile_size = str(w_mobile) + 'x' + str(h_mobile)

        original_sizes.append(orig_size)
        pc_sizes.append(pc_size)
        mobile_sizes.append(mobile_size)
    return original_sizes, pc_sizes, mobile_sizes

# Combine the id of the vector and the name of the image into a list
def format_data(ids, paths, raw_sizes, pc_sizes, mobile_sizes):
    data = []
    for i in range(len(ids)):
        value = (str(ids[i]), paths[i], os.path.basename(paths[i]), raw_sizes[i], pc_sizes[i], mobile_sizes[i])
        data.append(value)
    return data

# Get the vector of images
def extract_features(img_dir, model):
    try:
        cache = Cache('./tmp')
        feats = []
        paths = []
        img_list, _ , _ = get_paths(img_dir, PC_PREVIEW, MOBILE_PREVIEW)
        total = len(img_list)
        cache['total'] = total
        for i, img_path in enumerate(img_list):
            try:
                norm_feat = model.extract_feature(img_path)
                feats.append(norm_feat)
                paths.append(img_path)
                cache['current'] = i + 1
                print(f"Extracting feature from image No. {i + 1} , {total} images in total")
            except Exception as e:
                LOGGER.error(f"Error with extracting feature from image {e}")
                continue
        return feats, paths
    except Exception as e:
        LOGGER.error(f"Error with extracting feature from image {e}")
        sys.exit(1)

# Get the vector of images
def load_features(subdir):
    try:
        cache = Cache('./tmp')
        feats = []
        imgs = []
        sublist = os.listdir(subdir)
        total = len(sublist)
        cache['total'] = total

        for i in range(len(sublist)):
            try:
                if (sublist[i].endswith(extension) for extension in ['.npy']):
                    f_path = os.path.join(subdir, sublist[i])
                    x = numpy.load(f_path, allow_pickle=True)
                    y = x.tolist()
                    feat =  y['feat'] / LA.norm(y['feat'])
                    feats.append(feat.tolist())
                    #path = y['path']
                    path = y['path'].replace('/home/supermicro/下载', '/media/supermicro/DATA1/')
                    imgs.append(path)
                    cache['current'] = i + 1
                    print(f"Extracting feature from No. {i + 1} / {total} images in folder {subdir}")
            except Exception as e:
                LOGGER.error(f"Error with loading feature of images {e}")
                continue

        return feats, imgs

    except Exception as e:
        LOGGER.error(f"Error with extracting feature from image {e}")
        raise Exception(f"Error with extracting feature from image {e}")

# Import vectors to Milvus and data to Mysql respectively
def do_load_img(table_name, image_dir, model, milvus_client, mysql_cli):
    vectors, paths = extract_features(image_dir, model)
    ids = milvus_client.insert(table_name, vectors)
    original_sizes, pc_sizes, mobile_sizes = get_sizes(paths, PC_PREVIEW, MOBILE_PREVIEW)
    milvus_client.create_index(table_name)
    mysql_cli.create_mysql_table(table_name)
    mysql_cli.load_data_to_mysql(table_name, format_data(ids, paths, original_sizes, pc_sizes, mobile_sizes))
    return len(ids)

# Import vectors to Milvus and data to Mysql respectively
def do_load_feat(table_name, feat_dir, milvus_client, mysql_cli):
    total_ids = []
    for subfold in os.listdir(feat_dir):
        sub_path = os.path.join(feat_dir, subfold)
        vectors, img_paths = load_features(sub_path)
        ids = milvus_client.insert(table_name, vectors)
        original_sizes, pc_sizes, mobile_sizes = get_sizes(img_paths, PC_PREVIEW, MOBILE_PREVIEW)
        milvus_client.create_index(table_name)
        mysql_cli.create_mysql_table(table_name)
        mysql_cli.load_data_to_mysql(table_name, format_data(ids, img_paths, original_sizes, pc_sizes, mobile_sizes))
        total_ids.append(ids)
    return len(total_ids)

if __name__ == "__main__":
    from milvus_helpers import MilvusHelper
    from mysql_helpers import MySQLHelper
    from encode import encoder

    MODEL = encoder("resnet50")

    MILVUS_CLI = MilvusHelper()
    MYSQL_CLI = MySQLHelper()
    dir = '../../data/vec'

    do_load_feat(table_name, feat_dir, milvus_client, mysql_cli)
