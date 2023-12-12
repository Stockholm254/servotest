from ctypes import (
    c_int,
    c_char_p,
    c_double,
    c_long,
    c_float,
    byref,
)
import sys 
from time import time, sleep
from thorlabs_kinesis import KCube_DC_Servo as kdc
from thorlabs_kinesis.KCube_DC_Servo import LinearRange, RotationalUnlimited, RotationalWrapping, Quickest, Forwards, Reverse


class Kinesis:
    def __init__(self, serial: str, milliseconds=100) -> None:
        self.serial_no = c_char_p(bytes(serial, "utf-8"))
        self.milliseconds = c_int(milliseconds)
        self.pos_prev = None

        err = kdc.CC_Open(self.serial_no)
        if err == 0:
            print("Starting polling")
            kdc.CC_StartPolling(self.serial_no, self.milliseconds )
            print("Clearing message queue ")
            kdc.CC_ClearMessageQueue(self.serial_no)
            sleep(0.2)
            CanMoveWithoutHomingFirst = kdc.CC_CanMoveWithoutHomingFirst(self.serial_no)
            print("CanMoveWithoutHomingFirst :", CanMoveWithoutHomingFirst)
            if not CanMoveWithoutHomingFirst:
                raise RuntimeError("The stage is not homed! Please home with Thorlabs Kinesis Software!")

            # Set motor parameters to convert from degrees to device units
            err = kdc.CC_SetMotorParamsExt(self.serial_no, c_double(512), c_double(67), c_double(17.87)) #StepsPerRev, GearboxRatio, Pitch
            print(f"error status 1: {err}")
            err = kdc.CC_SetRotationModes(self.serial_no, RotationalUnlimited, Quickest) #MOT_MovementModes, MOT_MovementDirections
            print(f"error status 2: {err}")

            initial_pos = self.getPosition()
            self.pos_prev = initial_pos
            print(f"initial position: {initial_pos}")

        


    def close(self):
        kdc.CC_StopPolling(self.serial_no)
        kdc.CC_Close(self.serial_no)

    def __del__(self):
        self.close()

    def getPosition(self, real=True):
        # Get the stage position in device units and convert to real units if real=True

        # Read current position
        pos = int(kdc.CC_GetPosition(self.serial_no))
        if real:
            degrees = c_double(0)
            err = kdc.CC_GetRealValueFromDeviceUnit(self.serial_no, c_int(pos), byref(degrees), c_int(0))
            if err != 0:
                raise RuntimeError(f"Could not read stage position, error code {err}")
            return degrees.value
        else:
            return pos

    def moveToPosition(self, pos, *args, **kwargs):

        #only move if the position sent changes to avoid overhead
        if (self.pos_prev == pos):
            print("already here!")
        elif (self.pos_prev is None) or (self.pos_prev != pos):
            self.pos_prev = pos
            self._moveToPosition(pos, *args, **kwargs)
    

    def _moveToPosition(self, pos, real=True, eps=2):
        # Set the position of the stage in degrees if real=True otherwise device units

        if real==True:
            degrees_to = c_double(pos)
            move_to = c_int(0)
            err = kdc.CC_GetDeviceUnitFromRealValue(self.serial_no, degrees_to, byref(move_to), c_int(0))
            if err != 0:
                raise RuntimeError(f"Could not convert position, error code {err}")
            print(f"Moving to: {move_to.value} device units ~~ {degrees_to.value} degree ")
        else:
            move_to = c_int(pos)


        t0 = time()
        kdc.CC_SetMoveAbsolutePosition(self.serial_no, move_to)
        kdc.CC_MoveAbsolute(self.serial_no)
        sleep(0.1)
        pos = int(kdc.CC_GetPosition(self.serial_no))
        print(f"Current pos: {pos}")
        while abs(pos-move_to.value)>eps:
            pos = int(kdc.CC_GetPosition(self.serial_no))
            sleep(0.25)
            tmoving = time() - t0
            print(f"Current pos: {pos} moving for {tmoving:.1f} s")
            if tmoving > 8.0:
                print("WARNING move took too long, angle might not be correct!")
                break
        t1 = time()
        print(f"Move to {move_to.value} ({pos}) completed in {(t1-t0)} s")
        

if __name__ == "__main__":
    k = Kinesis(serial="27501301")
    
    err = kdc.CC_ResetRotationModes(k.serial_no)
    pos = k.getPosition()
    print(f"Stage is at position {pos}")
    err = kdc.CC_SetRotationModes(k.serial_no, RotationalUnlimited, Quickest) #MOT_MovementModes, MOT_MovementDirections
    print(f"error status 2: {err}")
    pos = k.getPosition()
    print(f"Stage is at position {pos}")
    newPos = 0.5
    k.moveToPosition(newPos, eps=15)
    pos = k.getPosition()
    print(f"Stage is now at position {pos}")


    # for i in range(4):
    #     pos = k.getPosition()
    #     print(f"Stage is at position {pos}")
    #     k.moveToPosition(pos+0.5, eps=i)
    #     sleep(0.2)
    # k.close()




