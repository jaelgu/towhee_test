from numpy import linalg as LA
from towhee import pipeline

class encoder:
    """
    Say something about the ExampleCalass...

    Args:
        args_0 (`type`):
        ...
    """
    def __init__(self, model_name):
        self.embedding_pipeline = pipeline('towhee/image-embedding-' + model_name)

    def extract_feature(self, img_path):
        # Return the normalized embedding([[vec]]) of image
        feat = self.embedding_pipeline(img_path)
        norm_feat = feat / LA.norm(feat)
        return norm_feat.tolist()

if __name__=='__main__':
    model = encoder('swinbase')
    emb = model.extract_feature('/media/supermicro/DATA1/imagenet2012/train/n15075141/n15075141_999.JPEG')
    print(len(emb))
    print(LA.norm(emb))
