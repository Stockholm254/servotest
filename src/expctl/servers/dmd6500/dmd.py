import numpy as np

class DLP6500:
    NUMROWS = 1080 #1920
    NUMCOLS = 1920 #1080
    PX_PITCH_UM = 7.56*np.sqrt(2)
    MIRROR_TILT_ANGLE_DEG = 12

    def __init__(self, sharpness=2, period=10, lam_um=0.78, phaseMap=None, amplitudeMap=None, angle=0.0, beta_deg=25.0):
        
        self.beta_deg = beta_deg # output angle of the DMD, the theory doesn't quite agree so this is measured!
        self.a = sharpness # sharpness of the phase mask, should always be 2
        self.d = period # period of the super grating, in pixels
        self.angle_deg = angle # angle of the super grating, in degrees
        self.lam = lam_um  # wavelength of the light, in microns

        self.DMD_rows = self.NUMROWS
        self.DMD_cols = self.NUMCOLS
        self.DMD_shape = (self.DMD_rows,self.DMD_cols)
        
        #self.X, self.Y = np.meshgrid(xs,ys)
        self.X, self.Y = self.pixel_to_xyCoord(np.arange(self.DMD_cols), np.arange(self.DMD_rows))
        self.R2 = self.X**2+self.Y**2

        if phaseMap is None:
            self.phaseMap = np.zeros(self.DMD_shape)
        else:
            self.phaseMap = phaseMap

        if amplitudeMap is None:
            self.amplitudeMap = np.ones(self.DMD_shape)
        else:
            self.amplitudeMap = amplitudeMap
    
    def pixel_to_xyCoord(self, colnum, rownum):
        col = (colnum -self.DMD_cols/2)[None,:]
        row = (rownum - self.DMD_rows/2)[:,None]
        b = np.deg2rad(self.beta_deg)
        x = 0.5*( (np.cos(b)+1)*col + (np.cos(b)-1)*row) # this is a shear transformation accounting for the DMD tilt along the (anti-)diagonal axis that squeezes the output field
        y = 0.5*( (np.cos(b)-1)*col + (np.cos(b)+1)*row)
        return x, y