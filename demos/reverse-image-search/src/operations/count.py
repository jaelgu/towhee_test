import sys

sys.path.append("..")
from logs import LOGGER


def do_count(table_name, milvus_cli):
    try:
        if not milvus_cli.has_collection(table_name):
            return None
        num = milvus_cli.count(table_name)
        return num
    except Exception as e:
        LOGGER.error(" Error with count table {}".format(e))
        sys.exit(1)

if __name__ == '__main__':
    from milvus_helpers import MilvusHelper

    MILVUS_CLI = MilvusHelper()
    do_count('resnet101', MILVUS_CLI)
