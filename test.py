import os
from numpy import linalg as LA
from towhee import pipeline
from PIL import Image

encoder = pipeline('image-embedding')

def extract_features(img_dir):
    vectors = []
    pics = []
    for x in os.listdir(img_dir):
        img_path = os.path.join(img_dir, x)
        img = Image.open(img_path)
        feat = encoder(img)
        norm_feat = feat / LA.norm(feat)
        vectors.append(norm_feat.tolist()[0][0])
        pics.append(img_path)
    return vectors, pics

vectors, names = extract_features(image_dir)
ids = milvus_client.insert(table_name, vectors)
milvus_client.create_index(table_name)
mysql_cli.create_mysql_table(table_name)
mysql_cli.load_data_to_mysql(table_name, format_data(ids, names))
