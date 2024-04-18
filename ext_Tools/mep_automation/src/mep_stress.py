import os
import time as tm
import string
import argparse

from camera_ops import *
from settings_cam import *
from utils import *
from mylog import *

def get_output_dir(app, resolution):
    cur_time = tm.localtime()
    format_time = tm.strftime('%Y_%m_%d_%H_%M_%S',cur_time)
    str_res=resolution
    punctuation=string.punctuation
    for char in punctuation:
        str_res = str_res.replace(char, ' ')
    str_res=str_res.replace(' ', '_')
    logger = logging.getLogger("__main__")
    path = app+"_"+str_res
    out_folder = "{}\{}".format(path, format_time)
    Log.debug(logger, "Get output folder")
    Log.debug(logger, out_folder)

    return out_folder

def mep_cam_test(value, resolution, abs_path, r_w, r_h):
    task = MepStressTask(value['app'],
                        resolution,
                        value['screenshot'],
                        value['interval'],
                        value['loopCnt'],
                        value['sub_tests'],
                        value['function'],
                        abs_path,
                        r_w,
                        r_h)

    task.run()
    stress=mep_cam(task)
    stress.task_init()
    stress.mep_cam_run()
    return

def mep_settings_test(value, resolution, abs_path):
    task = MepStressTask(value['path'],
                        resolution,
                        value['screenshot'],
                        value['interval'],
                        value['loopCnt'],
                        value['sub_tests'],
                        value['function'],
                        abs_path)

    task.run()
    stress=mep_settings(task)
    stress.task_init()
    stress.mep_settings_run()
    return

def get_camera_config():
    logger = logging.getLogger("__main__")
    camera_mep=CameraOps("WindowsCamera")
    camera_mep.start_app()
    camera_mep.ret_mainview()

    default_cfg = camera_mep.camera_default_settings()
    res_lists = camera_mep.get_video_resoulution()
    if len(res_lists) == 0:
        Log.warning(logger, "Get camera resolution failed, only config default resolution")
        camera_cfg= {"720p 16:9"  : 0}
        return camera_cfg
    Log.debug(logger, res_lists)
    camera_cfg = {}
    for idx in range(len(res_lists)):
        # print(res_lists[idx], idx)
        camera_cfg[res_lists[idx]] = idx

    camera_mep.close_camera()

    return default_cfg, camera_cfg

def set_camera_config(default_cfg):
    logger = logging.getLogger("__main__")
    camera_mep=CameraOps("WindowsCamera")
    camera_mep.start_app()
    camera_mep.ret_mainview()

    default_cfg = camera_mep.camera_default_settings(default_cfg)

    camera_mep.close_camera()

    return default_cfg

class mep_cam:

    def __init__(self, task) -> None:
        self.app = task.app_name
        self.resolution = task.resolution
        self.screenshot = task.screenshot
        self.interval = task.interval
        self.loopCnt = task.loopCnt
        self.subtests = task.subtests
        self.function = task.function
        self.camera = None
        self.save_path = task.save_path
        self.ratio_w = task.ratio_w
        self.ratio_h = task.ratio_h
        self.logger = logging.getLogger("__main__")


    def task_init(self):
        if self.screenshot == 'True':
            if os.path.exists('{}'.format(self.save_path)) == False:
                Log.debug(self.logger, "make dir {}".format(self.save_path))
                os.system('mkdir {}'.format(self.save_path))
        self.camera = CameraOps(self.app)
        self.camera.start_app()
        self.camera.ret_mainview()
        self.camera.switch_to_video()
        self.camera.change_video_resoulution(self.resolution)


    def mep_cam_run(self):
        if self.function == 'mep_toggle':
            Log.debug(self.logger, "mep_toggle test, loopCnt {}".format(self.loopCnt))
            for idx in range(self.loopCnt):
                Log.debug(self.logger, "turn on MEP effects, iter = {}".format(idx))
                self.camera.mep_effects_on(idx, self.subtests, self.ratio_w, self.ratio_h, self.interval,path=self.save_path)
                Log.debug(self.logger, "turn off MEP effects")
                self.camera.mep_effects_off(idx, self.subtests, self.ratio_w, self.ratio_h, self.interval, path=self.save_path)

        elif self.function == 'video_recording':
            Log.debug(self.logger, "video_recording start")
            for idx in range(self.loopCnt):
                Log.debug(self.logger, "turn on MEP effects, iter =  {}, interval = {} s".format(idx, self.interval))
                self.camera.mep_effects_on(idx, self.subtests, self.ratio_w, self.ratio_h, 1,path=None)
                self.camera.video_recording(self.interval)
                self.camera.mep_effects_off(idx, self.subtests, self.ratio_w, self.ratio_h, 1, path=None)

        self.camera.close_camera()
