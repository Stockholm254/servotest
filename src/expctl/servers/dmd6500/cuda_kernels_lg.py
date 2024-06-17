import numpy as np
from cuda import cudart
import cupy as cp
import cupyx

lg_cart_kernel = cp.RawKernel(r"""
#include <cupy/complex.cuh>
#include "math_constants.h"
                              
__device__ int factorial(int n) {
    int result = 1;
    for (int i = 1; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// Function to compute the reciprocal factorial
__device__ double reciprocal_factorial(int n) {
    double result = 1.0;
    for (int i = 1; i <= n; ++i) {
        result /= i;
    }
    return result;
}

__device__ float laguerre(int n, float a, float x) {
    if (n == 0) {
        return 1.0f;
    } else if (n == 1) {
        return 1.0f + a - x;
    } else {
        float L_prev = 1.0f;
        float L_curr = 1.0f + a - x;

        for (int i = 2; i <= n; ++i) {
            float L_next = ((2.0f * i - 1.0f + a - x) * L_curr - (i - 1.0f + a) * L_prev) / i;
            L_prev = L_curr;
            L_curr = L_next;
        }

        return L_curr;
    }
}


extern "C" __global__
void lg_func(const float* xx, const float* yy,
             complex<float>* z, float w, int l, int p, float x0, float y0, float tx, float ty, float phaseoff, int N, int M) {
                              
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
                              
    if (row < N && col < M) {
                              
    int idx = row * M + col;
                                                      
    float x = xx[idx] - x0;
    float y = yy[idx] - y0;
    float R = sqrtf(pow(x,2) + pow(y,2))/w; // scaled r
    float Phi = atan2f(y, x)*l;
    //float amp = sqrtf(2.0f / ( CUDART_PI_F * factorial(abs(l)))) / w;
    //float amp = sqrtf(2.0f *factorial(p) / ( CUDART_PI_F * factorial(p + abs(l))));
                              
    double amp = sqrt(2.0f * reciprocal_factorial(abs(l)) / ( CUDART_PI_F )) / w; // still diverges
                              
    //float amp = sqrtf(2.0f * / ( CUDART_PI_F )) / w;
    //float rad = pow((sqrtf(2.0f) * R / w),abs(l)) * expf(-1.0f*pow(R/w,2));
    double rad = pow((sqrtf(2.0f) * R),abs(l)) * expf(-1.0f*pow(R,2));
    float lag = laguerre(p, abs(l), 2*pow(R,2));
    //downcase a double to a float 
    float ramp = rad * amp;                          

    z[idx] = ramp* lag * exp(complex<float>(0.0f, -1.0f) * (Phi - phaseoff - tx*x - ty*y));
    //z[idx] = complex<float>(xx[idx], yy[idx]);                      
    }
}
""", 'lg_func')

def laguerre_cuda(X, Y, w, l, p, x0=0, y0=0, tx=0, ty=0, phase_offset=0, blockSize = 32, out=None):
    
    
    if isinstance(blockSize, tuple):
        threadsPerBlock = blockSize
    else:
        threadsPerBlock = (blockSize, blockSize)

    N, M = X.shape

    numBlocks = ((M + threadsPerBlock[0] - 1) // threadsPerBlock[0], (N + threadsPerBlock[1] - 1) // threadsPerBlock[1])
    
    if out is None:
        out = cp.empty_like(X, dtype=cp.complex64)
    else:
        assert out.dtype == cp.complex64
    lg_cart_kernel(numBlocks, threadsPerBlock, (X.astype(cp.float32), Y.astype(cp.float32), out, 
                                                cp.float32(w), cp.int32(l), cp.int32(p), 
                                                cp.float32(x0), cp.float32(y0), cp.float32(tx), cp.float32(ty), 
                                                cp.float32(phase_offset), cp.int32(N), cp.int32(M)))  # grid, block and arguments
    
    return out

hologram_kernel = cp.RawKernel(r"""
#include <cupy/complex.cuh>
#include "math_constants.h"
#include <curand_kernel.h>
                              
extern "C" __global__
void hologram(complex<float>* target, const float* xx, const float* yy,
             uint8_t* z, float d, float angle_rad, float a, float defocus, int N, int M) { //, curandState* states
                              
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
                              
    if (row < N && col < M) {
                              
    int idx = row * M + col;
                               
    // Initialize the random state for the current thread
    curandState state;
    curand_init(idx, 0, 0, &state);
                                                      
    float mag = abs(target[idx]);
    float targetPhase = arg(target[idx]); //atan2(imag(target), real(target));
                               
    float kx = cosf(angle_rad)*2.0f*CUDART_PI_F/d;
    float ky = sinf(angle_rad)*2.0f*CUDART_PI_F/d;
    float r2 = powf(xx[idx],2) + powf(yy[idx],2);
    float phase = fmodf(kx*xx[idx] + ky*yy[idx] + targetPhase + defocus*r2, 2.0f*CUDART_PI_F);
                                
    phase = fmodf(phase + 2.0f*CUDART_PI_F, 2.0f*CUDART_PI_F); // WATCH OUT! C computes a remainder, not a true modulus!          
    if (phase>CUDART_PI_F){
        phase = phase - 2.0f*CUDART_PI_F;                             
    }
    
            
    float prob = 0.5f*(tanhf(a*(phase+CUDART_PI_F*mag/2.0f)) + tanhf(a*(CUDART_PI_F*mag/2.0f-phase)));
    float r = curand_uniform(&state);

    //z[idx] = (r > prob) ? 0 : 1;
    //z[idx] = phase;                          

    // Compare p with r and store the result in the output array
    z[idx] = static_cast<uint8_t>(prob > r);
    }
}
""", 'hologram')

def hologram_cuda(target, X, Y, d=8, angle_deg = 0,a=2, defocus = 0, blockSize = 32, out=None):
    
    if isinstance(blockSize, tuple):
        threadsPerBlock = blockSize
    else:
        threadsPerBlock = (blockSize, blockSize)

    N, M = X.shape

    numBlocks = ((M + threadsPerBlock[0] - 1) // threadsPerBlock[0], (N + threadsPerBlock[1] - 1) // threadsPerBlock[1])
    
    angle_rad = angle_deg * np.pi/180.0
    #states = cp.zeros((N, M), dtype=cp.uint64)
    if out is None:
        out = cp.empty_like(X, dtype=cp.uint8)
    else:
        assert out.dtype == cp.uint8

    hologram_kernel(numBlocks, threadsPerBlock, (target.astype(cp.complex64), 
                                                X.astype(cp.float32), Y.astype(cp.float32), 
                                                out, 
                                                cp.float32(d), cp.float32(angle_rad), cp.float32(a), cp.float32(defocus), cp.int32(N), cp.int32(M)))  # grid, block and arguments , states
    
    return out

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
    
