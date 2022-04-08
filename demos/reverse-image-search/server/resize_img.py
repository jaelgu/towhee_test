import os
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

def resize_img(img_path, target_w):
    img = Image.open(img_path)
    old_w, old_h = img.size
    target_h = int((target_w / old_w) * old_h)
    new_img = img.resize((target_w, target_h))
    return new_img

if __name__ == '__main__':
    pc_w = 290
    mobile_w = 139

    img_dir = '../data/img'
    mobile_preview = '../data/preview_mobile'
    pc_preview = '../data/preview_pc'
    if not os.path.exists(mobile_preview):
        os.makedirs(mobile_preview)
    if not os.path.exists(pc_preview):
        os.makedirs(pc_preview)

    try:
        for f in os.listdir(img_dir):
            f_path = os.path.join(img_dir, f)
            if os.path.isdir(f_path):
                for img in os.listdir(f_path):
                    try:
                        if (img.endswith(extension) for extension in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']):
                            img_path = os.path.join(f_path, img)
                            pc_path = os.path.join(pc_preview, img)
                            mobile_path = os.path.join(mobile_preview, img)
                            pc_img = resize_img(img_path, pc_w)
                            mobile_img = resize_img(img_path, mobile_w)
                            pc_img.save(pc_path)
                            mobile_img.save(mobile_path)
                    except Exception as e:
                        print('Fail to resize image for: ', os.path.join(img_dir, f, img))
                        continue
            else:
                raise Exception('ERROR: check image dirs.')
        print('Successfully resized images for preview.')
    except Exception as e:
        raise Exception('Fails to resize images for preview: ', e)

