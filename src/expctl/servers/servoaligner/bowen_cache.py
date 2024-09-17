i2cbus = SMBus(1)
MCP3424_fiber=MCP342x.MCP342x(i2cbus, 0x68, device='MCP3424', channel=0, gain=1, resolution=12, continuous_mode=False, scale_factor=1.0, offset=0.0)
MCP3424_pinhole=MCP342x.MCP342x(i2cbus, 0x68, device='MCP3424', channel=1, gain=1, resolution=12, continuous_mode=False, scale_factor=1.0, offset=0.0)
MCP3424_ref=MCP342x.MCP342x(i2cbus, 0x68, device='MCP3424', channel=2, gain=1, resolution=12, continuous_mode=False, scale_factor=1.0, offset=0.0)


###
data_cache=[]
for i in range(100):
    data_cache.append(MCP3424_pinhole.convert_and_read())
    if i%100==0:
        print(i)
print('pinhole output:',np.mean(data_cache))

data_cache=[]
for i in range(100):
    data_cache.append(MCP3424_fiber.convert_and_read())
    if i%100==0:
        print(i)
print('fiber output:',np.mean(data_cache))

###
with np.load('/home/rydpi5/servomotor/Feetech-Servo-SDK-main/args20240809a.npz') as args_data:
    tl1_x_array=args_data['tl1_x_array']
    tl2_x_array=args_data['tl2_x_array']
    tl3_x_array=args_data['tl3_x_array']
    tl4_x_array=args_data['tl4_x_array']
    array_products=args_data['array_products']
    tl1_y_array=args_data['tl1_y_array']
    tl2_y_array=args_data['tl2_y_array']
    tl3_y_array=args_data['tl3_y_array']
    tl4_y_array=args_data['tl4_y_array']

print(array_products)
print(len(array_products))
print(tl1_x_array)
print(tl2_x_array)
print(tl3_x_array)
print(tl4_x_array)

print(tl1_y_array)
print(tl2_y_array)
print(tl3_y_array)
print(tl4_y_array)



##
data_saved=[]
dy0_saved=[]
dy1_saved=[]
tl1_y_n_saved=[]
tl1_x_n_saved=[]

filename='/home/rydpi5/servomotor/Feetech-Servo-SDK-main/test20240809a.npz'

for i in range(len(tl1_y_array)):
    dy0=array_products[i][0]
    dy1=array_products[i][1]
    tl1_y_n=array_products[i][2]
    tl1_x_n=array_products[i][3]
    #tl1_x_array[i], tl2_x_array[i],
    sync_angle_list=[tl1_x_array[i], tl2_x_array[i], tl1_y_array[i], tl2_y_array[i]]
    servos.set_angle(sync_angle_list)

    data_cache=[]
    for j in range(100):
        data_cache.append(MCP3424_pinhole.convert_and_read())
    data_saved.append(np.mean(data_cache))

    print('saving..., data is', np.mean(data_cache))
    dy0_saved.append(dy0)
    dy1_saved.append(dy1)
    tl1_y_n_saved.append(tl1_y_n)
    tl1_x_n_saved.append(tl1_x_n)
    np.savez(filename, data_saved=np.array(data_saved), dy0_saved=np.array(dy0_saved), dy1_saved=np.array(dy1_saved), tl1_y_n_saved=np.array(tl1_y_n_saved), tl1_x_n_saved=np.array(tl1_x_n_saved))

servos.home()


##
data_saved=[]
dy0_saved=[]
dy1_saved=[]
tl1_y_n_saved=[]
tl1_x_n_saved=[]

filename='/home/rydpi5/servomotor/Feetech-Servo-SDK-main/test20240809a.npz'

for i in range(len(tl1_y_array)):
    dy0=array_products[i][0]
    dy1=array_products[i][1]
    tl1_y_n=array_products[i][2]
    tl1_x_n=array_products[i][3]
    #tl1_x_array[i], tl2_x_array[i],
    sync_angle_list=[tl1_x_array[i], tl2_x_array[i], tl1_y_array[i], tl2_y_array[i]]
    servos.set_angle(sync_angle_list)

    data_cache=[]
    for j in range(100):
        data_cache.append(MCP3424_pinhole.convert_and_read())
    data_saved.append(np.mean(data_cache))

    print('saving..., data is', np.mean(data_cache))
    dy0_saved.append(dy0)
    dy1_saved.append(dy1)
    tl1_y_n_saved.append(tl1_y_n)
    tl1_x_n_saved.append(tl1_x_n)
    np.savez(filename, data_saved=np.array(data_saved), dy0_saved=np.array(dy0_saved), dy1_saved=np.array(dy1_saved), tl1_y_n_saved=np.array(tl1_y_n_saved), tl1_x_n_saved=np.array(tl1_x_n_saved))

servos.home()