from PIL import Image
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
from mylog import *
import argparse

def get_pic_info(logger, file_name):
    str_tmp = file_name
    pos_end = str_tmp.rfind(".png")

    if pos_end == -1:
        Log.warning(logger, "no vaild png file")
        return 0, 0, 0, 0
    
    top_x = int(str_tmp[pos_end-19:pos_end-15])+48
    top_y = int(str_tmp[pos_end-14:pos_end-10])+48
    # width = int(str_tmp[pos_end-9:pos_end-5])-256
    # height = int(str_tmp[pos_end-4:pos_end])-256
    width = int(str_tmp[pos_end-9:pos_end-5])/4
    height = int(str_tmp[pos_end-4:pos_end])/2
    # width = 128
    # height = 256

    # print(top_x,top_y,width,height)
    # print(str_tmp[pos_end-19:pos_end])    
    return top_x, top_y, width, height

def generate_pic_report(logger):
    cur_dir = os.getcwd()
    Log.info(logger, "Stored image folder path is {}".format(cur_dir))
    file_names = []
    file_status = []
    for folder in os.listdir(cur_dir):
        if folder.startswith('Windows'):
            app_dir = cur_dir+'/'+folder
            for root, dir, files in os.walk(app_dir):
                for file in files:
                    top_x,top_y,width,height=get_pic_info(logger, file)
                    img_path = os.path.join(root, file)
                    Log.debug(logger, "processing image {}".format(img_path))
                    # file_names.append(img_path)
                    img = Image.open(img_path)

                    # Crop the image
                    # top_x =90
                    # top_y =220
                    # width=960
                    # height=550
                    area = (top_x, top_y, width+top_x, height+top_y)
                    croped_img = img.crop(area)
                    img_array = np.array(croped_img)

                    # Get the means of r, g, b channels of the image
                    r_means=np.mean(img_array[:,:,0])
                    g_means=np.mean(img_array[:,:,1])
                    b_means=np.mean(img_array[:,:,2])

                    # Determine if the image is greyout
                    if abs(r_means-g_means)<1 and abs(r_means-b_means)<1 and abs(g_means-b_means)<1:
                        file_names.append(img_path)
                        file_status.append('error')
                        Log.error(logger, "Detect failure at image {}".format(img_path))
                    # else:
                    #     file_status.append('normal')

    # Generate a csv file
    report_data = {'files': file_names, 'status': file_status}
    report = pd.DataFrame(data=report_data)
    report.to_csv('grey_statistics.csv', index=False)

if __name__ == "__main__":
    # Input debug level
    parser = argparse.ArgumentParser(description="grey out detection")
    parser.add_argument('-log_level', type=str, help='log level configuration, supported config is CRITICAL,ERROR,WARNING,INFO and DEBUG', required=False, default="INFO")
    
    args = parser.parse_args()
    debug_level = args.log_level
    
    # Run once at startup:
    logging.config.dictConfig(LOGGING_CONFIG)
    # Include in each module:
    logger = logging.getLogger(__name__)
    for handler in logger.handlers:
        handler.setLevel(debug_level)
        
    Log.info(logger, "Image grey out detection start")
    generate_pic_report(logger)
    Log.info(logger, "Image grey out detection end")