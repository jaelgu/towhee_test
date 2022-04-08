import uvicorn
import os
import time
from PIL import Image
from diskcache import Cache
from fastapi import FastAPI, File, UploadFile
#from fastapi.param_functions import Form
#from werkzeug.utils import secure_filename
from fastapi.middleware.cors import CORSMiddleware
#from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.requests import Request
from encode import encoder
from milvus_helpers import MilvusHelper
from mysql_helpers import MySQLHelper
from config import UPLOAD_PATH, PC_PREVIEW, MOBILE_PREVIEW, DIM_DICT
from operations.load import do_load_img, do_load_feat
from operations.search import do_search
from operations.count import do_count
from operations.drop import do_drop
from logs import LOGGER
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

MILVUS_CLI = MilvusHelper()
MYSQL_CLI = MySQLHelper()

# Pre-load models in pipelines
for x in DIM_DICT.keys():
    MODEL = encoder(x)
    MODEL.extract_feature('https://github.com/towhee-io/towhee/raw/main/docs/get-started/towhee.jpeg')

# Mkdir '/tmp/search-images'
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)
    LOGGER.info(f"mkdir the path:{UPLOAD_PATH}")

@app.get('/model')
async def model_list():
    model_list = []
    for x in DIM_DICT.keys():
        model_list.append(x)
    return {"model_list": model_list}

@app.get('/data/raw')
async def get_raw_img(table_name: str = None, image_name: str = None):
    # Get the image file
    try:
        image_path = MYSQL_CLI.search_path_by_name(table_name, image_name)
        LOGGER.info(f"Successfully load image: {image_path}")
        return FileResponse(image_path)
    except Exception as e:
        LOGGER.error(f"Get image error: {e}")
        return {'status': False, 'msg': e}, 400

@app.get('/data/pc')
async def get_pc_img(image_name: str = None):
    # Get the image file
    try:
        image_path = os.path.join(PC_PREVIEW, image_name)
        LOGGER.info(f"Successfully load image: {image_path}")
        return FileResponse(image_path)
    except Exception as e:
        LOGGER.error(f"Get image error: {e}")
        return {'status': False, 'msg': e}, 400

@app.get('/data/mobile')
async def get_mobile_img(image_name: str = None):
    # Get the image file
    try:
        image_path = os.path.join(MOBILE_PREVIEW, image_name)
        LOGGER.info(f"Successfully load image: {image_path}")
        return FileResponse(image_path)
    except Exception as e:
        LOGGER.error(f"Get image error: {e}")
        return {'status': False, 'msg': e}, 400

@app.get('/process')
async def get_progress():
    # Get the progress of dealing with images
    try:
        cache = Cache(UPLOAD_PATH[:-14])
        return f"current: {cache['current']}, total: {cache['total']}"
    except Exception as e:
        LOGGER.error(f"upload image error: {e}")
        return {'status': False, 'msg': e}, 400

class Item(BaseModel):
    Table: Optional[str] = None
    File: str

@app.post('/img/load')
async def load_images(item: Item):
    # Insert all the image under the file path to Milvus/MySQL
    try:
        model = encoder(item.Table)
        total_num = do_load_img(item.Table, item.File, model, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info(f"Successfully loaded data, total count: {total_num}")
        return "Successfully loaded data!"
    except Exception as e:
        LOGGER.error(e)
        return {'status': False, 'msg': e}, 400

@app.post('/feature/load')
async def load_features(item: Item):
    # Insert all the image under the file path to Milvus/MySQL
    try:
        total_num = do_load_feat(item.Table, item.File, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info(f"Successfully loaded data, total count: {total_num}")
        return "Successfully loaded data!"
    except Exception as e:
        LOGGER.error(e)
        return {'status': False, 'msg': e}, 400

@app.post('/search')
async def search_images(request: Request, image: UploadFile = File(...), table_name: str = None, device="pc", page: int = 1, num: int = 16):
    # Search the upload image in Milvus/MySQL
    try:
        content = await image.read()
        print('Successfully read pic.')
        img_path = os.path.join(UPLOAD_PATH, image.filename)
        with open(img_path, "wb+") as f:
            f.write(content)
        img = Image.open(img_path)
        if img.mode != 'RGB':
            new_img = img.convert('RGB')
        else:
            new_img = img
        if image.filename=="blob":
            img_path = img_path + ".jpeg"
        new_img.save(img_path)
        topk = page * num
        start = time.time()
        names, sizes, distances = do_search(table_name, topk, img_path, MILVUS_CLI, MYSQL_CLI, device)
        end = time.time()
        duration = end - start
        names, sizes, distances = names[-num:], sizes[-num:], distances[-num:]

        host = request.headers['host']
        pre_pcs = []
        pre_mobiles = []
        for name in names:
            request_pc = "http://" + host + "/data/pc?&image_name=" + name
            request_mobile = "http://" + host + "/data/mobile?&image_name=" + name
            pre_pcs.append(request_pc)
            pre_mobiles.append(request_mobile)

        if device == "pc":
            res = zip(pre_pcs, sizes, distances)
        elif device == "mobile":
            res = zip(pre_mobiles, sizes, distances)
        else:
            raise Exception(f"ERROR: invalid device = {device}")
        res = sorted(res, key=lambda item: item[2])
        LOGGER.info("Successfully searched similar images!")
        return duration, res
    except Exception as e:
        LOGGER.error(e)
        return {'status': False, 'msg': e}, 400


@app.post('/count')
async def count_images(table_name: str = None):
    # Returns the total number of images in the system
    try:
        num = do_count(table_name, MILVUS_CLI)
        LOGGER.info("Successfully count the number of images!")
        return num
    except Exception as e:
        LOGGER.error(e)
        return {'status': False, 'msg': e}, 400


@app.post('/drop')
async def drop_tables(table_name: str = None):
    # Delete the collection of Milvus and MySQL
    try:
        status = do_drop(table_name, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info("Successfully drop tables in Milvus and MySQL!")
        return status
    except Exception as e:
        LOGGER.error(e)
        return {'status': False, 'msg': e}, 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=5000)
