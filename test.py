from numpy import linalg as LA
from towhee import pipeline

encoder = pipeline('image-embedding')
feat = encoder(img_path)
norm_feat = feat / LA.norm(feat)
