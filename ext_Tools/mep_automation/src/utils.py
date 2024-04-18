import subprocess
import pywinauto
import json
from mylog import *

def getMsftAppPath(app_name):
    # command =  '(Get-AppxPackage Microsoft.WindowsCamera).InstallLocation'
    logger = logging.getLogger("my.func")
    command = '('+'Get-AppxPackage '+'Microsoft.'+app_name+')'+'.InstallLocation'
    # print(command)
    Log.debug(logger, "MSFT application path: ")
    Log.debug(logger, command)
    p = subprocess.Popen(['powershell', '-Command', command], stdout=subprocess.PIPE)
    output = p.communicate()[0].decode()
    # print(output)
    return output.rstrip("\r\n")+'\\'+app_name+'.exe'

def getNpuDevices():
    dev_lists = ["PCI\VEN_8086&DEV_643E",
                "PCI\VEN_8086&DEV_AD1D",
                "PCI\VEN_8086&DEV_7D1D",
                "PCI\VEN_8086&DEV_B03E",
                "PCI\VEN_8086&DEV_FD3E"]
    dev_sum = 0
    output_str = None
    logger = logging.getLogger("__main__")
    for dev in dev_lists:
        command = 'pnputil /enum-devices | findstr ' + '"' + dev + '"'
        p = subprocess.Popen(['powershell', '-Command', command], stdout=subprocess.PIPE)
        output = p.communicate()[0].decode()
        if len(output) > 0:
            output_str = output
        dev_sum += len(output)

    if dev_sum == 0:
        Log.critical(logger, "No valid Intel NPU")
        raise SystemExit()
    pos = output_str.find('P')
    Log.info(logger, output_str[pos:-1])

    return


def getSettingsPath(settings_name):
    logger = logging.getLogger("my.func")
    command = 'cmd.exe /c start '+ settings_name
    Log.debug(logger, "Windows Settings Command: ")
    Log.debug(logger, command)
    return command

def get_control_wrapper(app_windows, match_class, match_text):
    logger = logging.getLogger("__main__")
    try:
        for child in app_windows:
            tmp_win=child.descendants()
            for wrapper in tmp_win:
                if wrapper.automation_id().find(match_class) >= 0:
                    if wrapper.window_text().find(match_text) >= 0 :
                        Log.debug(logger, "automation_id '{}' matched, text '{}'".format(match_class, match_text))
                        return wrapper
                else:
                    if wrapper.friendly_class_name().find(match_class) >= 0:
                        if wrapper.window_text().find(match_text) >= 0 :
                            Log.debug(logger, "friendly_class_name '{}' matched, text '{}'".format(match_class, match_text))
                            return wrapper
    except AttributeError:
        Log.warning(logger, "Doesn't get wrapper for '{}' and '{}'".format(match_class, match_text))
    return None

def read_json(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data

def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

def read_json_file(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data

def write_json_file(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

def get_resolution_ratio(input_str):
    pos0 = input_str.find(' ')
    pos1 = input_str.find(':')
    # print(input_str)
    # print(input_str[pos0+1:pos1])
    # print(input_str[pos1+1:])
    radio_w = int(input_str[pos0+1:pos1])
    pos2 = input_str[pos1+1:].find(' ')
    if pos2 < 0:
        radio_h = int(input_str[pos1+1:])
    else:
        radio_h = int(input_str[pos1+1:pos1+1+pos2])
    logger = logging.getLogger("my.func")
    Log.debug(logger, "get_resolution_ratio radio_w {}, radio_h {}".format(radio_w, radio_h))
    return radio_w, radio_h

class MepStressTask:
    def __init__(self, app_name, resolution, screenshot, interval, loopCnt, subtests, func, path, r_w=16, r_h=9):
        self.app_name = app_name
        self.resolution = resolution
        self.screenshot = screenshot
        self.interval = interval
        self.loopCnt = loopCnt
        self.subtests = subtests
        self.function = func
        self.save_path = path
        self.ratio_w = r_w
        self.ratio_h = r_h
        self.logger = logging.getLogger("__main__")


    def run(self):
        Log.info(self.logger, "Starting {} {} test".format(self.app_name,self.function))
        Log.info(self.logger, "Resolution is : {}, ratio is {}:{}".format(self.resolution, self.ratio_w, self.ratio_h))
        Log.info(self.logger, "Screen shot is : {}".format(self.screenshot))
        Log.info(self.logger, "Effects interval is : {}".format(self.interval))
        Log.info(self.logger, "Total loop count is : {}".format(self.loopCnt))



if __name__ == "__main__":
    # Run once at startup:
    logging.config.dictConfig(LOGGING_CONFIG)
    # Include in each module:
    logger = logging.getLogger(__name__)
    for handler in logger.handlers:
        handler.setLevel('DEBUG')
    # path=getMsftAppPath('WindowsCamera')
    # camera_run = '"'+path+'"'
    # subprocess.run(camera_run, shell=True, capture_output=True, text=True)
    Log.info(logger, "Get Devices")
    getNpuDevices()