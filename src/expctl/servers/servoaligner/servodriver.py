import os
import numpy as np
import matplotlib.pyplot as plt
import time
from smbus2 import SMBus,i2c_msg
from .scservo_sdk import *                    # Uses SCServo SDK library
import MCP342x

import json
from pathlib import Path
import atexit

# Control table address
ADDR_SCS_TORQUE_ENABLE     = 40
ADDR_SCS_GOAL_ACC          = 41
ADDR_SCS_GOAL_POSITION     = 42
ADDR_SCS_GOAL_SPEED        = 46
ADDR_SCS_PRESENT_POSITION  = 56
ADDR_SCS_MOVING_STATUS = 66

# Default setting
BAUDRATE                    = 115200           # SCServo default baudrate : 1000000
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
# dmesg | grep tty
protocol_end                = 0           # SCServo bit end(STS/SMS=0, SCS=1)

sts3032_dict={0:[2,'1x'], 1:[1,'1y'], 2:[4,'2x'], 3:[3,'2y'], 4:[4,'3x'], 5:[3,'3y'], 6:[2,'4x'],7:[1,'4y']} # dict {index:[ID, servo name]}
class sts3032:

    def __init__(self, channel, portHandler, packetHandler):
        self.portHandler=portHandler
        self.packetHandler=packetHandler
        self.SCS_ID=sts3032_dict[channel][0]
        self.turn_num = 0
        self.SCS_MOVING_SPEED = 1500          # SCServo moving speed
        self.SCS_MOVING_ACC   = 50          # SCServo moving acc
        self.raw_angle_current = 0
        self.message='Servo '+sts3032_dict[channel][1]+': '
        #atexit.register(self.home)
        # Write SCServo acc
        scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_GOAL_ACC, self.SCS_MOVING_ACC)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

        print(self.message+'SCServo acc set!')
        # Write SCServo speed
        scs_comm_result, scs_error = self.packetHandler.write2ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_GOAL_SPEED, self.SCS_MOVING_SPEED)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))
        print(self.message+'SCServo speed set!')

    def set_zero(self):
        #Set Zeros
        scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_TORQUE_ENABLE, 128)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))
        self.turn_num = 0
        self.angle_current = 2048
        try:
            scs_present_position_speed, scs_comm_result, scs_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_PRESENT_POSITION)
            if scs_comm_result != COMM_SUCCESS:
                print(self.message+'result',self.packetHandler.getTxRxResult(scs_comm_result))
            elif scs_error != 0:
                print(self.message+'error',self.packetHandler.getRxPacketError(scs_error))
            print(self.message+'SCServo zero set!')
            return 0
        except:
            print(self.message+'Read not sucessful!')
            return 1

    def set_speed(self, set_speed):
        # Write SCServo speed
        self.SCS_MOVING_SPEED=set_speed
        scs_comm_result, scs_error = self.packetHandler.write2ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_GOAL_SPEED, self.SCS_MOVING_SPEED)
        if scs_comm_result != COMM_SUCCESS:
            print(self.message+"%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(self.message+"%s" % self.packetHandler.getRxPacketError(scs_error))
        print(self.message+'SCServo speed set!')
        
    def set_angle(self, goal_position):

        if goal_position>=0:
            val=0b0000000000000000|abs(goal_position)
            scs_goal_position=val
        elif goal_position<0:
            val=0b1000000000000000|abs(goal_position)
            scs_goal_position=val

        #pre-read
        scs_present_position_speed, scs_comm_result, scs_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_PRESENT_POSITION)
        if scs_comm_result != COMM_SUCCESS:
            print(self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(self.packetHandler.getRxPacketError(scs_error))
        self.raw_angle_current = SCS_LOWORD(scs_present_position_speed)

        # Write SCServo goal position
        scs_comm_result, scs_error = self.packetHandler.write2ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_GOAL_POSITION, scs_goal_position)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

        i=0
        while i<5000:
            # Read SCServo present position 
            scs_present_position_speed, scs_comm_result, scs_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_PRESENT_POSITION)
            if scs_comm_result != COMM_SUCCESS:
                print(self.packetHandler.getTxRxResult(scs_comm_result))
            elif scs_error != 0:
                print(self.packetHandler.getRxPacketError(scs_error))
            # Read SCServo present status
            scs_present_status, scs_comm_result, scs_error = self.packetHandler.read4ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_MOVING_STATUS)
            if scs_comm_result != COMM_SUCCESS:
                print(self.packetHandler.getTxRxResult(scs_comm_result))
            elif scs_error != 0:
                print(self.packetHandler.getRxPacketError(scs_error))
            scs_present_position = SCS_LOWORD(scs_present_position_speed)
            if abs(scs_present_position-self.raw_angle_current)>3500:
                self.turn_num=self.turn_num+int(np.sign(self.raw_angle_current-scs_present_position))
            self.raw_angle_current=scs_present_position
            self.angle_current=scs_present_position+4096*self.turn_num

            scs_present_status=scs_present_status&0x0001
            if i%10==0:
                print(i,scs_present_status,self.raw_angle_current, self.angle_current, goal_position)
            i=i+1

            if (abs(goal_position - self.angle_current) ==0) and (scs_present_status==0):
                print(i,scs_present_status,self.raw_angle_current, self.angle_current, goal_position)
                break
    
    def home(self):
        self.set_angle(2048)

    def torque_disable(self):
        scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_TORQUE_ENABLE, 0)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

    def torque_enable(self):
        scs_comm_result, scs_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.SCS_ID, ADDR_SCS_TORQUE_ENABLE, 1)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(scs_error))

