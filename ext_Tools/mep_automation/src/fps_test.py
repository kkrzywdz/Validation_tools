import json 
import os
from pymediainfo import MediaInfo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mylog import *
import argparse

def generate_video_report(logger, custom_path=None):
    # vedio_dir = r"C:\Users\Local_Admin\Pictures\Camera Roll"
    
    if custom_path == None:
        home_dir = os.path.expanduser('~')
        video_path = home_dir + "\Pictures\Camera Roll"
    else:
        video_path = custom_path
    
    Log.info(logger, "Video path is {}".format(video_path))

    file_names = []
    file_fps = []
    file_width = []
    file_height = []
    for file in os.listdir(video_path):
        if file.endswith('.mp4'):
            file_path = video_path + '/' + file
            file_names.append(file_path)
            Log.debug(logger, "Get media info from {}".format(file_path))
            # Get the fps of the file
            media_info = MediaInfo.parse(file_path)
            media_json = media_info.to_json()
            media_data = json.loads(media_json)  
            fps = float(media_data['tracks'][1]['frame_rate'])
            file_fps.append(fps)
            width = int(media_data['tracks'][1]['width'])
            file_width.append(width)
            height = int(media_data['tracks'][1]['height'])
            file_height.append(height)

    # Generate a csv file
    fps_dict = {'files': file_names, 'fps': file_fps, 'width': file_width, 'height': file_height}
    fps_df = pd.DataFrame(data=fps_dict)
    fps_df.to_csv('fps_statistics.csv', index=False)

    # Generate a historgram
    ax = fps_df.plot.hist(column=['fps'], bins=range(10, 45, 5))
    plt.xlabel('FPS')
    plt.ylabel('Count')
    plt.savefig('fps_statistics.png')
    plt.show()    

if __name__ == "__main__":
    # Input debug level
    parser = argparse.ArgumentParser(description="fps statistics")
    parser.add_argument('-log_level', type=str, help='log level configuration, supported config is CRITICAL,ERROR,WARNING,INFO and DEBUG', required=False, default="INFO")
    
    args = parser.parse_args()
    debug_level = args.log_level
    
    # Run once at startup:
    logging.config.dictConfig(LOGGING_CONFIG)
    # Include in each module:
    logger = logging.getLogger(__name__)
    for handler in logger.handlers:
        handler.setLevel(debug_level)
        
    Log.info(logger, "Recorded video FPS detection start")
    generate_video_report(logger)
    Log.info(logger,"Recorded video FPS detection end")