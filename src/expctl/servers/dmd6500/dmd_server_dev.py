# This is the main dmd server class. It is responsible for 
# 1) in the main thread, create the GLFW window that shows patterns and transfers them to the DMD over HDMI. This is for all cavity measurements and doesn't require real time control.
#    it maintains all the opengl buffer opbjects, shaders and textures for the main window.
# 2) in a separate thread, launch the server class "DMDServer" from dmd_server_old that creates a TCP server that listens for commands from the frontpanel and sends a dataclass or list of dataclasses to the main thread
# 3) in the main thread, the list of dataclasses gets turned into a series of holograms using cupy and cuda_kernels_lg.py 
# 4) the holograms are then displayed on the DMD in one of two ways:
#   a) if the DMD is in "live" mode, the holograms are sent to the DMD over HDMI, which means we add a preamble to the series of patterns and then display them in a loop using GLFW
#   b) if the DMD is in "sequence" mode, the holograms are sent to the DMD over USB, using the encode function in pycrafter6500, which is a wrapper for the C++ library that controls the DMD
# in both cases, once the display loop is started or the upload is completed, the main thread sends a mesage back to the server class to indicate the new pattern is displayed
# to make the code compatible with other existing code, we want to use the pyqt threading framework, which means we need to make the DMDServer class a QObject and use signals and slots to communicate between the main thread and the server thread
# this will require some refactoring of the existing code, but should be relatively straightforward

import numpy as np
import OpenGL.GL as gl
import glfw
# from cuda import cudart
import cupy as cp
import cupyx
import ctypes
import sys
import OpenGL.GL.shaders
import time
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from .dmd_server_class import DMDServer

from .cuda_gl import *
from .cuda_kernels_lg import laguerre_cuda, hologram_cuda, merge_rgb, merge_white

def compute_holograms():
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
        LG_field += laguerre_cuda(X_rot, Y_rot, w, 0, 0, xprb[k], yprb[p], phases[j])
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

class DMDServerWorker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)
    storeSignal = pyqtSignal(object)

    def __init__(self, parent=None, port=60614, camera_id=0, camera_kwargs={}):
        super().__init__(parent)
        message = \
        """===========================================
        ==             DMD Server 1              ==
        ==        TI DLP Lightcrafter 6500       ==
        ===========================================

        Resolution: 1280*960
        Bit Depth: 8
        Maximum Trigger Rate: 14fps
        WARNING: The maximum frame rate is 14fps!"""
        self.serv = DMDServer("COut1", port, message=message, parent=self, camera_id=camera_id, camera_kwargs=camera_kwargs)

    def run_loop(self, roi):
        self.serv.main_loop(cond_fn=(lambda : not QThread.currentThread().isInterruptionRequested()) )
        self.serv.device.Disconnect()
        print("Exiting...")


