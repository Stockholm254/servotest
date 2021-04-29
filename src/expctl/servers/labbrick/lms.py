import ctypes
import tempfile
import os
import zipfile
import platform
import shutil
import logging
import inspect
# from typing import List, Dict


__all__ = ['download_LMS_binaries', 'VNX_LMS_API', 'LMSStatus']


def default_library_location():
    print(os.path.dirname(os.path.realpath(__file__)))
    return os.path.dirname(os.path.realpath(__file__)) + '\\vnx_fmsynth.dll'


class LMSStatus:
    """Helper class for inspecting answer of get_device_status"""
    def __init__(self, raw_status): # raw_status is int
        self._raw_status = raw_status

    def is_invalid(self):
        return bool(self._raw_status & VNX_LMS_API.INVALID_DEVID)

    def is_connected(self):
        return bool(self._raw_status & VNX_LMS_API.DEV_CONNECTED)

    def is_open(self):
        return bool(self._raw_status & VNX_LMS_API.DEV_OPENED)

    def is_sweeping(self):
        return bool(self._raw_status & VNX_LMS_API.SWP_ACTIVE)

    def is_sweeping_up(self):
        return bool(self._raw_status & VNX_LMS_API.SWP_UP)

    def is_repeating_sweep(self):
        return bool(self._raw_status & VNX_LMS_API.SWP_REPEAT)

    def is_sweeping_bidirectional(self):
        return bool(self._raw_status & VNX_LMS_API.SWP_BIDIRECTIONAL)

    def is_pll_locked(self):  # returns bool
        return bool(self._raw_status & VNX_LMS_API.PLL_LOCKED)

    def as_dict(self): # -> Dict[str, bool]:
        state_methods = [method for method in dir(self) if method.startswith('is_')]

        return {method: getattr(self, method)()
                for method in state_methods}

    def __repr__(self):
        # only show True flags
        return 'LMSState(%r)' % {key: value
                                 for key, value in self.as_dict().items()
                                 if value}


