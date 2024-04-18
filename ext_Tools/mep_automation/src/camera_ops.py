import pywinauto
import pyautogui
from pywinauto.application import Application
from pywinauto.keyboard import *
from time import sleep
# import utils
from utils import getMsftAppPath, get_control_wrapper
from mylog import *


class CameraOps:
    def __init__(self, app_name):
        self.app_name = app_name
        self.app_path = getMsftAppPath(app_name)
        self.app_windows = None
        self.win = None
        self.mep_ops = {}
        self.pos_center = 0
        self.video_recording_flag = False
        self.logger = logging.getLogger("my.func")

    def start_app(self):
        app_ret=Application(backend="uia").start(self.app_path, timeout=2, wait_for_idle=False)
        if app_ret.is_process_running()==True:
            app = Application(backend="uia").connect(title="Camera", timeout=5)
            sleep(2)
            if app.process is None:
                Log.error(self.logger, "Camera application connect failed, retry connect after 10 second")
                sleep(10)
                app_retry = Application(backend="uia").connect(title="Camera", timeout=5)
                if app_retry.process is None:
                    Log.critical(self.logger, "Camera application retry connected failed, exit")
                    raise SystemExit()
                else:
                    Log.debug(self.logger, "Camera application retry start successfully")
                    Log.debug(self.logger, "Camera application process id is {}".format(app_retry.process))
                    self.app_windows  = app_retry.windows()
                    self.win = app_retry.window(title="Camera")
            else:
                Log.debug(self.logger, "Camera application start successfully")
                Log.debug(self.logger, "Camera application process id is {}".format(app.process))
                self.app_windows  = app.windows()
                self.win = app.window(title="Camera")
        else:
            Log.error(self.logger, "Camera application start failed, please check the application installation and CPU status")
            raise SystemExit()

    def get_back_button(self):
        back_wrapper = get_control_wrapper(self.app_windows, "CloseButton", "Back")
        return back_wrapper

    def ret_mainview(self):
        current_view = self.get_back_button()
        if current_view:
            Log.debug(self.logger, "swich to mainview")
            current_view.click()
            sleep(2)
        else:
            Log.debug(self.logger, "return button is not availbale, already in mainview")
        return

    def switch_to_video(self):
        # Check video recording is active or not
        Log.debug(self.logger, "Switch to video mode")
        video_pause_wrapper = get_control_wrapper(self.app_windows, "Button", "Stop taking")
        if video_pause_wrapper:
            Log.warning(self.logger, "Video recording is active")
            self.video_recording_flag = True
            self.pos_center = video_pause_wrapper.rectangle().mid_point().y

            return video_pause_wrapper

        video_wrapper = get_control_wrapper(self.app_windows, "Button", "Take video")

        if video_wrapper == None:
            try:
                Log.debug(self.logger, "get mode switch button wrapper")
                switch_wrapper = get_control_wrapper(self.app_windows, "Button", "Switch to")
                while video_wrapper == None:
                    switch_wrapper.click()
                    sleep(2)
                    Log.debug(self.logger, "Switch to next available mode")
                    video_wrapper = get_control_wrapper(self.app_windows, "Button", "Take video")
            except AttributeError:
                Log.critical(self.logger, "can't switch to video mode, please restart the camera application")
                raise SystemExit()

        self.pos_center = video_wrapper.rectangle().mid_point().y
        return video_wrapper

    def video_recording(self, duriation):
        take_video_wrapper = self.switch_to_video()
        take_video_wrapper.set_focus()
        if self.video_recording_flag == False:
            take_video_wrapper.click()
        sleep(duriation)
        take_video_wrapper.click()
        sleep(5)
        self.video_recording_flag = False
        return

    def switch_to_photo(self):
        self.switch_to_video()
        photo_wrapper = get_control_wrapper(self.app_windows, "Button", "Take photo")

        if photo_wrapper == None:
            try:
                Log.debug(self.logger, "get mode switch button wrapper for photo")
                switch_wrapper = get_control_wrapper(self.app_windows, "Button", "Switch to photo")
                while photo_wrapper == None:
                    switch_wrapper.click()
                    sleep(2)
                    Log.debug(self.logger, "Switch to next available mode")
                    photo_wrapper = get_control_wrapper(self.app_windows, "Button", "Take photo")
            except AttributeError:
                Log.critical(self.logger, "can't switch to photo mode, please restart the camera application")
                raise SystemExit()
        return

    def change_video_resoulution(self, profile_idx):
        if self.video_recording_flag == True:
            Log.warning(self.logger, "Video recording is active, can't change resolution")
            self.ret_mainview()
            return
        try:
            settings_wrapper = get_control_wrapper(self.app_windows, "settingsButton", "Settings")
            settings_wrapper.click()
            sleep(3)

            videosettings_wrapper = get_control_wrapper(self.app_windows, "Button", "Video settings")
            videosettings_wrapper.set_focus()
            group = videosettings_wrapper.children()
            group[0].expand()
            sleep(3)

            videoquality_wrapper = get_control_wrapper(self.app_windows, "ComboBox", "Video quality")
            videoquality_wrapper.select(profile_idx)
            sleep(3)
        except AttributeError:
            Log.warning(self.logger, "Can't get video resolution change wrapper, resolution not changed.")

        self.ret_mainview()
        return

    def get_video_resoulution(self):
        total_resolutions = 0
        res_lists = []
        if self.video_recording_flag == True:
            Log.warning(self.logger, "Video recording is active, can't get the camera resolution, recommend to stop camera recording or add camera resolution in json file ")
            self.ret_mainview()
            return res_lists
        try:
            settings_wrapper = get_control_wrapper(self.app_windows, "settingsButton", "Settings")
            settings_wrapper.click()
            sleep(3)

            videosettings_wrapper = get_control_wrapper(self.app_windows, "Button", "Video settings")
            videosettings_wrapper.set_focus()
            group = videosettings_wrapper.children()
            group[0].expand()
            sleep(3)

            videoquality_wrapper = get_control_wrapper(self.app_windows, "ComboBox", "Video quality")
            # print(videoquality_wrapper.get_selection())
            Log.debug(self.logger, videoquality_wrapper.item_count())
            # Log.debug(self.logger, videoquality_wrapper.texts())
            total_resolutions = videoquality_wrapper.item_count() - 1
            videoquality_wrapper.select(total_resolutions - 1)
            sleep(1)
            res_lists = videoquality_wrapper.texts()
        except AttributeError:
            Log.warning(self.logger, "Can't get video resolution change wrapper, please restart the camera application.")

        self.ret_mainview()
        return res_lists

    def camera_default_settings(self, index_str="Use custom in-app settings"):
        if self.video_recording_flag == True:
            Log.warning(self.logger, "Video recording is active, can't change the camera default settings, recommend to stop camera recording or add camera resolution in json file ")
            self.ret_mainview()
            return index_str
        try:
            settings_wrapper = get_control_wrapper(self.app_windows, "settingsButton", "Settings")
            settings_wrapper.click()
            sleep(3)

            camerasettings_wrapper = get_control_wrapper(self.app_windows, "Button", "Camera settings")
            camerasettings_wrapper.set_focus()
            group = camerasettings_wrapper.children()
            group[0].expand()
            sleep(3)

            defaultsettings_wrapper = get_control_wrapper(self.app_windows, "ComboBox", "Default settings")
            total_cfg = defaultsettings_wrapper.item_count() - 1
            for idx in range(total_cfg):
                defaultsettings_wrapper.select(idx)
                sleep(1)
                selected_item = defaultsettings_wrapper.selected_text()
                if selected_item.find(index_str) >= 0 :
                    # print(selected_item)
                    break
            group[0].collapse()
        except:
            Log.warning(self.logger, "Can't change the default setting, please update and restart the camera application.")

        self.ret_mainview()
        return index_str


    def maximize_restore_camera(self):
        try:
            max_wrapper = get_control_wrapper(self.app_windows, "Maximize", "Camera")
            max_wrapper.click()
            sleep(2)
        except AttributeError:
            Log.warning(self.logger, "max or restore camera failed.")
        return

    def minimize_camera(self):
        try:
            max_wrapper = get_control_wrapper(self.app_windows, "Minimize", "Camera")
            max_wrapper.click()
            sleep(2)
        except AttributeError:
            Log.warning(self.logger, "min camera failed.")
        return

    def close_camera(self):
        try:
            close_wrapper = get_control_wrapper(self.app_windows, "Close", "Camera")
            close_wrapper.click()
            sleep(2)
        except AttributeError:
            Log.warning(self.logger, "close camera failed.")
        return

    def get_effects_status(self):
        try:
            effects_wrapper = get_control_wrapper(self.app_windows, "CameraEffectToggleButton", "Effects")
            toggle_state = effects_wrapper.get_toggle_state()
        except AttributeError:
            Log.critical(self.logger, "Camera Effect Toggle Button is not available, update and restart the Windows Camera application.")
            raise SystemExit()
        return toggle_state

    def windows_studio_effects_on(self):
        try:
            effects_wrapper = get_control_wrapper(self.app_windows, "CameraEffectToggleButton", "Effects")
            toggle_state = effects_wrapper.get_toggle_state()
            if toggle_state:
                return
            effects_wrapper.toggle()
            sleep(1)
        except AttributeError:
            Log.critical(self.logger, "Turn on Camera Effect Toggle Button failed, please keep the camera at the foreground.")
            raise SystemExit()
        return

    def windows_studio_effects_off(self):
        try:
            effects_wrapper = get_control_wrapper(self.app_windows, "CameraEffectToggleButton", "Effects")
            toggle_state = effects_wrapper.get_toggle_state()
            if toggle_state == 0:
                return
            pos=effects_wrapper.rectangle().mid_point()
        except AttributeError:
            Log.critical(self.logger, "Turn off Camera Effect Toggle Button failed, please keep the camera at the foreground.")
            raise SystemExit()
        pywinauto.mouse.click(button='left', coords=(pos.x, pos.y))
        sleep(1)
        return

    def mep_switch_init(self):
        wrapper_ctrl=get_control_wrapper(self.app_windows, "Switch", "Automatic framing")
        self.mep_ops['Automatic framing']=wrapper_ctrl

        wrapper_ctrl=get_control_wrapper(self.app_windows, "Switch", "Eye contact")
        self.mep_ops['Eye contact']=wrapper_ctrl

        wrapper_ctrl=get_control_wrapper(self.app_windows, "Switch", "Background effects")
        self.mep_ops['Background effects']=wrapper_ctrl

    def effect_switch(self, key, state, interval=0):
        try:
            if state == 1:
                # turn on
                if self.mep_ops[key].get_toggle_state() == 0:
                    self.mep_ops[key].toggle()
                if key == "Background effects":
                    try:
                        sleep(interval+1)
                        standard_blur_wrapper = get_control_wrapper(self.app_windows, "RadioButton", "Standard blur")
                        cur_state=standard_blur_wrapper.is_selected()
                        if cur_state == 1:
                            portrait_blur_wrapper = get_control_wrapper(self.app_windows, "RadioButton", "Portrait blur")
                            portrait_blur_wrapper.select()
                        else:
                            standard_blur_wrapper.select()
                    except:
                        Log.error(self.logger, "Blur switch failed")
                sleep(interval)
            if state == 0:
                # turn off
                if self.mep_ops[key].get_toggle_state() == 1:
                    self.mep_ops[key].toggle()
                sleep(interval)
        except AttributeError:
            Log.error(self.logger, "Effects switch failed, the {} toggle switch object is not initialized.".format(key))
        return

    def mep_af_on(self):
        effects_status = self.get_effects_status()
        if effects_status == 0:
            self.windows_studio_effects_on()

        self.mep_switch_init()
        self.effect_switch('Automatic framing', 1)
        return

    def mep_af_off(self):
        effects_status = self.get_effects_status()
        if effects_status == 0:
            self.windows_studio_effects_on()

        self.mep_switch_init()
        self.effect_switch('Automatic framing', 0)
        return

    def mep_ecc_on(self):
        effects_status = self.get_effects_status()
        if effects_status == 0:
            self.windows_studio_effects_on()

        self.mep_switch_init()
        self.effect_switch('Eye contact', 1)
        return

    def mep_ecc_off(self):
        effects_status = self.get_effects_status()
        if effects_status == 0:
            self.windows_studio_effects_on()

        self.mep_switch_init()
        self.effect_switch('Eye contact', 0)
        return

    def mep_blur_on(self):
        effects_status = self.get_effects_status()
        if effects_status == 0:
            self.windows_studio_effects_on()

        self.mep_switch_init()
        self.effect_switch('Background effects', 1)
        return

    def mep_blur_off(self):
        effects_status = self.get_effects_status()
        if effects_status == 0:
            self.windows_studio_effects_on()

        self.mep_switch_init()
        self.effect_switch('Background effects', 0)
        return

    def image_path(self, effect, status, idx, ratio_w, ratio_h):
        image_pos = self.win.rectangle()
        img_width = image_pos.width() - (48+96)
        img_height = round(img_width * ratio_h / ratio_w)

        img_x = 48
        # use take video button center to calculate the image height position.
        img_y = int(self.pos_center - img_height/2) - image_pos.top
        # print("camera image x pos is "+str(img_x))
        # print("camera image y pos is "+str(img_y))
        str_x = "%04d" % img_x
        str_y = "%04d" % img_y
        str_w = "%04d" % img_width
        str_h = "%04d" % img_height
        preview_str = str_x + '_' + str_y + '_'+ str_w + '_' + str_h
        str_res = effect.replace(' ','_') + '_' + status + '_' + str(idx) +'-'+ preview_str + '.png'
        # print(str_res)
        return str_res



    def mep_effects_on(self, cnt, effects_list, ratio_w=16, ratio_h=9, interval=1, path=None):
        effects_status = self.get_effects_status()
        if effects_status == 0:
            self.windows_studio_effects_on()

        self.mep_switch_init()
        for effect in effects_list:
            self.effect_switch(effect, 1)
            sleep(interval)
            if path:
                file = self.image_path(effect,'on', cnt, ratio_w, ratio_h)
                file_path = '{}\{}'.format(path,file)
                # print(file_path)
                Log.debug(self.logger, "Camera application captured file store at {}".format(file_path))
                self.capture_img(file_path)



    def mep_effects_off(self, cnt, effects_list, ratio_w=16, ratio_h=9, interval=1,path=None):
        effects_status = self.get_effects_status()
        if effects_status == 0:
            self.windows_studio_effects_on()

        self.mep_switch_init()
        for effect in effects_list:
            self.effect_switch(effect, 0)
            sleep(interval)
            if path:
                file = self.image_path(effect,'off', cnt, ratio_w, ratio_h)
                file_path = '{}\{}'.format(path,file)
                Log.debug(self.logger, "Camera application captured file store at {}".format(file_path))
                self.capture_img(file_path)

    def capture_img(self,path):
        try:
            pos = self.win.rectangle()
            # self.pos_center -  self.img_height
            # pos = self.get_camera_image()
            pyautogui.screenshot(path,region=(pos.left, pos.top, pos.width(), pos.height()))
        except:
            Log.warning(self.logger, "capture file failed")
        return






