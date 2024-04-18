import pywinauto
import pyautogui
from pywinauto.application import Application
from time import sleep
from utils import getSettingsPath, get_control_wrapper
from mylog import *

class SettingCamOps:
    def __init__(self, app_name):
        self.app_name = app_name
        self.app_path = getSettingsPath(app_name)
        self.app_windows = None
        self.app_win = None
        self.preview_pos = None
        self.mep_ops = {}
        self.logger = logging.getLogger("my.func")


    def start_app(self):
        app_ret=Application(backend="uia").start(self.app_path, timeout=2, wait_for_idle=False)
        if app_ret.is_process_running()==True:
            app = Application(backend="uia").connect(title="Settings", timeout=5)
            sleep(2)
            if app.process is None:
                Log.error(self.logger, "OS setting connect failed, retry connect after 10 second")
                sleep(10)
                app_retry = Application(backend="uia").connect(title="Settings", timeout=5)
                if app_retry.process is None:
                    Log.critical(self.logger, "OS setting retry connected failed, exit")
                    raise SystemExit()
                else:
                    Log.debug(self.logger, "OS setting retry start successfully")
                    Log.debug(self.logger, "OS setting process id is {}".format(app_retry.process))
                    self.app_windows  = app_retry.windows()
                    self.win = app_retry.window(title="Settings")
            else:
                Log.debug(self.logger, "OS setting start successfully")
                Log.debug(self.logger, "OS setting process id is {}".format(app.process))
                self.app_windows  = app.windows()
                self.app_win      = app.window(title="Settings")

    def enter_camera_settings(self):
        try:
            camera_top = self.app_win.child_window(auto_id="SystemSettings_Camera_DeviceList_ListView", control_type="List")
            # camera_top.print_control_identifiers()
            cam_win = camera_top.child_window(auto_id="EntityItemButton", control_type="Button")
            cam_win.wrapper_object().click()
            sleep(2)
            # self.app_win.print_control_identifiers()
            # sleep(2)
            cam_preview = self.app_win.child_window(auto_id="pageContent", control_type="Group")
            self.preview_pos = cam_preview.rectangle()
            # print(pos)
            sleep(1)
        except AttributeError:
            Log.critical(self.logger, "Enter OS camera setting failed, only support 1 integrated camera")
            raise SystemExit()

    def expand_effects(self):
        try:
            # effects_top = self.app_win.child_window(title="Windows Studio Effects", control_type="Group")
            # effects_top.print_control_identifiers()
            all_setting_wrapper = get_control_wrapper(self.app_windows, "Button", "Show")
            # print(all_setting_wrapper.get_properties())
            if all_setting_wrapper.is_collapsed() == True:
                all_setting_wrapper.expand()
                sleep(1)
            if len(self.mep_ops) == 0:
                self.mep_switch_init()
        except AttributeError:
            Log.critical(self.logger, "Windows Studio Effects is not available, please check the MEP installation")
            raise SystemExit()

    def get_back_button(self):
        back_wrapper = get_control_wrapper(self.app_windows, match_class="NavigationViewBackButton", match_text="Back")
        return back_wrapper

    def maximize_restore_settings(self):
        try:
            max_wrapper = get_control_wrapper(self.app_windows, match_class="Maximize", match_text="Settings")
            max_wrapper.click()
            sleep(1)
        except:
            Log.warning(self.logger, "Max or restore OS Camera Setting failed.")

    def minimize_restore_settings(self):
        try:
            min_wrapper = get_control_wrapper(self.app_windows, match_class="Minimize", match_text="Settings")
            min_wrapper.click()
            sleep(1)
        except:
            Log.warning(self.logger, "Min OS Camera Setting failed.")

    def close_settings(self):
        try:
            close_wrapper = get_control_wrapper(self.app_windows, match_class="Close", match_text="Settings")
            close_wrapper.click()
            sleep(1)
        except:
            Log.warning(self.logger, "Close OS Camera Setting failed.")

    def mep_switch_init(self):
        wrapper_ctrl=get_control_wrapper(self.app_windows, "Switch", "Automatic framing")
        self.mep_ops['Automatic framing']=wrapper_ctrl

        wrapper_ctrl=get_control_wrapper(self.app_windows, "Switch", "Eye contact")
        self.mep_ops['Eye contact']=wrapper_ctrl

        wrapper_ctrl=get_control_wrapper(self.app_windows, "Switch", "Background effects")
        self.mep_ops['Background effects']=wrapper_ctrl

    def effect_switch(self, key, state, interval=2):
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
        except:
            Log.critical(self.logger, "Effects switch failed, the OS Setting {} toggle switch object is not initialized.".format(key))

    def mep_af_on(self):
        self.expand_effects()
        self.effect_switch('Automatic framing', 1)

    def mep_af_off(self):
        self.expand_effects()
        self.effect_switch('Automatic framing', 0)

    def mep_ecc_on(self):
        self.expand_effects()
        self.effect_switch('Eye contact', 1)

    def mep_ecc_off(self):
        self.expand_effects()
        self.effect_switch('Eye contact', 0)

    def mep_blur_on(self):
        self.expand_effects()
        self.effect_switch('Background effects', 1)

    def mep_blur_off(self):
        self.expand_effects()
        self.effect_switch('Background effects', 0)

    def image_path(self, effect, status, idx):
        cam_image = self.app_win.child_window(auto_id="SystemSettings_Camera_PreviewElement_CameraPreview", control_type="Group")
        image_pos = cam_image.rectangle()
        img_width = image_pos.width()
        img_height = image_pos.height()

        img_x = image_pos.left - self.preview_pos.left
        img_y = image_pos.top - self.preview_pos.top

        str_x = "%04d" % img_x
        str_y = "%04d" % img_y
        str_w = "%04d" % img_width
        str_h = "%04d" % img_height

        preview_str = str_x + '_' + str_y + '_'+ str_w + '_' + str_h
        str_res = effect.replace(' ','_') + '_' + status + '_' + str(idx) + '-' + preview_str +'.png'
        # print(str_res)
        return str_res



    def mep_effects_on(self, cnt, effects_list, interval=1, path=None):
        self.expand_effects()
        for effect in effects_list:
            self.effect_switch(effect, 1)
            sleep(interval)
            if path:
                file = self.image_path(effect,'on', cnt)
                file_path = '{}\{}'.format(path,file)
                Log.debug(self.logger, "OS Setting captured file store at {}".format(file_path))
                self.capture_img(file_path)



    def mep_effects_off(self, cnt, effects_list, interval=1,path=None):
        self.expand_effects()
        for effect in effects_list:
            self.effect_switch(effect, 0)
            sleep(interval)
            if path:
                file = self.image_path(effect,'off', cnt)
                file_path = '{}\{}'.format(path,file)
                Log.debug(self.logger, "OS Setting captured file store at {}".format(file_path))
                self.capture_img(file_path)

    def capture_img(self,path):
        try:
            pos = self.preview_pos
            pyautogui.screenshot(path,region=(pos.left, pos.top, (pos.right-pos.left), (pos.bottom-pos.top)))
        except:
            Log.warning(self.logger, "OS Setting capture file failed")
        return


if __name__ == "__main__":
    # Run once at startup:
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("my.func")
    for handler in logger.handlers:
        handler.setLevel('DEBUG')
    settings_mep=SettingCamOps("ms-settings:camera")
    settings_mep.start_app()
    settings_mep.enter_camera_settings()
    # back = settings_mep.get_back_button()
    # back.click()
    settings_mep.mep_af_on()
    settings_mep.mep_af_off()
    settings_mep.mep_ecc_on()
    settings_mep.mep_ecc_off()
    settings_mep.mep_blur_on()
    settings_mep.mep_blur_off()

    effects_list = ['Automatic framing', 'Eye contact', 'Background effects']
    # effects_list = ['Background effects']
    settings_mep.mep_effects_on(0, effects_list)
    settings_mep.mep_effects_off(0, effects_list)

    sleep(2)