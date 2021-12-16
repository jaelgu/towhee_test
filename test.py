import os
from numpy import linalg as LA
from towhee import pipeline

encoder = pipeline('image-embedding')

def extract_features(img_dir):
    vectors = []
    pics = []
    for x in os.listdir(img_dir):
        img_path = os.path.join(img_dir, x)
        feat = encoder(img_path)
        norm_feat = feat / LA.norm(feat)
        vectors.append(norm_feat.tolist()[0][0])
        pics.append(img_path)
    return vectors, pics

# Get vectors & image paths
vectors, names = extract_features(image_dir)
# Insert vectors into milvus table & build index
ids = milvus_client.insert(table_name, vectors)
milvus_client.create_index(table_name)
# Insert milvus ids & image paths into mysql
mysql_cli.load_data_to_mysql(table_name, format_data(ids, names))