if __name__ == "__main__":
    # Run once at startup:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("my.func")
    for handler in logger.handlers:
        handler.setLevel('DEBUG')

    camera_mep=CameraOps("WindowsCamera")
    camera_mep.start_app()
    camera_mep.ret_mainview()

    camera_mep.video_recording(30)

    camera_mep.switch_to_video()
    
    camera_mep.windows_studio_effects_on()
    camera_mep.capture_img('123.png')
    camera_mep.windows_studio_effects_off()

    # camera_mep.mep_af_on()
    # camera_mep.mep_ecc_on()
    # camera_mep.mep_blur_on()

    # camera_mep.mep_af_off()
    # camera_mep.mep_ecc_off()
    # camera_mep.mep_blur_off()
    
    # effects_list = ['Automatic framing', 'Eye contact', 'Background effects']
    effects_list = ['Background effects']
    camera_mep.mep_effects_on(0, effects_list)
    camera_mep.mep_effects_off(0, effects_list)
    
    camera_mep.ret_mainview()
    camera_mep.camera_default_settings("Use system settings")
    camera_mep.camera_default_settings("Use custom in-app settings")
    camera_mep.get_video_resoulution()
    camera_mep.change_video_resoulution(0)
    camera_mep.change_video_resoulution(1)
    camera_mep.change_video_resoulution(2)
    camera_mep.change_video_resoulution(3)
    camera_mep.switch_to_photo()
    camera_mep.close_camera()