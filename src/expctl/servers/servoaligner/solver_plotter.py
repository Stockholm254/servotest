import numpy as np
from matplotlib import pyplot as plt

import sympy
from sympy import symbols, sin, cos, tan, Add
from sympy import Matrix, nsolve, nsimplify, solve, pi
from sympy.parsing.sympy_parser import parse_expr
from itertools import product

from matplotlib.ticker import AutoMinorLocator, MultipleLocator

import matplotlib
import atexit
import multiprocessing
import os
import time
from scipy.optimize import fsolve, least_squares

# the whole idea is to make a more general version of existing raytracing code
# adding constraint is equal to adding a point that a light ray must pass through

class Opelements:
    """Class of definitng single optical elements"""
    def __init__(self, tl0=0, tl=0, tl_last=0, u=0, v=0, RTM=None, element_length=25.4e-3):
        self.pos_x=u
        self.pos_y=v
        self.tl0=tl0
        self.tl=tl
        self.tl_last=tl_last
        self.RTM=RTM
        self.element_length=element_length

    def _ElemTR(self,elem,theta,u,v):
        return Matrix([[1,-u,-v],[0,1,0],[0,0,1]])*Matrix([[1,0,0],[0,cos(theta),sin(theta)],[0,-sin(theta),cos(theta)]])*elem*Matrix([[1,0,0],[0,cos(-theta),sin(-theta)],[0,-sin(-theta),cos(-theta)]])*Matrix([[1,u,v],[0,1,0],[0,0,1]])

    def elem(self):
        self.elem_mat=self._ElemTR(self.RTM, self.tl0 + self.tl + self.tl_last, self.pos_x, self.pos_y)
        return self.elem_mat

    def elem_ref(self):
        self.elem_ref_mat=self._ElemTR(self.RTM, self.tl0 + self.tl_last, self.pos_x, self.pos_y)
        return self.elem_ref_mat

    def change_RTM(self, RTM):
        self.RTM=RTM
        self.elem()
        self.elem_ref()

    def tl_all(self):
        """Return the total adjustable angle of the element in rad"""
        return self.tl + self.tl_last

    def tl_elem(self):
        """Return the total angle of the element in rad"""
        return self.tl0 + self.tl + self.tl_last

    def tl_ref(self):
        """Return the total angle of the element reference in rad"""
        return self.tl0 + self.tl_last

    def elem_ray(self):
        if self.tl_elem()==0:
            return Matrix([[-self.pos_x],[1],[0]])
        return Matrix([[self.pos_y-tan(pi/2-self.tl_elem())*self.pos_x],[tan(pi/2-self.tl_elem())],[-1]])

    def elem_ref_ray(self):
        if self.tl_ref()==0:
            return Matrix([[-self.pos_x],[1],[0]])
        return Matrix([[self.pos_y-tan(pi/2-self.tl_ref())*self.pos_x],[tan(pi/2-self.tl_ref())],[-1]])

class Mirror(Opelements):
    """Class of defining a mirror"""
    def __init__(self, tl0=0, tl_last=0, tl=0, u=0, v=0, chirality= 'Left', dist=0, comp=0, tpi=100, is_y=0, is_fixed=0):
        self.RTM=Matrix([[-1,0,0],[0,1,0],[0,0,-1]])
        super().__init__(tl0=tl0, tl=tl, tl_last=tl_last, u=u, v=v, RTM=self.RTM)
        self.elem_type='Mirror'
        if chirality=='Left':
            self.chirality=1
        elif chirality=='Right':
            self.chirality=-1
        else:
            raise ValueError("Chirality should be either 'Left' or 'Right'")
        self.is_y=is_y
        self.is_fixed=is_fixed

        if self.is_fixed==1:
            self.dist=0
        else:
            self.dist=dist

        self.tpi=tpi
        self.comp_dist=np.tan(float(-comp))*self.dist*0.5
        self.pos_x=self.pos_x + 0.5*self.dist*np.sin(self.tl0) - self.chirality * np.cos(self.tl0) * self.comp_dist
        self.pos_y=self.pos_y + 0.5*self.dist*np.cos(self.tl0) + self.chirality * np.sin(self.tl0) * self.comp_dist
        self.elem()
        self.elem_ref()

    def knob_deg(self):
        if self.is_y==1:
            self.knob_value_deg = np.tan(float(self.tl_all()))*360*self.tpi*(self.dist/25.4e-3)
            return np.tan(float(self.tl_all()))*360*self.tpi*(self.dist/25.4e-3)

        self.knob_value_deg = -1*self.chirality*np.tan(float(self.tl_all()))*360*self.tpi*(self.dist/25.4e-3)
        return self.knob_value_deg

    def knob_12b(self):
        """Return the absolute 12 bit value of the knob"""
        self.knob_value_12b = int(np.round(self.knob_deg()*4096/360)+2048)
        return self.knob_value_12b

class Lens(Opelements):
    """Class of defining a lens"""
    def __init__(self, tl0=0, tl_last=0, tl=0, u=0, v=0, f=1):
        self.RTM=Matrix([[1,0,0],[-1/f,1,0],[0,0,1]])
        super().__init__(tl0=tl0, tl=tl, tl_last=tl_last, u=u, v=v, RTM=self.RTM)
        self.elem_type='Lens'
        self.elem()
        self.elem_ref()

