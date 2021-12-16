from numpy import linalg as LA
from towhee import pipeline
from PIL import Image

embedding_pipeline = pipeline('image-embedding')

img = Image.open(img_path)
feat = embedding_pipeline(img)
norm_feat = feat / LA.norm(feat)
