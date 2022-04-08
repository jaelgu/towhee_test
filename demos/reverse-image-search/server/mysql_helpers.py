import pymysql
import sys
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DB
from logs import LOGGER


class MySQLHelper():
    def __init__(self):
        self.conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, port=MYSQL_PORT, password=MYSQL_PWD,
                                    database=MYSQL_DB,
                                    local_infile=True)
        self.cursor = self.conn.cursor()

    def test_connection(self):
        try:
            self.conn.ping()
            self.cursor = self.conn.cursor()
        except Exception:
            self.conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, port=MYSQL_PORT, password=MYSQL_PWD,
                                        database=MYSQL_DB, local_infile=True)
            self.cursor = self.conn.cursor()

    # Create mysql table if not exists
    def create_mysql_table(self, table_name):
        self.test_connection()
        sql = "create table if not exists " + table_name + "(milvus_id TEXT, image_path TEXT, image_name TEXT, raw_size TEXT, pc_size TEXT, mobile_size TEXT);"
        try:
            self.cursor.execute(sql)
            LOGGER.debug("MYSQL create table: {} with sql: {}".format(table_name, sql))
        except Exception as e:
            LOGGER.error("MYSQL ERROR: {} with sql: {}".format(e, sql))
            sys.exit(1)

    # Batch insert (Milvus_ids, image_paths, raw_sizes, pc_sizes, mobile_sizes) to mysql
    def load_data_to_mysql(self, table_name, data):
        self.test_connection()
        sql = "insert into " + table_name + " (milvus_id, image_path, image_name, raw_size, pc_size, mobile_size) values (%s,%s,%s,%s,%s,%s);"
        try:
            self.cursor.executemany(sql, data)
            self.conn.commit()
            LOGGER.debug("MYSQL loads data to table: {} successfully".format(table_name))
        except Exception as e:
            LOGGER.error("MYSQL ERROR: {} with sql: {}".format(e, sql))
            sys.exit(1)

    # Get the img_path according to the milvus ids
    def search_by_milvus_ids(self, ids, table_name, device):
        self.test_connection()
        str_ids = str(ids).replace('[', '').replace(']', '')
        if device == "pc":
            sql = "select image_name, pc_size from " + table_name + " where milvus_id in (" + str_ids + ") order by field (milvus_id," + str_ids + ");"
        elif device == "mobile":
            sql = "select image_name, mobile_size from " + table_name + " where milvus_id in (" + str_ids + ") order by field (milvus_id," + str_ids + ");"
        else:
            raise Exception(f"ERROR: invalid device = {device}")
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            names = [res[0] for res in results]
            sizes = [res[1] for res in results]
            LOGGER.debug("MYSQL search by milvus id.")
            return names, sizes
        except Exception as e:
            LOGGER.error("MYSQL ERROR: {} with sql: {}".format(e, sql))
            sys.exit(1)
        self.cursor.close()

    # Get the img_path according to the image name
    def search_path_by_name(self, table_name, img_name):
        self.test_connection()
        sql = "select image_path from " + table_name + " where image_name = '" + img_name + "';"
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            paths = [res[0] for res in results]
            return paths[0]
        except Exception as e:
            LOGGER.error("MYSQL ERROR: {} with sql: {}".format(e, sql))
            sys.exit(1)
        self.cursor.close()

    # Delete mysql table if exists
    def delete_table(self, table_name):
        self.test_connection()
        sql = "drop table if exists " + table_name + ";"
        try:
            self.cursor.execute(sql)
            LOGGER.debug("MYSQL delete table:{}".format(table_name))
            print("Delete table successfully!")
        except Exception as e:
            LOGGER.error("MYSQL ERROR: {} with sql: {}".format(e, sql))
            sys.exit(1)

    # Delete all the data in mysql table
    def delete_all_data(self, table_name):
        self.test_connection()
        sql = 'delete from ' + table_name + ';'
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            LOGGER.debug("MYSQL delete all data in table:{}".format(table_name))
        except Exception as e:
            LOGGER.error("MYSQL ERROR: {} with sql: {}".format(e, sql))
            sys.exit(1)

    # Get the number of mysql table
    def count_table(self, table_name):
        self.test_connection()
        sql = "select count(milvus_id) from " + table_name + ";"
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            LOGGER.debug("MYSQL count table:{}".format(table_name))
            return results[0][0]
        except Exception as e:
            LOGGER.error("MYSQL ERROR: {} with sql: {}".format(e, sql))
            sys.exit(1)