class Point:
    """Class of defining a point"""
    def __init__(self, u=0, v=0, name='untitled', color='red', marker='o'):
        self.pos_x=u
        self.pos_y=v
        self.name=name
        self.color=color
        self.marker=marker

class Optical_system_solver:
    """Class of defining the whole optical system, needs at least one input ray and a starting position"""
    def __init__(self, ray_in=[[0],[1],[0]], init_elem=list(), xy=0):
        if type(init_elem) is list:
            self.elem_list=init_elem.copy()
        else:
            self.elem_list=[init_elem]
        if ray_in is not None:
            self.ray_in=Matrix(ray_in.copy())
        self.xy=xy
        self.ray_list=[self.ray_in]
        self.ray_list_ref=[self.ray_in]
        self.point_list=[]
        self.init_ray_length=0.5
        self.plot_size=(10,10)

    #here the elem should be a class of Opelements
    def add_element(self, elem):
        if type(elem) is list:
            self.elem_list=self.elem_list+elem
        elif isinstance(elem, Opelements):
            self.elem_list.append(elem)
        else:
            raise ValueError("The element or list of elements should be a class of Opelements")

    def add_input_ray(self, ray_in):
        self.ray_in=Matrix(ray_in.copy())
        self.ray_list=[self.ray_in]
        self.ray_list_ref=[self.ray_in]

    def _ray_colinear_solver(self, ray1, ray2, x1, x2):
        try:
            eqn1 = (ray1[1]*ray2[0] - ray2[1]*ray1[0])
            eqn2 = (ray1[2]*ray2[0] - ray2[2]*ray1[0])
            result=nsolve((eqn1,eqn2),(x1,x2),(1e-3,1e-3), prec=10)
        except:
            eqn1 = (ray1[1]*ray2[2] - ray2[1]*ray1[2])
            eqn2 = (ray1[0]*ray2[2] - ray2[0]*ray1[2])
            result=nsolve((eqn1,eqn2),(x1,x2),(1e-3,1e-3), prec=10)
        return result

    def _ray_colinear_solver_scipy(self, ray1, ray2, x1, x2):
        tol_opts = {'xtol': 1e-12, 'ftol': 1e-12, 'gtol': 1e-12, 'max_nfev': 10000}
        if abs(ray2[1]/ray2[2]) < 1e2:
            eqn1 = ray1[1]*ray2[2] - ray2[1]*ray1[2]
            eqn2 = ray1[0]*ray2[2] - ray2[0]*ray1[2]
            fb1 = sympy.lambdify((x1, x2), eqn1, 'numpy')
            fb2 = sympy.lambdify((x1, x2), eqn2, 'numpy')
            f = lambda vars: [fb1(vars[0], vars[1]), fb2(vars[0], vars[1])]
            bounds = ([-np.pi/8, -np.pi/8], [np.pi/8, np.pi/8])
            result = least_squares(f, [0, 0], bounds=bounds, **tol_opts).x
        else:
            eqn1 = ray1[1]*ray2[0] - ray2[1]*ray1[0]
            eqn2 = ray1[2]*ray2[0] - ray2[2]*ray1[0]
            fb1 = sympy.lambdify((x1, x2), eqn1, 'numpy')
            fb2 = sympy.lambdify((x1, x2), eqn2, 'numpy')
            f = lambda vars: [fb1(vars[0], vars[1]), fb2(vars[0], vars[1])]
            bounds = ([-np.pi/8, -np.pi/8], [np.pi/8, np.pi/8])
            result = least_squares(f, [0, 0], bounds=bounds, **tol_opts).x
        return result

    def _intersection_solver_symbol(self, ray_cache1, ray_cache2):
        a1=ray_cache1[1]
        a2=ray_cache2[1]
        b1=ray_cache1[2]
        b2=ray_cache2[2]
        c1=ray_cache1[0]
        c2=ray_cache2[0]
        x_solve=(b2*c1-b1*c2)/(a2*b1-a1*b2)
        y_solve=(a1*c2-a2*c1)/(a2*b1-a1*b2)
        return x_solve, y_solve

    def _intersection_solver(self, ray_cache1, ray_cache2):
        a1=float(ray_cache1[1])
        a2=float(ray_cache2[1])
        b1=float(ray_cache1[2])
        b2=float(ray_cache2[2])
        c1=float(ray_cache1[0])
        c2=float(ray_cache2[0])
        x_solve=(b2*c1-b1*c2)/(a2*b1-a1*b2)
        y_solve=(a1*c2-a2*c1)/(a2*b1-a1*b2)
        return x_solve, y_solve

    def default_setup_solver(self, params=dict(), tl_list=[0,0,0,0], comp_list=[0,0,0,0], plot_switch=0):
        #default setup should be integrated with angle solver which provides the constraint
        #comp_list is the list of compensation x angle for each mirror that is coupled to y angle
        #definition of parameters
        tl1, tl2, tl3, tl4 = symbols('tl1 tl2 tl3 tl4')
        
        x1=params['x1']
        x2=params['x2']
        x3=params['x3']
        x4=params['x4']
        dy0=params['dy0']
        dy1=params['dy1']
        fl1=params['fl1']
        fl2=params['fl2']
        fl3=params['fl3']
        MOT_Cav_dist=params['MOT_Cav_dist']
        MOT_pos=params['MOT_pos_1']
        MOT_pos_rel=params['MOT_pos_rel']
        Cav_pos=params['Cav_pos_1']

        Mrr1_pos_x=0
        Mrr1_pos_y=0
        Mrr2_pos_x=x1
        Mrr2_pos_y=0
        Mrr3_pos_x=x1
        Mrr3_pos_y=x2 + dy0 + dy1 + x3
        Mrr4_pos_x=x1 - x4
        Mrr4_pos_y=x2 + dy0 + dy1 + x3
        Ml1_pos_x=x1
        Ml1_pos_y=x2
        Ml2_pos_x=x1
        Ml2_pos_y=x2 + dy0
        Ml3_pos_x=x1
        Ml3_pos_y=x2 + dy0 + dy1
        
        MOT_pos_x= x1 + MOT_pos
        MOT_pos_y= x2 + MOT_pos_rel 

        Cav_pos_x= x1 + Cav_pos
        Cav_pos_y= x2 + MOT_pos_rel + MOT_Cav_dist
        MOT_point=Point(u=MOT_pos_x, v=MOT_pos_y, name='MOT')
        Cav_point=Point(u=Cav_pos_x, v=Cav_pos_y, name='Cavity', marker='x')
        
        self.point_list=[MOT_point, Cav_point]

        Mrr1=Mirror(tl0=3*np.pi/4, tl=tl1, tl_last=tl_list[0], u=Mrr1_pos_x, v=Mrr1_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[0])
        Mrr2=Mirror(tl0=np.pi/4, tl=tl2, tl_last=tl_list[1], u=Mrr2_pos_x, v=Mrr2_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[1])
        Mrr3=Mirror(tl0=-np.pi/4, tl=tl3, tl_last=tl_list[2], u=Mrr3_pos_x, v=Mrr3_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[2])
        Mrr4=Mirror(tl0=3*np.pi/4, tl=tl4, tl_last=tl_list[3], u=Mrr4_pos_x, v=Mrr4_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[3])
        Ml1=Lens(tl0=-np.pi/2, tl=0, u=Ml1_pos_x, v=Ml1_pos_y, f=fl1)
        Ml2=Lens(tl0=-np.pi/2, tl=0, u=Ml2_pos_x, v=Ml2_pos_y, f=fl2)
        Ml3=Lens(tl0=-np.pi/2, tl=0, u=Ml3_pos_x, v=Ml3_pos_y, f=fl3)

        ray_in=[[0],[1],[0]]

        self.ray_in=Matrix(ray_in.copy())
        #angle solver
        raymiddleref=Matrix([[Cav_pos_x*MOT_pos_y-MOT_pos_x*Cav_pos_y],[Cav_pos_y-MOT_pos_y],[MOT_pos_x-Cav_pos_x]])
        raymiddle = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Ml1])[0]
        result = self._ray_colinear_solver_scipy(raymiddle, raymiddleref, tl1, tl2)

        Mrr1.tl=result[0]
        Mrr2.tl=result[1]
        #update the element matrix
        Mrr1.elem()
        Mrr2.elem()
        raymiddle = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Ml1])[0]

        rayfinal = self._ray_propagator(raymiddle, [Ml2, Ml3, Mrr3, Mrr4])[0]
        rayfinalref = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Ml1, Ml2, Ml3, Mrr3, Mrr4])[1]
        result=self._ray_colinear_solver_scipy(rayfinal, rayfinalref, tl3, tl4)

        Mrr3.tl=result[0]
        Mrr4.tl=result[1]
        #update the element matrix
        Mrr3.elem()
        Mrr4.elem()
        rayfinal = self._ray_propagator(raymiddle, [Ml2, Ml3, Mrr3, Mrr4])[0]

        self.elem_list=[Mrr1, Mrr2, Ml1, Ml2, Ml3, Mrr3, Mrr4]
        if plot_switch==1:
            self.ray_plotter()

        return Mrr1, Mrr2, Mrr3, Mrr4

    def default_setup_solver_y(self, params=dict(), tl_list=[0,0,0,0], comp_list=[0,0,0,0], plot_switch=0):
        #default setup should be integrated with angle solver which provides the constraint
        #comp_list is the list of compensation x angle for each mirror that is coupled to y angle
        #definition of parameters
        tl1, tl2, tl3, tl4 = symbols('tl1 tl2 tl3 tl4')

        x1=params['x1']
        x2=params['x2']
        x3=params['x3']
        x4=params['x4']
        dy0=params['dy0']
        dy1=params['dy1']
        fl1=params['fl1']
        fl2=params['fl2']
        fl3=params['fl3']
        MOT_Cav_dist=params['MOT_Cav_dist']
        MOT_pos=params['MOT_pos_2']
        MOT_pos_rel=params['MOT_pos_rel']
        Cav_pos=params['Cav_pos_2']

        Mrr1_pos_x=0
        Mrr1_pos_y=0
        Mrr2_pos_x=x1
        Mrr2_pos_y=0
        Ml1_pos_x=Mrr2_pos_x + x2
        Ml1_pos_y=0
        Ml2_pos_x=Ml1_pos_x + dy0
        Ml2_pos_y=0
        Ml3_pos_x=Ml2_pos_x + dy1
        Ml3_pos_y=0
        Mrr3_pos_x=Ml3_pos_x + x3
        Mrr3_pos_y=0
        Mrr4_pos_x=Mrr3_pos_x + x4
        Mrr4_pos_y=0

        MOT_pos_x= Ml1_pos_x + MOT_pos_rel
        MOT_pos_y= MOT_pos

        Cav_pos_x= Ml1_pos_x + MOT_pos_rel + MOT_Cav_dist
        Cav_pos_y= Cav_pos
        MOT_point=Point(u=MOT_pos_x, v=MOT_pos_y, name='MOT')
        Cav_point=Point(u=Cav_pos_x, v=Cav_pos_y, name='Cavity', marker='x')
        
        self.point_list=[MOT_point, Cav_point]

        Mrr1=Mirror(tl0=np.pi, tl=tl1, tl_last=tl_list[0], u=Mrr1_pos_x, v=Mrr1_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[0], is_y=1)
        Mrr2=Mirror(tl0=np.pi, tl=tl2, tl_last=tl_list[1], u=Mrr2_pos_x, v=Mrr2_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[1], is_y=1)
        Mrr3=Mirror(tl0=np.pi, tl=tl3, tl_last=tl_list[2], u=Mrr3_pos_x, v=Mrr3_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[2], is_y=1)
        Mrr4=Mirror(tl0=np.pi, tl=tl4, tl_last=tl_list[3], u=Mrr4_pos_x, v=Mrr4_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[3], is_y=1)
        Ml1=Lens(tl0=0, tl=0, u=Ml1_pos_x, v=Ml1_pos_y, f=fl1)
        Ml2=Lens(tl0=0, tl=0, u=Ml2_pos_x, v=Ml2_pos_y, f=fl2)
        Ml3=Lens(tl0=0, tl=0, u=Ml3_pos_x, v=Ml3_pos_y, f=fl3)

        ray_in=[[0],[0],[1]]

        self.ray_in=Matrix(ray_in.copy())

        elem_list=[Mrr1, Mrr2, Ml1, Ml2, Ml3, Mrr3, Mrr4]
        #angle solver
        raymiddleref=Matrix([[Cav_pos_x*MOT_pos_y-MOT_pos_x*Cav_pos_y],[Cav_pos_y-MOT_pos_y],[MOT_pos_x-Cav_pos_x]])
        raymiddle = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Ml1])[0]
        result = self._ray_colinear_solver_scipy(raymiddle, raymiddleref, tl1, tl2)

        Mrr1.tl=result[0]
        Mrr2.tl=result[1]
        Mrr1.elem()
        Mrr2.elem()
        raymiddle = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Ml1])[0]

        rayfinal = self._ray_propagator(raymiddle, [Ml2, Ml3, Mrr3, Mrr4])[0]
        rayfinalref = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Ml1, Ml2, Ml3, Mrr3, Mrr4])[1]
        result = self._ray_colinear_solver_scipy(rayfinal, rayfinalref, tl3, tl4)

        Mrr3.tl=result[0]
        Mrr4.tl=result[1]
        Mrr3.elem()
        Mrr4.elem()
        rayfinal = self._ray_propagator(raymiddle, [Ml2, Ml3, Mrr3, Mrr4])[0]

        self.elem_list=[Mrr1, Mrr2, Ml1, Ml2, Ml3, Mrr3, Mrr4]
        if plot_switch==1:
            self.ray_plotter()

        return Mrr1, Mrr2, Mrr3, Mrr4

    def real_setup_solver_1(self, params=dict(), tl_list=[0,0,0,0], comp_list=[0,0,0,0], plot_switch=0):
        #default setup should be integrated with angle solver which provides the constraint
        #comp_list is the list of compensation x angle for each mirror that is coupled to y angle
        #definition of parameters
        tl1, tl2, tl3, tl4 = symbols('tl1 tl2 tl3 tl4')
        
        x1=params['x1']
        x2=params['x2']        
        x3=params['x3']
        x4=params['x4']
        dy0=params['dy0']
        dy1=params['dy1']
        dy2=params['dy2']
        dy3=params['dy3']
        fl1=params['fl1']
        fl2=params['fl2']
        fl3=params['fl3']
        MOT_Cav_dist=params['MOT_Cav_dist']
        MOT_pos=params['MOT_pos_1']
        Cav_pos=params['Cav_pos_1']
        MOT_pos_rel=params['MOT_pos_rel']

        Mrr1_pos_x=0
        Mrr1_pos_y=0
        Mrr2_pos_x=0
        Mrr2_pos_y=x1
        Mrra_pos_x=-x2
        Mrra_pos_y=x1
        Ml1_pos_x=-x2
        Ml1_pos_y=x1-dy0
        Ml2_pos_x=-x2
        Ml2_pos_y=Ml1_pos_y - dy1
        Mrrb_pos_x=-x2
        Mrrb_pos_y=Ml2_pos_y - dy2
        Ml3_pos_x=-x2 - dy3
        Ml3_pos_y=Mrrb_pos_y
        Mrr3_pos_x=Ml3_pos_x - x3
        Mrr3_pos_y=Mrrb_pos_y
        Mrr4_pos_x=Mrr3_pos_x - x4
        Mrr4_pos_y=Mrrb_pos_y

        MOT_pos_x= Ml1_pos_x + MOT_pos
        MOT_pos_y= Ml1_pos_y - MOT_pos_rel

        Cav_pos_x= Ml1_pos_x + Cav_pos
        Cav_pos_y= Ml1_pos_y - MOT_pos_rel + MOT_Cav_dist
        MOT_point=Point(u=MOT_pos_x, v=MOT_pos_y, name='MOT')
        Cav_point=Point(u=Cav_pos_x, v=Cav_pos_y, name='Cavity', marker='x')

        self.point_list=[MOT_point, Cav_point]

        Mrr1=Mirror(tl0=np.pi/4, tl=tl1, tl_last=tl_list[0], u=Mrr1_pos_x, v=Mrr1_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[0], is_y=0)
        Mrr2=Mirror(tl0=-np.pi/4, tl=tl2, tl_last=tl_list[1], u=Mrr2_pos_x, v=Mrr2_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[1], is_y=0)
        Mrra=Mirror(tl0=np.pi/4, u=Mrra_pos_x, v=Mrra_pos_y, is_y=0, is_fixed=1)
        Mrrb=Mirror(tl0=np.pi/4, u=Mrrb_pos_x, v=Mrrb_pos_y, is_y=0, is_fixed=1)
        Mrr3=Mirror(tl0=np.pi, tl=tl3, tl_last=tl_list[2], u=Mrr3_pos_x, v=Mrr3_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[2], is_y=1)
        Mrr4=Mirror(tl0=np.pi, tl=tl4, tl_last=tl_list[3], u=Mrr4_pos_x, v=Mrr4_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[3], is_y=1)
        Ml1=Lens(tl0=np.pi/2, tl=0, u=Ml1_pos_x, v=Ml1_pos_y, f=fl1)
        Ml2=Lens(tl0=np.pi/2, tl=0, u=Ml2_pos_x, v=Ml2_pos_y, f=fl2)
        Ml3=Lens(tl0=0, tl=0, u=Ml3_pos_x, v=Ml3_pos_y, f=fl3)

        ray_in=[[0],[0],[1]]

        self.ray_in=Matrix(ray_in.copy())

        elem_list=[Mrr1, Mrr2, Mrra, Ml1, Ml2, Mrrb, Ml3, Mrr3, Mrr4]
        #angle solver
        raymiddleref=Matrix([[Cav_pos_x*MOT_pos_y-MOT_pos_x*Cav_pos_y],[Cav_pos_y-MOT_pos_y],[MOT_pos_x-Cav_pos_x]])
        raymiddle = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Mrra, Ml1])[0]
        result = self._ray_colinear_solver(raymiddle, raymiddleref, tl1, tl2)

        Mrr1.tl=result[0]
        Mrr2.tl=result[1]
        Mrr1.elem()
        Mrr2.elem()
        raymiddle = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Mrra, Ml1])[0]

        rayfinal = self._ray_propagator(raymiddle, [Ml2, Mrrb, Ml3, Mrr3, Mrr4])[0]
        rayfinalref = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Mrra, Ml1, Ml2, Mrrb, Ml3, Mrr3, Mrr4])[1]
        result = self._ray_colinear_solver(rayfinal, rayfinalref, tl3, tl4)

        Mrr3.tl=result[0]
        Mrr4.tl=result[1]
        Mrr3.elem()
        Mrr4.elem()
        rayfinal = self._ray_propagator(raymiddle, [Ml2, Mrrb, Ml3, Mrr3, Mrr4])[0]

        self.elem_list=[Mrr1, Mrr2, Mrra, Ml1, Ml2, Mrrb, Ml3, Mrr3, Mrr4]
        if plot_switch==1:
            self.ray_plotter()

        return Mrr1, Mrr2, Mrr3, Mrr4

    def real_setup_solver_2(self, params=dict(), tl_list=[0,0,0,0], comp_list=[0,0,0,0], plot_switch=0):
        #default setup should be integrated with angle solver which provides the constraint
        #comp_list is the list of compensation x angle for each mirror that is coupled to y angle
        #definition of parameters
        tl1, tl2, tl3, tl4 = symbols('tl1 tl2 tl3 tl4')
        
        x1=params['x1']
        x2=params['x2']
        x3=params['x3']
        x4=params['x4']
        dy0=params['dy0']
        dy1=params['dy1']
        dy2=params['dy2']
        dy3=params['dy3']
        fl1=params['fl1']
        fl2=params['fl2']
        fl3=params['fl3']
        MOT_Cav_dist=params['MOT_Cav_dist']
        MOT_pos=params['MOT_pos_2']
        Cav_pos=params['Cav_pos_2']
        MOT_pos_rel=params['MOT_pos_rel']

        Mrr1_pos_x=0
        Mrr1_pos_y=0
        Mrr2_pos_x=-x1
        Mrr2_pos_y=0
        Mrra_pos_x=Mrr2_pos_x - x2
        Mrra_pos_y=0
        Ml1_pos_x=Mrra_pos_x
        Ml1_pos_y=-dy0
        Ml2_pos_x=Ml1_pos_x
        Ml2_pos_y=Ml1_pos_y - dy1
        Mrrb_pos_x=Ml2_pos_x
        Mrrb_pos_y=Ml2_pos_y - dy2
        Ml3_pos_x=Mrrb_pos_x
        Ml3_pos_y=Mrrb_pos_y - dy3
        Mrr3_pos_x=Ml3_pos_x
        Mrr3_pos_y=Ml3_pos_y - x3
        Mrr4_pos_x=Mrr3_pos_x + x4
        Mrr4_pos_y=Mrr3_pos_y

        MOT_pos_x= Ml1_pos_x + MOT_pos
        MOT_pos_y= Ml1_pos_y - MOT_pos_rel

        Cav_pos_x= Ml1_pos_x + Cav_pos
        Cav_pos_y= Ml1_pos_y - MOT_pos_rel + MOT_Cav_dist
        MOT_point=Point(u=MOT_pos_x, v=MOT_pos_y, name='MOT')
        Cav_point=Point(u=Cav_pos_x, v=Cav_pos_y, name='Cavity', marker='x')
        
        self.point_list=[MOT_point, Cav_point]

        Mrr1=Mirror(tl0=-np.pi, tl=tl1, tl_last=tl_list[0], u=Mrr1_pos_x, v=Mrr1_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[0], is_y=1)
        Mrr2=Mirror(tl0=-np.pi, tl=tl2, tl_last=tl_list[1], u=Mrr2_pos_x, v=Mrr2_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[1], is_y=1)
        Mrra=Mirror(tl0=np.pi/4, u=Mrra_pos_x, v=Mrra_pos_y, is_y=0, is_fixed=1)
        Mrrb=Mirror(tl0=np.pi/2, u=Mrrb_pos_x, v=Mrrb_pos_y, is_y=0, is_fixed=1)
        Mrrb.change_RTM(Matrix([[1,0,0],[0,1,0],[0,0,1]]))
        Mrr3=Mirror(tl0=-np.pi/4, tl=tl3, tl_last=tl_list[2], u=Mrr3_pos_x, v=Mrr3_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[2], is_y=0)
        Mrr4=Mirror(tl0=-np.pi/4, tl=tl4, tl_last=tl_list[3], u=Mrr4_pos_x, v=Mrr4_pos_y, chirality='Left', dist=33.02e-3, comp=comp_list[3], is_y=0)
        Ml1=Lens(tl0=np.pi/2, tl=0, u=Ml1_pos_x, v=Ml1_pos_y, f=fl1)
        Ml2=Lens(tl0=np.pi/2, tl=0, u=Ml2_pos_x, v=Ml2_pos_y, f=fl2)
        Ml3=Lens(tl0=np.pi/2, tl=0, u=Ml3_pos_x, v=Ml3_pos_y, f=fl3)

        ray_in=[[0],[0],[-1]]

        self.ray_in=Matrix(ray_in.copy())

        elem_list=[Mrr1, Mrr2, Mrra, Ml1, Ml2, Mrrb, Ml3, Mrr3, Mrr4]
        #angle solver
        raymiddleref=Matrix([[Cav_pos_x*MOT_pos_y-MOT_pos_x*Cav_pos_y],[Cav_pos_y-MOT_pos_y],[MOT_pos_x-Cav_pos_x]])
        raymiddle = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Mrra, Ml1])[0]
        result = self._ray_colinear_solver(raymiddle, raymiddleref, tl1, tl2)

        Mrr1.tl=result[0]
        Mrr2.tl=result[1]
        Mrr1.elem()
        Mrr2.elem()
        raymiddle = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Mrra, Ml1])[0]

        rayfinal = self._ray_propagator(raymiddle, [Ml2, Mrrb, Ml3, Mrr3, Mrr4])[0]
        rayfinalref = self._ray_propagator(self.ray_in, [Mrr1, Mrr2, Mrra, Ml1, Ml2, Mrrb, Ml3, Mrr3, Mrr4])[1]
        result = self._ray_colinear_solver(rayfinal, rayfinalref, tl3, tl4)

        Mrr3.tl=result[0]
        Mrr4.tl=result[1]
        Mrr3.elem()
        Mrr4.elem()
        rayfinal = self._ray_propagator(raymiddle, [Ml2, Mrrb, Ml3, Mrr3, Mrr4])[0]

        self.elem_list=[Mrr1, Mrr2, Mrra, Ml1, Ml2, Mrrb, Ml3, Mrr3, Mrr4]
        if plot_switch==1:
            self.ray_plotter()

        return Mrr1, Mrr2, Mrr3, Mrr4

    def _ray_propagator(self, ray_in, elem_list):
        '''Propagate the ray through the optical elements, input ray should be a sympy matrix'''
        ray_list=[ray_in]
        ray_list_ref=[ray_in]
        for i in range(len(elem_list)):
            ray_cache=elem_list[i].elem_mat*ray_list[-1]
            ray_ref_cache=elem_list[i].elem_ref_mat*ray_list_ref[-1]
            ray_list.append(ray_cache)
            ray_list_ref.append(ray_ref_cache)
            #deal with y mirrors
            if elem_list[i].elem_type=='Mirror' and elem_list[i].is_y==1:
                x_solve, y_solve=self._intersection_solver_symbol(elem_list[i].elem_ray(), ray_list[-1])
                x_solve_ref, y_solve_ref=self._intersection_solver_symbol(elem_list[i].elem_ref_ray(), ray_list_ref[-1])

                sign=1
                sign_ref=1
                slope=-ray_list[-1][1]/ray_list[-1][2]
                slope_ref=-ray_list_ref[-1][1]/ray_list_ref[-1][2]
                ray_list[-1]=Matrix([[-(y_solve+slope*x_solve)*sign],[slope*sign],[sign]])
                ray_list_ref[-1]=Matrix([[-(y_solve_ref+slope_ref*x_solve_ref)*sign_ref],[slope_ref*sign_ref],[sign_ref]])

        return [ray_list[-1], ray_list_ref[-1]]

    def ray_in(self, ray_in):
        self.ray_in=Matrix(ray_in.copy())

    def clear_element(self):
        self.elem_list=[]

    def _plot_ray_solver(self):
        #first solving all the rays by matrix multiplication
        self.ray_list=[self.ray_in]
        self.ray_list_ref=[self.ray_in]

        start_vec=np.array([self.ray_in[2], -self.ray_in[1]])/np.sqrt(float(self.ray_in[1]**2+self.ray_in[2]**2))

        xy_solve=[]
        xy_solve_ref=[]
        for i in range(len(self.elem_list)):
            ray_cache=self.elem_list[i].elem_mat*self.ray_list[-1]
            ray_ref_cache=self.elem_list[i].elem_ref_mat*self.ray_list_ref[-1]
            self.ray_list.append(ray_cache)
            self.ray_list_ref.append(ray_ref_cache)
            x_solve, y_solve=self._intersection_solver(self.elem_list[i].elem_ray(), self.ray_list[-1])
            x_solve_ref, y_solve_ref=self._intersection_solver(self.elem_list[i].elem_ref_ray(), self.ray_list_ref[-1])
            #plot the input ray
            if i==0:
                xy_solve.append(list(np.array([x_solve,y_solve])-self.init_ray_length*start_vec))
                xy_solve_ref.append(list(np.array([x_solve_ref,y_solve_ref])-self.init_ray_length*start_vec))
            xy_solve.append([x_solve,y_solve])
            xy_solve_ref.append([x_solve_ref,y_solve_ref])

            #deal with y mirrors
            if self.elem_list[i].elem_type=='Mirror' and self.elem_list[i].is_y==1:
                #keep the same direction as before
                sign=np.sign(self.ray_list[-2][2])
                sign_ref=np.sign(self.ray_list_ref[-2][2])
                slope=-self.ray_list[-1][1]/self.ray_list[-1][2]
                slope_ref=-self.ray_list_ref[-1][1]/self.ray_list_ref[-1][2]
                self.ray_list[-1]=Matrix([[-(y_solve+slope*x_solve)*sign],[slope*sign],[sign]])
                self.ray_list_ref[-1]=Matrix([[-(y_solve_ref+slope_ref*x_solve_ref)*sign_ref],[slope_ref*sign_ref],[sign_ref]])

        #Solve the output ray
        ray_out=self.ray_list[-1]
        ray_out_ref=self.ray_list_ref[-1]
        end_vec=np.array([ray_out[2], -ray_out[1]])/np.sqrt(float(ray_out[1]**2+ray_out[2]**2))
        end_vec_ref=np.array([ray_out_ref[2], -ray_out_ref[1]])/np.sqrt(float(ray_out_ref[1]**2+ray_out_ref[2]**2))

        xy_solve.append(list(np.array([x_solve,y_solve])+self.init_ray_length*end_vec))
        xy_solve_ref.append(list(np.array([x_solve_ref,y_solve_ref])+self.init_ray_length*end_vec_ref))

        return xy_solve, xy_solve_ref

    def _Rotation_matrix(self,theta):
            return np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])

    def ray_plotter(self):
        #ray plotter
        xy_ray, xy_ray_ref=self._plot_ray_solver()
        fig,ax=plt.subplots(figsize=self.plot_size)
        #plt.scatter(x0,y0,marker='x',color='r')
        for i in range(len(xy_ray)-1):
            if i==0:
                plt.plot([xy_ray[i][0], xy_ray[i+1][0]], [xy_ray[i][1], xy_ray[i+1][1]],'b',label='Light Ray')
                plt.axis('equal')
                continue
            plt.plot([xy_ray[i][0], xy_ray[i+1][0]], [xy_ray[i][1], xy_ray[i+1][1]],'b')
            plt.axis('equal')

        for i in range(len(xy_ray_ref)-1):
            if i==0:
                plt.plot([xy_ray_ref[i][0], xy_ray_ref[i+1][0]], [xy_ray_ref[i][1], xy_ray_ref[i+1][1]],'g--',label='Reference Ray')
                continue
            plt.plot([xy_ray_ref[i][0], xy_ray_ref[i+1][0]], [xy_ray_ref[i][1], xy_ray_ref[i+1][1]],'g--')

        #Element plotter
        pivot_size=5
        #reference plot:
        for i in range(len(self.elem_list)):
            if self.elem_list[i].elem_type=='Mirror' and self.elem_list[i].is_fixed==0:
                point1=np.array([[0],[-self.elem_list[i].dist/2-self.elem_list[i].element_length/2]])
                point1=(self._Rotation_matrix(-float(self.elem_list[i].tl0 + self.elem_list[i].tl_last))@point1)+np.array([[self.elem_list[i].pos_x],[self.elem_list[i].pos_y]])
                point2=np.array([[0],[-self.elem_list[i].dist/2+self.elem_list[i].element_length/2]])
                point2=(self._Rotation_matrix(-float(self.elem_list[i].tl0 + self.elem_list[i].tl_last))@point2)+np.array([[self.elem_list[i].pos_x],[self.elem_list[i].pos_y]])
                cache_array=np.concatenate((point1,point2),1)
                if i==0:
                    ax.plot(cache_array[0,:],cache_array[1,:],linestyle='dashed',color='lightskyblue',lw=1,label='Reference Mirror')
                    ax.scatter(self.elem_list[i].pos_x,self.elem_list[i].pos_y,color='k',s=pivot_size)
                    continue
                ax.plot(cache_array[0,:],cache_array[1,:],linestyle='dashed',color='lightskyblue',lw=1)
                ax.scatter(self.elem_list[i].pos_x,self.elem_list[i].pos_y,color='k',s=pivot_size)

        #true plot:
        for i in range(len(self.elem_list)):
            if self.elem_list[i].elem_type=='Mirror':
                point1=np.array([[0],[-self.elem_list[i].dist/2-self.elem_list[i].element_length/2]])
                point1=(self._Rotation_matrix(-float(self.elem_list[i].tl0+self.elem_list[i].tl_all()))@point1)+np.array([[self.elem_list[i].pos_x],[self.elem_list[i].pos_y]])
                point2=np.array([[0],[-self.elem_list[i].dist/2+self.elem_list[i].element_length/2]])
                point2=(self._Rotation_matrix(-float(self.elem_list[i].tl0+self.elem_list[i].tl_all()))@point2)+np.array([[self.elem_list[i].pos_x],[self.elem_list[i].pos_y]])
                cache_array=np.concatenate((point1,point2),1)
                if i==0:
                    ax.plot(cache_array[0,:],cache_array[1,:],'-k',lw=1,label='Mirror')
                    if self.elem_list[i].is_fixed==0:
                        ax.scatter(self.elem_list[i].pos_x,self.elem_list[i].pos_y,color='k',s=pivot_size)
                    continue
                ax.plot(cache_array[0,:],cache_array[1,:],'-k',lw=1)
                if self.elem_list[i].is_fixed==0:
                    ax.scatter(self.elem_list[i].pos_x,self.elem_list[i].pos_y,color='k',s=pivot_size)
            elif self.elem_list[i].elem_type=='Lens':
                point1=np.array([[0],[self.elem_list[i].element_length/2]])
                point1=(self._Rotation_matrix(-float(self.elem_list[i].tl0+self.elem_list[i].tl_all()))@point1)+np.array([[self.elem_list[i].pos_x],[self.elem_list[i].pos_y]])
                point2=np.array([[0],[-self.elem_list[i].element_length/2]])
                point2=(self._Rotation_matrix(-float(self.elem_list[i].tl0+self.elem_list[i].tl_all()))@point2)+np.array([[self.elem_list[i].pos_x],[self.elem_list[i].pos_y]])
                cache_array=np.concatenate((point1,point2),1)
                ax.plot(cache_array[0,:],cache_array[1,:],'*-k',lw=1)

        #plotting the points
        for i in range(len(self.point_list)):
            ax.scatter(self.point_list[i].pos_x,self.point_list[i].pos_y,color=self.point_list[i].color,marker=self.point_list[i].marker,s=20,label=self.point_list[i].name)

        # Change major ticks to show every 20.
        ax.xaxis.set_major_locator(MultipleLocator(0.05))
        ax.yaxis.set_major_locator(MultipleLocator(0.05))
        # Change minor ticks to show every 5. (20/4 = 5)
        ax.xaxis.set_minor_locator(AutoMinorLocator(0.01))
        ax.yaxis.set_minor_locator(AutoMinorLocator(0.01))
        ax.minorticks_on()
        ax.grid(which='major', color='#CCCCCC', linestyle='--')
        ax.grid(which='minor', color='#CCCCCC', linestyle=':')
        ax.legend()
        if self.xy==0:
            plt.title('Layout of Optical Elements in Plane 1')
        elif self.xy==1:
            plt.title('Layout of Optical Elements in Plane 2')
        plt.xlabel('X/m')
        plt.ylabel('Y/m')
        plt.show()