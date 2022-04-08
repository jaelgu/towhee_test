import os
from milvus import MetricType

############### Milvus Configuration ###############
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", 19530)
INDEX_FILE_SIZE = os.getenv("INDEX_FILE_SIZE", 2048)
METRIC_TYPE = os.getenv("METRIC_TYPE", MetricType.L2)
DIM_DICT = {
    "efficientnetb5": 2048,
    "efficientnetb7": 2560,
    "resnet50": 2048,
    "resnet101": 2048,
    "swinbase": 1024,
    "swinlarge": 1536,
    "vitlarge": 1024,
}

############### MySQL Configuration ###############
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PWD = os.getenv("MYSQL_PWD", "123456")
MYSQL_DB = os.getenv("MYSQL_DB", "mysql")

############### Data Path ###############
DATA_PATH = os.getenv("DATA_PATH", "/data/demos/img-search/imagenet2012/train")
UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/data/demos/img-search/tmp/search-images")
PC_PREVIEW = os.getenv("PC_PREVIEW", "/data/demos/img-search/deploy/data/preview_pc")
MOBILE_PREVIEW = os.getenv("MOBILE_PREVIEW", "/data/demos/img-search/deploy/data/preview_mobile")

############### Number of log files ###############
LOGS_NUM = os.getenv("logs_num", 0)
