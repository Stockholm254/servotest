#mirror spacing
x1 = 0.155
x2 = 0.27
x3 = 0.14
x4 = 0.15
#lens spacing
dy0 = 0.35
dy1 = 0.16
#focal length
fl1 = 0.1925
fl2 = 0.15
fl3 = 1
#MOT and Cavity
MOT_pos_1=2e-4
Cav_pos_1=0

MOT_pos_2=2e-4
Cav_pos_2=0

MOT_pos_rel = 0.2
MOT_Cav_dist = -0.044

params={'x1':x1, 'x2':x2, 'x3': x3, 'x4':x4, 'dy0':dy0, 'dy1':dy1, 'fl1': fl1, 'fl2': fl2, 'fl3': fl3, 'MOT_pos_rel': MOT_pos_rel, 'MOT_Cav_dist': MOT_Cav_dist, 'MOT_pos_1': MOT_pos_1, 'Cav_pos_1': Cav_pos_1, 'MOT_pos_2': MOT_pos_2, 'Cav_pos_2': Cav_pos_2}

servos_dict={'servo_1x':0, 'servo_1y':1, 'servo_2x':2, 'servo_2y':3, 'servo_3x':4, 'servo_3y':5, 'servo_4x':6, 'servo_4y':7}