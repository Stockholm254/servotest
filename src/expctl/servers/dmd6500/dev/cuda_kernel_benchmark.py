import numpy as np
from cuda import cudart
import cupy as cp
import cupyx
import time
from cupyx.profiler import time_range

from cuda_gl import *
from cuda_kernels_lg import laguerre_cuda, hologram_cuda

def merge_white(image, out):

    w = (image*255).astype(cp.uint8)
    out[:,:,0] = w
    out[:,:,1] = w
    out[:,:,2] = w
    out[:,:,3] = 1
    
def merge_rgb(r, g, b, out):

    out[:,:,0] = (r*255).astype(cp.uint8)
    out[:,:,1] = (g*255).astype(cp.uint8)
    out[:,:,2] = (b*255).astype(cp.uint8)
    out[:,:,3] = 1
    

def main(fullscreen=True):


    width = 1920
    height = 1080

    scale = 1.0  # Scale factor for coordinates
    theta = 0  # Rotation in radians

    # Generate coordinate grid
    x = cp.linspace(-width / 2, width / 2, width) * scale
    y = cp.linspace(-height / 2, height / 2, height) * scale
    X, Y = cp.meshgrid(x, y)

    # Apply rotation
    X_rot = X * cp.cos(theta) - Y * cp.sin(theta)
    Y_rot = X * cp.sin(theta) + Y * cp.cos(theta)

    # Convert to polar coordinates
    # R = cp.sqrt(X_rot**2 + Y_rot**2)
    # Phi = cp.arctan2(Y_rot, X_rot)
    Nx = 20
    Ny = 16
    Nphase = 3
    wprb = 35
    xprb = np.linspace(-width//2 + wprb, width//2 - wprb, Nx) * scale
    yprb = np.linspace(-height//2 + wprb, height//2 - wprb, Ny) * scale

    Npre = 6
    Nholograms = Nx*Ny*Nphase
    phases = np.linspace(0, 2*np.pi, Nphase, endpoint=False)
    Nframes = Nholograms + Npre
    hologram_buffer = cp.zeros((Nframes, height, width), dtype=cp.uint8)
    LG_field = cp.zeros((height, width), dtype=cp.complex64)
    
    print(Nframes, Nframes/3)
    assert Nframes%3 == 0
    # Example usage
    ds = np.linspace(2, 20, Ny)
    print("starting compute holograms")
    start_gpu = cp.cuda.Event()
    end_gpu = cp.cuda.Event()
    start_gpu.record()
    start_cpu = time.perf_counter()
    for i in range(Nholograms):
        with time_range('lg', color_id=0):
            w = wprb  # Beam waist
            j = i%Nphase
            k = (i//Nphase)%Nx
            p = (i//(Nphase*Nx))%Ny

            # Generate the Laguerre-Gaussian beam field
            laguerre_cuda(X_rot, Y_rot, w, 0, 0, 0, 0, out=LG_field)
            LG_field[:,:]  += laguerre_cuda(X_rot, Y_rot, w, 0, 0, xprb[k], yprb[p], phases[j])
            # LG_field += laguerre_cuda(X_rot, Y_rot, w, 0, 0, 150.0, 50.0, phases[j])
            #LG_field = LG_field/cp.max(LG_field)
        with time_range('holo', color_id=1):
            hologram_cuda(LG_field, X_rot, Y_rot, d=10, angle_deg=120, out=hologram_buffer[i])

    for i in range(Npre):
        w = wprb  # Beam waist
        j = Nholograms + i

        if i%2:
            LG_field = laguerre_cuda(X_rot, Y_rot, 3*wprb, 0, 0, 0, 0)
            LG_field = LG_field/cp.max(LG_field)
 
            hologram_cuda(LG_field, X, Y, d=12, angle_deg=120, out=hologram_buffer[j])
    print("done compute holograms")
    end_cpu = time.perf_counter()

    end_gpu.record()
    end_gpu.synchronize()
    t_gpu = cp.cuda.get_elapsed_time(start_gpu, end_gpu)
    t_cpu = end_cpu - start_cpu

    print(f"making {Nframes} holograms took {t_gpu*1e-3:.3f} s GPU time and {t_cpu:.3f} s CPU time")
    return 0

if __name__ == "__main__":
    #sys.exit(main())
    main()