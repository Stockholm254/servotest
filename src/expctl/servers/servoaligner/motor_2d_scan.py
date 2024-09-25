import numpy as np
import tqdm
import matplotlib.pyplot as plt
import logging
from servo_util import create_zigzag_X, r2nd

def motor_2d_scan(N_pts, scan_range, servos, callback_func):
    # create the grid
    Xs = np.linspace(-scan_range,scan_range,N_pts)
    Ys = np.linspace(-scan_range,scan_range,N_pts)
    X,Y = np.meshgrid(Xs,Ys)
    Z = np.zeros_like(X)
    X_zig, index_map = create_zigzag_X(X)
    dX = Xs[1]-Xs[0]
    servos.set_precision(dX)
    #
    z0 = callback_func([0,0])
    logging.info(f"z0: {z0}")

    #
    try:
        with tqdm.tqdm(total=len(Xs)*len(Ys)) as pbar:
            for i in range(len(Xs)):
                for j in range(len(Ys)):
                    x,y = X_zig[i,j], Y[i,j]
                    idx = index_map[i,j] # original index of X
                    idx_i, idx_j = np.unravel_index(idx, X.shape) # r[idx_i, idx_j] == r_zig[i,j]
                    #
                    # goal_position_list  = r2nd([x,y],pos_mask)
                    # servos.set_angle(goal_position_list)
                    # z = measurement()
                    #
                    para,z = callback_func(para=[x,y])
                    Z[idx_i,idx_j] = z
                    pbar.update(1)

    except Exception as e:
        servos.close()
        logging.error(f"Error in motor_2d_scan: {e}")
    finally:
        servos.home()
        servos.set_precision(1)
    #
    plt.matshow(Z)
    plt.contourf(X,Y,Z)
    plt.colorbar()
    print(np.max(Z))
    print(np.min(Z))
    # plt.show()
    return X,Y,Z