#A bigger Class that contains all the motors, should try to initialize the port connection as well in init of this class
class Servoset:
    def __init__(self):
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.portHandler = PortHandler(DEVICENAME)
        self.portHandler.setPacketTimeoutMillis(100)
        # Initialize self.packetHandler instance
        # Get methods and members of Protocol
        self.packetHandler = PacketHandler(protocol_end)

        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()

        servo_1x=sts3032(0, self.portHandler, self.packetHandler)
        servo_1y=sts3032(1, self.portHandler, self.packetHandler)
        servo_2x=sts3032(2, self.portHandler, self.packetHandler)
        servo_2y=sts3032(3, self.portHandler, self.packetHandler)

        servo_1x.set_speed(1000)
        servo_2x.set_speed(1000)
        servo_1y.set_speed(1000)
        servo_2y.set_speed(1000)

        servo_1x.torque_enable()
        servo_2x.torque_enable()
        servo_1y.torque_enable()
        servo_2y.torque_enable()

        self.servo_list=[servo_1x, servo_2x, servo_1y, servo_2y]

        self.SCS_ID_list=[]
        for servo in self.servo_list:
            self.SCS_ID_list.append(servo.SCS_ID)
        #initialize turn numbers
        self.turn_num=list(np.zeros(len(self.SCS_ID_list)))
        self.file = Path(f"/home/rydpiservo/expctl/src/expctl/servers/servoaligner/servos.json")
        if self.file.exists():  # load existing data
            print("loading position from disk")
            self.load()

        # make sure the current position gets saved to disk when the programm exits
        atexit.register(self.save)

    def save(self):
        # persist encoder position to file when programm is closed
        dct = {'turns': self.turn_num, 'angles': self.multi_position_list, 'angles_deg': list((np.array(self.multi_position_list)+np.array(self.turn_num)*4096-2048)*360/4096)}
        self.file.write_text(json.dumps(dct))
        # with self.file.open("a") as f:
        #     f.write(json.dumps(dct))

    def load(self):
        # load position from file
        dct = json.loads(self.file.read_text())
        self.turn_num = dct['turns']
        self.multi_position_list = dct['angles']
        message="Loaded, the angles are: \n"
        for i in range(len(self.turn_num)):
            message+=self.servo_list[i].message
            message+=str((self.multi_position_list[i]+self.turn_num[i]*4096-2048)*360/4096)+' deg\t'
        print(message)
    # def __del__(self):
    #     # also save when object is destroyed
    #     self.save()

    def set_zero(self):
        for servo in self.servo_list:
            iteration=1
            while 1:
                print('Set Zero Trail ',iteration)
                result=servo.set_zero()
                if result==0:
                    break
                iteration+=1
        #Set turn number to be zero when we set zero on all the motors.
        self.turn_num=list(np.zeros(len(self.SCS_ID_list)))
        self.save()


    def torques_enable(self):
        for servo in self.servo_list:
            servo.torque_enable()

    def torques_disable(self):
        for servo in self.servo_list:
            servo.torque_disable()

    def home(self):
        goal_position_list=[]
        for i in range(len(self.SCS_ID_list)):
            goal_position_list.append(2048)
        self.set_angle(goal_position_list)

    def set_angle(self, goal_position_list):

        ADDR_STS_GOAL_ACC          = 41
        ADDR_STS_GOAL_POSITION     = 42
        ADDR_STS_GOAL_SPEED        = 46
        ADDR_STS_PRESENT_POSITION  = 56

        scs_goal_position=[]
        for goal_position in goal_position_list:
            if goal_position>=0:
                val=0b0000000000000000|abs(goal_position)
                scs_goal_position.append(val)
            elif goal_position<0:
                val=0b1000000000000000|abs(goal_position)
                scs_goal_position.append(val)

        SCS_MOVING_STATUS_THRESHOLD = 0               # SCServo moving status threshold
        protocol_end                = 0                 # SCServo bit end(STS/SMS=0, SCS=1)

        # Initialize GroupSyncWrite instance
        groupSyncWrite = GroupSyncWrite(self.portHandler, self.packetHandler, ADDR_STS_GOAL_POSITION, 2)

        # Initialize GroupSyncRead instace for Present Position
        groupSyncRead = GroupSyncRead(self.portHandler, self.packetHandler, ADDR_STS_PRESENT_POSITION, 4)

        # Add parameter storage for SCServo present position value
        for SCS_ID in self.SCS_ID_list:
            scs_addparam_result = groupSyncRead.addParam(SCS_ID)
            if scs_addparam_result != True:
                print("[ID:%03d] groupSyncRead addparam failed" % SCS_ID)
                quit()

        # Allocate goal position value into byte array
        # Add SCServo goal position values to the Syncwrite parameter storage
        index=0
        for SCS_ID in self.SCS_ID_list:
            param_goal_position = [SCS_LOBYTE(scs_goal_position[index]), SCS_HIBYTE(scs_goal_position[index])]
            scs_addparam_result = groupSyncWrite.addParam(SCS_ID, param_goal_position)
            index+=1
            if scs_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % SCS_ID)
                quit()

        # Syncwrite goal position
        scs_comm_result = groupSyncWrite.txPacket()
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))

        # Clear syncwrite parameter storage
        groupSyncWrite.clearParam()

        #Pre-read
        scs_comm_result = groupSyncRead.txRxPacket()
        if scs_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))

        scs_present_position_speed = []

        for SCS_ID in self.SCS_ID_list:
            scs_getdata_result = groupSyncRead.isAvailable(SCS_ID, ADDR_STS_PRESENT_POSITION, 4)
            if scs_getdata_result == True:
                scs_present_position_speed.append(groupSyncRead.getData(SCS_ID, ADDR_STS_PRESENT_POSITION, 4))
            else:
                print("[ID:%03d] groupSyncRead getdata failed" % SCS_ID)
                scs_present_position_speed.append(0)

        status_string='Start Position: '+'\t'
        scs_present_position_list=[]

        index=0
        for SCS_ID in self.SCS_ID_list:
            scs_present_position = SCS_LOWORD(scs_present_position_speed[index])
            scs_present_position_list.append(scs_present_position)
            index+=1

        self.multi_position_list=[]
        for index in range(len(self.SCS_ID_list)): 
            self.multi_position_list.append(int(scs_present_position_list[index]+self.turn_num[index]*4096))
            status_string+='[ID:'+f'{self.SCS_ID_list[index]:03d}'+'] Goal:'+f'{goal_position_list[index]:03d}'+' Pres:'+f'{self.multi_position_list[index]:03d}'+'\t'

        scs_present_position_list_cache=scs_present_position_list.copy()
        print(status_string)

        iteration=0
        while iteration<2000:
            # Syncread present single turn position
            scs_comm_result = groupSyncRead.txRxPacket()
            if scs_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))

            scs_present_position_speed = []

            for SCS_ID in self.SCS_ID_list:
                # Check if groupsyncread data of SCServo is available
                scs_getdata_result = groupSyncRead.isAvailable(SCS_ID, ADDR_STS_PRESENT_POSITION, 4)
                if scs_getdata_result == True:
                    # Get SCServo#1 present position value
                    scs_present_position_speed.append(groupSyncRead.getData(SCS_ID, ADDR_STS_PRESENT_POSITION, 4))
                else:
                    print("[ID:%03d] groupSyncRead getdata failed" % SCS_ID)
                    scs_present_position_speed.append(0)
            
            status_string='Iteration: '+str(iteration)+'\t'
            # Printing current status
            scs_present_position_list=[]

            index=0
            for SCS_ID in self.SCS_ID_list:
                scs_present_position = SCS_LOWORD(scs_present_position_speed[index])
                scs_present_position_list.append(scs_present_position)
                index+=1

            self.multi_position_list=[]
            #determine whether turn number has been changed
            for index in range(len(self.SCS_ID_list)): 
                if abs(scs_present_position_list[index]-scs_present_position_list_cache[index])>3500:
                    if scs_present_position_list[index]-scs_present_position_list_cache[index]>0:
                        self.turn_num[index]=self.turn_num[index]-1
                    elif scs_present_position_list[index]-scs_present_position_list_cache[index]<0:
                        self.turn_num[index]=self.turn_num[index]+1

                self.multi_position_list.append(int(scs_present_position_list[index]+self.turn_num[index]*4096))

                status_string+='[ID:'+f'{self.SCS_ID_list[index]:03d}'+'] Goal:'+f'{goal_position_list[index]:03d}'+' Pres:'+f'{self.multi_position_list[index]:03d}'+'\t'

            scs_present_position_list_cache=scs_present_position_list.copy()

            if iteration%100==0:
                print(status_string)
            
            #count how many motors have finished moving
            is_done=0
            for i in range(len(self.SCS_ID_list)): 
                if abs(goal_position_list[i] - self.multi_position_list[i]) == SCS_MOVING_STATUS_THRESHOLD:
                    is_done+=1

            if is_done==len(self.SCS_ID_list):
                print(status_string)
                break

            iteration+=1
        self.save()
        # Clear syncread parameter storage
        groupSyncRead.clearParam()

    def close(self):
        # Close port
        self.portHandler.closePort()