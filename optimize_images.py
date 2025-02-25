from utils.image_optimizer import create_thumbnails
import os

if __name__ == '__main__':
    img_dir = os.path.join('static', 'images', 'recommendations')
    create_thumbnails(img_dir)