class DMDWindow:
    def __init__(self, fullscreen=True, width=1920, height=1080):
        self.fullscreen = fullscreen
        self.width = width
        self.height = height
        self.window = None
        self.shader_program = None
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.texture = None
        self.pbo = None
        self.texture_mapping = None
        self.hologram_buffer = None
        self.last_time = None
        self.fps = None
        self.nframes = None
        self.i = None

    def create_window(self, width = 1920, height = 1080):
        # Create GLFW window
        if not glfw.init():
            return False

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 5)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)


        if self.fullscreen:
            glfw.window_hint(glfw.DECORATED, False)
            glfw.window_hint(glfw.RESIZABLE, False)
            glfw.window_hint(glfw.VISIBLE, True)
            glfw.window_hint(glfw.AUTO_ICONIFY, False)
            
            monitors = glfw.get_monitors()
            # if len(monitors) < 2:
            #     raise RuntimeError("Second monitor not found.")
            print(monitors)
            self.window = glfw.create_window(self.width, self.height, "Hologram Display", monitors[-1], None)
        else:
            self.window = glfw.create_window(self.width, self.height, "DMD Window", None, None)

        if not self.window:
            glfw.terminate()
            return False

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        return True

    def bind_buffers(self):
        # Compile shaders
        self.shader_program = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader_source, gl.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader_source, gl.GL_FRAGMENT_SHADER),
        )

        # Create VAO and VBO
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)

        # quads that make up a square
        vertices = np.array([
         1, 1, 0,  1, 0, 0,  1, 1,
         1,-1, 0,  0, 1, 0,  1, 0,
        -1,-1, 0,  0, 0, 1,  0, 0,
        -1, 1, 0,  1, 1, 0,  0, 1], dtype = 'float32')

        indices = np.array([
            0, 1, 3,
            1, 2, 3
        ], dtype=np.uint32)

        gl.glBindVertexArray(self.vao)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
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
        self.texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        self.pbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, self.pbo)
        gl.glBufferData(gl.GL_PIXEL_UNPACK_BUFFER, self.width * self.height * 4, None, gl.GL_STREAM_DRAW)

        # Map PBO to CUDA and generate texture data
        flags = cudart.cudaGraphicsRegisterFlags.cudaGraphicsRegisterFlagsWriteDiscard
        self.texture_mapping = CudaOpenGLMappedArray(cp.uint8, (self.height, self.width, 4), self.pbo, flags)

    def compute_patterns_phasemap(self):
        # Compute holograms

        width, height = self.width, self.height
        scale = 1.0  # Scale factor for coordinates
        theta = 0  # Rotation in radians

        # Generate coordinate grid
        x = cp.linspace(-width / 2, width / 2, width) * scale
        y = cp.linspace(-height / 2, height / 2, height) * scale
        X, Y = cp.meshgrid(x, y)

        # Apply rotation
        X_rot = X * cp.cos(theta) - Y * cp.sin(theta)
        Y_rot = X * cp.sin(theta) + Y * cp.cos(theta)

        Nx = 24
        Ny = 20
        Nphase = 5
        wprb = 30
        xprb = np.linspace(-width//2+100 + wprb, width//2 - wprb -100, Nx) * scale
        yprb = np.linspace(-height//2 +100 + wprb, height//2 - wprb - 100, Ny) * scale

        Npre = 9
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
            LG_field += laguerre_cuda(X_rot, Y_rot, w, 0, 0, xprb[k], yprb[p], phases[j])
            # LG_field += laguerre_cuda(X_rot, Y_rot, w, 0, 0, 150.0, 50.0, phases[j])
            LG_field = LG_field/cp.max(LG_field)

            hologram_cuda(LG_field, X_rot, Y_rot, d=10, angle_deg=60, defocus=-2e-4, out=hologram_buffer[i])

        for i in range(Npre):
            w = wprb  # Beam waist
            j = Nholograms + i

            if i%2:
                LG_field = laguerre_cuda(X_rot, Y_rot, 5*wprb, 0, 0, 0, 0)
                LG_field = LG_field/cp.max(LG_field)
    
                hologram_cuda(LG_field, X, Y, d=10, angle_deg=60, out=hologram_buffer[j])
        print("done compute holograms")
        end_cpu = time.perf_counter()

        end_gpu.record()
        end_gpu.synchronize()
        t_gpu = cp.cuda.get_elapsed_time(start_gpu, end_gpu)
        t_cpu = end_cpu - start_cpu

        print(f"making {Nframes} holograms took {t_gpu*1e-3:.3f} s GPU time and {t_cpu:.3f} s CPU time")
        return hologram_buffer
    
    def compute_patterns(self):
        # Compute holograms

        width, height = self.width, self.height
        scale = 1.0  # Scale factor for coordinates
        theta = 0  # Rotation in radians

        # Generate coordinate grid
        x = cp.linspace(-width / 2, width / 2, width) * scale
        y = cp.linspace(-height / 2, height / 2, height) * scale
        X, Y = cp.meshgrid(x, y)

        # Apply rotation
        X_rot = X * cp.cos(theta) - Y * cp.sin(theta)
        Y_rot = X * cp.sin(theta) + Y * cp.cos(theta)

        Npre = 0
        Nholograms = 36
        Nframes = Nholograms + Npre
        hologram_buffer = cp.zeros((Nframes, height, width), dtype=cp.uint8)
        
        print(Nframes, Nframes/3)
        assert Nframes%3 == 0


        print("starting compute holograms")
        start_gpu = cp.cuda.Event()
        end_gpu = cp.cuda.Event()
        start_gpu.record()
        start_cpu = time.perf_counter()

        for i in range(Nframes):
            w = 50  # Beam waist
            l = i%Nframes

            # Generate the Laguerre-Gaussian beam field
            LG_field = laguerre_cuda(X_rot, Y_rot, w, l, 0, 0, 0)
            # LG_field += laguerre_cuda(X_rot, Y_rot, w, 0, 0, 150.0, 50.0, phases[j])
            LG_field = LG_field/cp.max(LG_field)

            hologram_cuda(LG_field, X_rot, Y_rot, d=10, angle_deg=-120+180, out=hologram_buffer[i])

        print("done compute holograms")
        end_cpu = time.perf_counter()

        end_gpu.record()
        end_gpu.synchronize()
        t_gpu = cp.cuda.get_elapsed_time(start_gpu, end_gpu)
        t_cpu = end_cpu - start_cpu

        print(f"making {Nframes} holograms took {t_gpu*1e-3:.3f} s GPU time and {t_cpu:.3f} s CPU time")

        with self.texture_mapping as text_cuda:
            merge_rgb(hologram_buffer[0], hologram_buffer[1], hologram_buffer[2], text_cuda)
        
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.c_void_p(0))
        return hologram_buffer

    def merge_to_texture_and_draw(self, hologram_buffer, l, Nframes=66):
        # Merge holograms to texture
        show_rgb = False
        if show_rgb:
            k = (l%(Nframes//3))*3
            with self.texture_mapping as text_cuda:
                merge_rgb(hologram_buffer[k], hologram_buffer[k+1], hologram_buffer[k+2], text_cuda)
        else:
            k = (l%(Nframes))
            with self.texture_mapping as text_cuda:
                merge_white(hologram_buffer[k], text_cuda)

        gl.glClearColor(0.2, 0.3, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, self.width, self.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, ctypes.c_void_p(0))


        gl.glBindVertexArray(self.vao)

        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None) # last was None

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)


    def display_loop(self, hologram_buffer):
        # Main display loop
        last_time = glfw.get_time()
        fps = 0
        nframes = 0
        Nframes = hologram_buffer.shape[0]
        print("enetering display loop")
        # Main loop
        gl.glUseProgram(self.shader_program)
        
        
        i = 0
        while not glfw.window_should_close(self.window):
            t = glfw.get_time()
            dt = t - last_time
            last_time = t

            fps = 1.0/dt

            self.merge_to_texture_and_draw(hologram_buffer, i, Nframes=Nframes)

            glfw.swap_buffers(self.window)
            glfw.poll_events()
            # glfw.set_window_title(window, f"cuda ({fps:.1f} fps)")
            if nframes%10000:
                #print(f"cuda ({fps:.1f} fps)")
                pass
            nframes += 1
            i += 1

    def run(self):
        if not self.create_window():
            sys.exit(1)

        self.bind_buffers()
        hologram_buffer = self.compute_patterns_phasemap() #
        # hologram_buffer = self.compute_patterns()
        self.display_loop(hologram_buffer)

        # Cleanup
        gl.glDeleteVertexArrays(1, [self.vao])
        gl.glDeleteBuffers(1, [self.vbo])
        gl.glDeleteBuffers(1, [self.ebo])
        gl.glDeleteProgram(self.shader_program)
        gl.glDeleteTextures(1, [self.texture])
        gl.glDeleteBuffers(1, [self.pbo])

        glfw.terminate()

if __name__ == "__main__":
    dmd_window = DMDWindow()
    dmd_window.run()
