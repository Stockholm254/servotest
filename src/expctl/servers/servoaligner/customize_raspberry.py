HOME_FOLDER                 = "/home/rydpi5/expctl/servers/servoaligner/"
DEVICENAME_LIST             = ['/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2']     # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
BAUDRATE                    = 115200          # SCServo default baudrate : 1000000
SERVO_SPEED = 2000
SERVO_ACC = 90
#
sts3032_dict={0:[1,'1x'], 1:[2,'1y'], 2:[3,'2x'], 3:[4,'2y'], 4:[5,'3x'], 5:[6,'3y'], 6:[7,'4x'],7:[8,'4y']} # dict {index:[ID, servo name]}