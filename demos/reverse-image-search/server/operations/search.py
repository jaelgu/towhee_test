import sys

sys.path.append("..")
from logs import LOGGER
from encode import encoder


def do_search(table_name, topk, img_path, milvus_client, mysql_cli, device):
    try:
        model = encoder(table_name)
        feat = model.extract_feature(img_path)
        vectors = milvus_client.search_vectors(table_name, [feat], topk)
        vids = [str(x.id) for x in vectors[0]]
        names, sizes = mysql_cli.search_by_milvus_ids(vids, table_name, device)
        distances = [x.distance for x in vectors[0]]
        return names, sizes, distances
    except Exception as e:
        LOGGER.error(" Error with search : {}".format(e))
        sys.exit(1)
