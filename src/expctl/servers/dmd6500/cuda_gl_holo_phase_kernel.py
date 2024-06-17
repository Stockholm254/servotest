import numpy as np
import OpenGL.GL as gl
import glfw
from cuda import cudart
import cupy as cp
import cupyx
import ctypes
import sys
import OpenGL.GL.shaders
import time

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

    # Initialize GLFW
    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 5)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    
    if fullscreen:
        width = 1920
        height = 1080

        glfw.window_hint(glfw.DECORATED, False)
        glfw.window_hint(glfw.RESIZABLE, False)
        glfw.window_hint(glfw.VISIBLE, True)
        glfw.window_hint(glfw.AUTO_ICONIFY, False)
        
        monitors = glfw.get_monitors()
        # if len(monitors) < 2:
        #     raise RuntimeError("Second monitor not found.")
        print(monitors)
        
        window = glfw.create_window(width, height, "Hologram Display", monitors[-1], None)

    else:
        width = 800
        height = 600

        # Create a window
        window = glfw.create_window(width, height, "Hologram Display", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    shader_program = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader_source, gl.GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader_source, gl.GL_FRAGMENT_SHADER),
    )

    print("shaders compiled")

    vertices = np.array([
         1, 1, 0,  1, 0, 0,  1, 1,
         1,-1, 0,  0, 1, 0,  1, 0,
        -1,-1, 0,  0, 0, 1,  0, 0,
        -1, 1, 0,  1, 1, 0,  0, 1], dtype = 'float32')

    indices = np.array([
        0, 1, 3,
        1, 2, 3
    ], dtype=np.uint32)

    # Create VAO and VBO
    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)
    ebo = gl.glGenBuffers(1)

    gl.glBindVertexArray(vao)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

    # Position attribute
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, ctypes.c_void_p(0))
    gl.glEnableVertexAttribArray(0)

    # Color
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 32, ctypes.c_void_p(12))
    gl.glEnableVertexAttribArray(1)

    # Texture
    gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 32, ctypes.c_void_p(24))
    gl.glEnableVertexAttribArray(2)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0)

    # Create texture and PBO
    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

    pbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, pbo)
    gl.glBufferData(gl.GL_PIXEL_UNPACK_BUFFER, width * height * 4, None, gl.GL_STREAM_DRAW)

    # # Map PBO to CUDA and generate texture data
    flags = cudart.cudaGraphicsRegisterFlags.cudaGraphicsRegisterFlagsWriteDiscard
    texture_mapping = CudaOpenGLMappedArray(cp.uint8, (height, width, 4), pbo, flags) # what to map here?!


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
        w = wprb  # Beam waist
        j = i%Nphase
        k = (i//Nphase)%Nx
        p = (i//(Nphase*Nx))%Ny

        # Generate the Laguerre-Gaussian beam field
        LG_field = laguerre_cuda(X_rot, Y_rot, w, 0, 0, 0, 0)
        LG_field[:] += laguerre_cuda(X_rot, Y_rot, w, 0, 0, xprb[k], yprb[p], phases[j])
        # LG_field += laguerre_cuda(X_rot, Y_rot, w, 0, 0, 150.0, 50.0, phases[j])
        LG_field = LG_field/cp.max(LG_field)

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

    #sys.exit()
    # print(X.shape)
    with texture_mapping as text_cuda:
        # merge_white(hologram_buffer[0], text_cuda)
        merge_rgb(hologram_buffer[0], hologram_buffer[1], hologram_buffer[2], text_cuda)
    print("done merging")
    # # Copy data from PBO to texture
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.c_void_p(0))
    last_time = glfw.get_time()
    fps = 0
    nframes = 0
    print("enetering display loop")
    # Main loop
    gl.glUseProgram(shader_program)
    
    
    i = 0
    while not glfw.window_should_close(window):
        t = glfw.get_time()
        dt = t - last_time
        last_time = t

        fps = 1.0/dt
        # if dt >= 1.0:
        #     fps = nframes / dt
        #     last_time = t
        #     nframes = 0

        # width, height = glfw.get_window_size(window)
        # gl.glViewport(0, 0, width, height)
        # if i%2:
        #     l = i%Nholograms
        # else:
        #     l = Nholograms-1 - i%Nholograms

        l = i

        # # Generate the Laguerre-Gaussian beam field
        # LG_field = laguerre_gaussian(R, Phi, w, l, p)
        # LG_field = LG_field/cp.max(LG_field)
        # # LG_field = cp.abs(LG_field)**2
        
        # holo = hologram(LG_field, X, Y, r)


        # with texture_mapping as holograms:
        #     merge_white(holo, holograms)

        k = (l%(Nframes//3))*3
        #print(k, k+1, k+2)

        with texture_mapping as text_cuda:
            # text_cuda = hologram_buffer[l]
            # merge_white(hologram_buffer[l], text_cuda)
            merge_rgb(hologram_buffer[k], hologram_buffer[k+1], hologram_buffer[k+2], text_cuda)

        gl.glClearColor(0.2, 0.3, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.c_void_p(0))


        gl.glBindVertexArray(vao)
        # gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)

        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None) # last was None
        # gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        glfw.swap_buffers(window)
        glfw.poll_events()
        # glfw.set_window_title(window, f"cuda ({fps:.1f} fps)")
        if nframes%100:
            #print(f"cuda ({fps:.1f} fps)")
            pass
        nframes += 1
        i += 1

    # Cleanup
    gl.glDeleteVertexArrays(1, [vao])
    gl.glDeleteBuffers(1, [vbo])
    gl.glDeleteBuffers(1, [ebo])
    gl.glDeleteProgram(shader_program)
    gl.glDeleteTextures(1, [texture])
    # gl.glDeleteBuffers(1, [pbo])

    glfw.terminate()

if __name__ == "__main__":
    sys.exit(main())