class mep_settings:

    def __init__(self, task) -> None:
        self.app = task.app_name
        self.resolution = task.resolution
        self.screenshot = task.screenshot
        self.interval = task.interval
        self.loopCnt = task.loopCnt
        self.subtests = task.subtests
        self.function = task.function
        self.settings_camera = None
        self.save_path = task.save_path
        self.logger = logging.getLogger("__main__")


    def task_init(self):
        if self.screenshot == 'True':
            if os.path.exists('{}'.format(self.save_path)) == False:
                Log.debug(self.logger, "make dir {}".format(self.save_path))
                os.system('mkdir {}'.format(self.save_path))
        self.settings_camera = SettingCamOps(self.app)
        self.settings_camera.start_app()
        self.settings_camera.enter_camera_settings()

    def mep_settings_run(self):
        if self.function == 'mep_toggle':
            for idx in range(self.loopCnt):
                self.settings_camera.mep_effects_on(idx, self.subtests, self.interval,path=self.save_path)
                self.settings_camera.mep_effects_off(idx, self.subtests, self.interval, path=self.save_path)

            self.settings_camera.close_settings()




if __name__ == "__main__":
    # Input debug level
    parser = argparse.ArgumentParser(description="mep stress test")
    parser.add_argument('-log_level', type=str, help='log level configuration, supported config is CRITICAL,ERROR,WARNING,INFO and DEBUG', required=False, default="INFO")

    args = parser.parse_args()
    debug_level = args.log_level

    # Run once at startup:
    logging.config.dictConfig(LOGGING_CONFIG)
    # Include in each module:
    logger = logging.getLogger(__name__)
    for handler in logger.handlers:
        handler.setLevel(debug_level)

    Log.info(logger, "Get Device")
    getNpuDevices()
    data = read_json("mep_stress.json")

    # print(data1)

    # mep_tasks = []
    # custom_tasks = []
    try:
        cam_data = read_json("cam_cfg.json")
        camera_cfg = cam_data["camera_resolution"]
        default_cfg = cam_data["default_settings"]
        set_camera_config(default_cfg)
    except:
        Log.warning(logger, "No valid camera configuration cam_cfg.json, create it automatically")
        default_cfg, camera_cfg = get_camera_config()
        cam_json = {}
        cam_json["camera_resolution"]=camera_cfg
        cam_json["default_settings"]=default_cfg
        write_json("cam_cfg.json",cam_json)
        Log.info(logger, "Generate camera configuration json file cam_cfg.json")


    Log.info(logger, "Camera Supported Resolution is")
    Log.info(logger, "{}".format(camera_cfg))

    for key, value_list in data.items():
        # print(key)
        # print(value)
        if key == "mep_stress":
            for value in value_list:
                # print(value)
                if value['app'] == 'WindowsCamera':
                    if value["resolution"] == "":
                        for res in camera_cfg.items():
                            resolution = res[1]
                            r_w, r_h = get_resolution_ratio(res[0])
                            abs_path = None
                            if value['screenshot'] == 'True':
                                screenshot_path=get_output_dir(value['app'], res[0])
                                # print(res)
                                abs_path = os.path.abspath(screenshot_path)
                                # print(abs_path)

                            mep_cam_test(value, resolution, abs_path, r_w, r_h)
                    else:
                        resolution = camera_cfg[value["resolution"]]
                        r_w, r_h = get_resolution_ratio(value["resolution"])
                        abs_path = None
                        if value['screenshot'] == 'True':
                            screenshot_path=get_output_dir(value['app'], value["resolution"])
                            abs_path = os.path.abspath(screenshot_path)
                            # print(abs_path)

                        mep_cam_test(value, resolution, abs_path, r_w, r_h)

                if value['app'] == 'WindowsSettings':
                    resolution = 0
                    abs_path = None

                    if value['screenshot'] == 'True':
                        screenshot_path=get_output_dir(value['app'], 'default')
                        abs_path = os.path.abspath(screenshot_path)
                        # print(abs_path)
                    mep_settings_test(value, resolution, abs_path)

        elif key == "custom":
            for value in value_list:
                print(value)
                for key1, value1 in value.items():
                    print(key1)
                    print(value1)