class VNX_LMS_API:
    """Wrapper for LabBrick Signal Generator API.
    All methods are explicit members for static type checking"""

    _default = None

    MAX_NUM_DEVICES = 64
    MAX_MODELNAME = 32

    MODE_RFON = 0x00000010  # bit is 1 for RF on, 0 if RF is off
    MODE_INTREF = 0x00000020  # bit is 1 for internal osc., 0 for external reference
    MODE_SWEEP = 0x0000000F  # bottom 4 bits are used to keep the sweep control bits

    STATUS_OK = 0
    BAD_PARAMETER = 0x80010000  # out of range input -- frequency outside min/max etc.
    BAD_HID_IO = 0x80020000
    DEVICE_NOT_READY = 0x80030000  # device isn't open, no handle, etc.
    F_INVALID_DEVID = -1.0  # for functions that return a float
    F_DEVICE_NOT_READY = -3.0

    INVALID_DEVID = 0x80000000  # MSB is set if the device ID is invalid
    DEV_CONNECTED = 0x00000001  # LSB is set if a device is connected
    DEV_OPENED = 0x00000002  # set if the device is opened
    SWP_ACTIVE = 0x00000004  # set if the device is sweeping
    SWP_UP = 0x00000008  # set if the device is sweeping up in frequency
    SWP_REPEAT = 0x00000010  # set if the device is in continuous sweep mode
    SWP_BIDIRECTIONAL = 0x00000020  # set if the device is in bi-directional sweep mode
    PLL_LOCKED = 0x00000040  # set if the PLL lock status is TRUE (both PLL's are locked)

    ERROR_BIT = 0x80000000

    DEVID = ctypes.c_uint
    DeviceIDArray = MAX_NUM_DEVICES * DEVID # TYPE? used to be DeviceIDArray: type= MAX_NUM_DEVICES*DEVID

    @classmethod
    def default(cls):
        if cls._default is None:
            cls._default = VNX_LMS_API()
        return cls._default

    def __init__(self, library=None):
        if library is None:
            library = ctypes.cdll.LoadLibrary(default_library_location())

        self._library = library

        self._library.fnLMS_SetTestMode.restype = None
        self._library.fnLMS_SetTestMode.argtypes = (ctypes.c_bool,)

        self._library.fnLMS_GetNumDevices.restype = int
        self._library.fnLMS_GetNumDevices.argtypes = ()

        self._library.fnLMS_GetDevInfo.restype = int
        self._library.fnLMS_GetDevInfo.argtypes = (self.DeviceIDArray,)

        if os.name == 'nt':
            self._get_model_name_char = self._library.fnLMS_GetModelNameA
        else:
            self._get_model_name_char = self._library.fnLMS_GetModelName
        self._get_model_name_char.restype = int
        self._get_model_name_char.argtypes = (self.DEVID, ctypes.c_char_p)
        self._get_model_name_char.errcheck = self.parse_int_answer

        self._library.fnLMS_InitDevice.restype = int
        self._library.fnLMS_InitDevice.argtypes = (self.DEVID,)
        self._library.fnLMS_InitDevice.errcheck = self.parse_int_answer

        self._library.fnLMS_CloseDevice.restype = int
        self._library.fnLMS_CloseDevice.argtypes = (self.DEVID,)
        self._library.fnLMS_CloseDevice.errcheck = self.parse_int_answer

        self._library.fnLMS_GetDLLVersion.restype = int
        self._library.fnLMS_GetDLLVersion.argtypes = ()
        self._library.fnLMS_GetDLLVersion.errcheck = self.parse_int_answer

        self._library.fnLMS_SetFrequency.restype = int
        self._library.fnLMS_SetFrequency.argtypes = (self.DEVID, ctypes.c_int)
        self._library.fnLMS_SetFrequency.errcheck = self.parse_int_answer

        self._library.fnLMS_SetStartFrequency.restype = int
        self._library.fnLMS_SetStartFrequency.argtypes = (self.DEVID, ctypes.c_int)
        self._library.fnLMS_SetStartFrequency.errcheck = self.parse_int_answer

        self._library.fnLMS_SetEndFrequency.restype = int
        self._library.fnLMS_SetEndFrequency.argtypes = (self.DEVID, ctypes.c_int)
        self._library.fnLMS_SetEndFrequency.errcheck = self.parse_int_answer

        self._library.fnLMS_SetPowerLevel.restype = int
        self._library.fnLMS_SetPowerLevel.argtypes = (self.DEVID, ctypes.c_int)
        self._library.fnLMS_SetPowerLevel.errcheck = self.parse_int_answer

        self._library.fnLMS_SetRFOn.restype = int
        self._library.fnLMS_SetRFOn.argtypes = (self.DEVID, ctypes.c_bool)
        self._library.fnLMS_SetRFOn.errcheck = self.parse_int_answer

        self._library.fnLMS_SetUseInternalRef.restype = int
        self._library.fnLMS_SetUseInternalRef.argtypes = (self.DEVID, ctypes.c_bool)
        self._library.fnLMS_SetUseInternalRef.errcheck = self.parse_int_answer

        self._library.fnLMS_SetSweepDirection.restype = int
        self._library.fnLMS_SetSweepDirection.argtypes = (self.DEVID, ctypes.c_bool)
        self._library.fnLMS_SetSweepDirection.errcheck = self.parse_int_answer

        self._library.fnLMS_SetUseExternalPulseMod.restype = int
        self._library.fnLMS_SetUseExternalPulseMod.argtypes = (self.DEVID, ctypes.c_bool)
        self._library.fnLMS_SetUseExternalPulseMod.errcheck = self.parse_int_answer

        self._library.fnLMS_SetSweepMode.restype = int
        self._library.fnLMS_SetSweepMode.argtypes = (self.DEVID, ctypes.c_bool)
        self._library.fnLMS_SetSweepMode.errcheck = self.parse_int_answer

        self._library.fnLMS_StartSweep.restype = int
        self._library.fnLMS_StartSweep.argtypes = (self.DEVID, ctypes.c_bool)
        self._library.fnLMS_StartSweep.errcheck = self.parse_int_answer

        self._library.fnLMS_SaveSettings.restype = int
        self._library.fnLMS_SaveSettings.argtypes = (self.DEVID,)
        self._library.fnLMS_SaveSettings.errcheck = self.parse_int_answer

        get_functions = ['fnLMS_GetSerialNumber',
                         'fnLMS_GetFrequency',
                         'fnLMS_GetPowerLevel',
                         'fnLMS_GetStartFrequency',
                         'fnLMS_GetEndFrequency',
                         'fnLMS_GetRF_On',
                         'fnLMS_GetUseInternalRef',
                         'fnLMS_GetMaxPwr',
                         'fnLMS_GetMinPwr',
                         'fnLMS_GetMaxFreq',
                         'fnLMS_GetMinFreq']

        # no return check
        self._library.fnLMS_GetDeviceStatus.restype = int
        self._library.fnLMS_GetDeviceStatus.argtypes = (self.DEVID,)

        for func_name in get_functions:
            func_ptr = getattr(self._library, func_name)
            func_ptr.restype = int
            func_ptr.argtypes = (self.DEVID,)
            func_ptr.errcheck = self.parse_int_answer

    def set_test_mode(self, test_mode): # -> None:
        self._library.fnLMS_SetTestMode(test_mode)

    def get_dll_version(self): # -> int:
        return self._library.fnLMS_GetDLLVersion()

    def get_num_devices(self): # -> int:
        return self._library.fnLMS_GetNumDevices()

    def get_dev_info(self): # -> List[int]:
        device_ids = (self.MAX_NUM_DEVICES * self.DEVID)()
        active_devices = self._library.fnLMS_GetDevInfo(device_ids)
        return list(device_ids[:active_devices])

    def get_model_name(self, device_id): # -> str:
        buffer = ctypes.create_string_buffer(self.MAX_MODELNAME)
        name_len = self._get_model_name_char(device_id, buffer)
        return buffer.value[:name_len].decode()

    def get_serial_number(self, device_id): # -> int:
        return self._library.fnLMS_GetSerialNumber(device_id)

    def init_device(self, device_id): # -> int:
        return self._library.fnLMS_InitDevice(device_id)

    def close_device(self, device_id): # -> int:
        return self._library.fnLMS_CloseDevice(device_id)

    def start_sweep(self, device_id, go): # -> int:
        return self._library.fnLMS_StartSweep(device_id, go)

    def save_settings(self, device_id): # -> int:
        return self._library.fnLMS_SaveSettings(device_id)

    # get / set methods
    def set_frequency(self, device_id, frequency): # -> int:
        return self._library.fnLMS_SetFrequency(device_id, frequency)

    def get_frequency(self, device_id): # -> int:
        return self._library.fnLMS_GetFrequency(device_id)

    def set_power_level(self, device_id, power_level): # -> int:
        return self._library.fnLMS_SetPowerLevel(device_id, power_level)

    def get_power_level(self, device_id): # -> int:
        # fnLMS_GetPowerLevel returns something strange
        return self._library.fnLMS_GetPowerLevel(device_id)

    def set_rf_on(self, device_id, rf_on): # -> int:
        return self._library.fnLMS_SetRFOn(device_id, rf_on)

    def get_rf_on(self, device_id): # -> int:
        return self._library.fnLMS_GetRF_On(device_id)

    def set_start_frequency(self, device_id, start_frequency): # -> int:
        return self._library.fnLMS_SetStartFrequency(device_id, start_frequency)

    def get_start_frequency(self, device_id): # -> int:
        return self._library.fnLMS_GetStartFrequency(device_id)

    def set_end_frequency(self, device_id, end_frequency): # -> int:
        return self._library.fnLMS_SetEndFrequency(device_id, end_frequency)

    def get_end_frequency(self, device_id): # -> int:
        return self._library.fnLMS_GetEndFrequency(device_id)

    def set_use_internal_ref(self, device_id, use_internal): # -> int:
        return self._library.fnLMS_SetUseInternalRef(device_id, use_internal)

    def get_use_internal_ref(self, device_id): # -> int:
        return self._library.fnLMS_GetUseInternalRef(device_id)

    # set only
    def set_sweep_direction(self, device_id, sweep_direction): # -> int:
        return self._library.fnLMS_SetSweepDirection(device_id, sweep_direction)

    def set_sweep_mode(self, device_id, sweep_mode): # -> int:
        return self._library.fnLMS_SetSweepMode(device_id, sweep_mode)

    def set_external_pulse_mod(self, device_id, external): # -> int:
        return self._library.fnLMS_SetUseExternalPulseMod(device_id, external)
        

    # get constants
    def get_min_pwr(self, device_id): # -> int:
        return self._library.fnLMS_GetMinPwr(device_id)

    def get_max_pwr(self, device_id): # -> int:
        return self._library.fnLMS_GetMaxPwr(device_id)

    def get_min_freq(self, device_id): # -> int:
        return self._library.fnLMS_GetMinFreq(device_id)

    def get_max_freq(self, device_id): # -> int:
        return self._library.fnLMS_GetMaxFreq(device_id)

    def get_device_status(self, device_id): # -> int:
        return self._library.fnLMS_GetDeviceStatus(device_id)

    @classmethod
    def parse_int_answer(cls, answer, func, arguments): # -> int:
        if answer <= ctypes.c_int(cls.DEVICE_NOT_READY).value:
            raise ValueError("Error executing %s" % func.__name__, answer, arguments)
        return answer