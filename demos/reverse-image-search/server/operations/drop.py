import sys

sys.path.append("..")
from logs import LOGGER


def do_drop(table_name, milvus_cli, mysql_cli):
    try:
        if not milvus_cli.has_collection(table_name):
            return ("Milvus doesn't have a collection named {}".format(table_name))
        status = milvus_cli.delete_collection(table_name)
        mysql_cli.delete_table(table_name)
        message = "Successfully drop tables in Milvus and MySQL!"
        return message
    except Exception as e:
        LOGGER.error(" Error with  drop table: {}".format(e))
        sys.exit(1)
