#%%
import numpy as np
from numpy import pi
import pandas as pd
#%%

###############################################################################
# Machine constants
###############################################################################


ang_bf = 0.0282919900228071 # focusing magnet bend angle
len_bf = 2.38269760837842 # focusing magnet length
fld_bf = -0.732732732732733 # focusing magnet 'bending field'
grd_bf = -32.8078078078078 # focusing magnet 'focusing gradient'

ang_bd = 0.0210733759567303 # defocusing magnet bend angle
len_bd = 1.31330817709767 # defocusing magnet length
fld_bd = -0.990189900342083  # defocusing magnet 'bending field'
grd_bd = 43.3933933933934 # defocusing magnet 'focusing gradient'

lo = 0.14142135623731 # drift length parameter

sag_bf = 0.5*len_bf*np.sinc(0.25*ang_bf/pi)*np.sin(0.25*ang_bf) # focusing magnet sagittal offset
dz_bf = 0.5*len_bf*(1-np.sinc(0.5*ang_bf/pi)) # change in BF path length due to sagittal offset
dl_bf = dz_bf/np.cos(0.5*ang_bf) # change in BF physical length due to sagittal offset
dx_bf = dz_bf*np.tan(0.5*ang_bf) # change in BF radial offset due to sagittal offset

sag_bd = 0.5*len_bd*np.sinc(0.25*ang_bd/pi)*np.sin(0.25*ang_bd) # defocusing magnet sagittal offset
dz_bd = 0.5*len_bd*(1-np.sinc(0.5*ang_bd/pi)) # change in BD path length due to sagittal offset
dl_bd = dz_bd/np.cos(0.5*ang_bd) # change in BD physical length due to sagittal offset
dx_bd = dz_bd*np.tan(0.5*ang_bd) # change in BD radial offset due to sagittal offset

#%%
###############################################################################
# magnet classes
###############################################################################

class bf: # define focusing magnets with optional errors
    def __init__(self, name):
        self.name = name # name of element; eventually these will be machine names
        self.l = len_bf  # element length
        self.dl = 0 # length modifier
        self.x = sag_bf/1.5+dx_bf # sagittal x_offset
        self.dx = 0 # error x offset
        self.y = 0 # element y_offset: 0 by default
        self.ang = ang_bf  # element bending angle
        self.da = 0 # angle modifier
        self.field = fld_bf  # element bending field
        self.db = 0 # field modifier
        self.grad = grd_bf  # element field gradient
        self.db1g = 0 # gradient modifier

    def ele_def(self): # class method to print the element definitions to text
        print(self.name+'_p_in: patch, x_pitch = '+str(-0.5*(self.ang+self.da))+
              ', x_offset = '+str(self.x + self.dx)+', y_offset = '+str(self.y))
        print(self.name+': sbend, l='+str(self.l+self.dl)+
              ', db_field = '+str(self.field+self.db)+', b1_gradient = '+str(self.grad+self.db1g))
        print(self.name+'_p_out: patch, x_pitch = '+str(-0.5*(self.ang+self.da)) +
              ', x_offset = '+str(-self.x + self.dx)+', y_offset = '+str(self.y))

    def lat_seg(self): # class method to print the lattice segment for these elements
        print('              '+self.name+'_p_in, ' +
              self.name+', '+self.name+'_p_out, ')


class bd:
    def __init__(self, name):
        self.name = name  # name of element; eventually these will be machine names
        self.l = len_bd   # element length
        self.dl = 0  # length modifier
        self.x = -(sag_bf/1.5+dx_bd)  # sagittal x_offset
        self.dx = 0 # error offset
        self.y = 0  # element y_offset: 0 by default
        self.ang = ang_bd   # element bending angle
        self.da = 0  # angle modifier
        self.field = fld_bd   # element bending field
        self.db = 0  # field modifier
        self.grad = grd_bd   # element field gradient
        self.db1g = 0  # gradient modifier

    def ele_def(self):  # class method to print the element definitions to text
        print(self.name+'_p_in: patch, x_pitch = '+str(-0.5*(self.ang+self.da)) +
              ', x_offset = '+str(self.x + self.dx)+', y_offset='+str(self.y))
        print(self.name+': sbend, l = '+str(self.l + self.dl) +
              ', db_field = '+str(self.field + self.db)+', b1_gradient = '+str(self.grad + self.db1g))
        print(self.name+'_p_out: patch, x_pitch = '+str(-0.5*(self.ang+self.da)) +
              ', x_offset = '+str(-self.x + self.dx)+', y_offset = '+str(self.y))


    def lat_seg(self):  # class method to print the lattice segment for these elements
        print('              '+self.name+'_p_in, ' +
              self.name+', '+self.name+'_p_out, ')


###############################################################################
# drift classes
###############################################################################

class o0f:
    def __init__(self, dname):
        self.name = 'o0f_'+dname  # name of element; eventually these will be machine names
        self.dl = 0  # presume the length error is 0
        self.l = 0.5*lo-dl_bf  # element length

    def ele_def(self):  # class method to print the element definitions to text
        print(self.name+': drift, l = '+str(self.l+self.dl))

    def lat_seg(self):  # class method to print the lattice segment for these elements
        print('              '+self.name+', MO1, ')


class ofd:
    def __init__(self, dname):
        self.name = 'ofd_'+dname  # name of element; eventually these will be machine names
        self.dl = 0 # presume the length error is 0
        self.l = lo-dl_bf-dl_bd  # element length

    def ele_def(self):  # class method to print the element definitions to text
        print(self.name+': drift, l = '+str(self.l+self.dl))

    def lat_seg(self):  # class method to print the lattice segment for these elements
        print('              '+self.name+', MO2, ')


class od0:
    def __init__(self, dname):
        self.name = 'od0_'+dname  # name of element; eventually these will be machine names
        self.dl = 0  # presume the length error is 0
        self.l = 0.5*lo-dl_bd  # element length

    def ele_def(self):  # class method to print the element definitions to text
        print(self.name+': drift, l = '+str(self.l+self.dl))
        print('\n')

    def lat_seg(self):  # class method to print the lattice segment for these elements
        print('              '+self.name+', MO3,')
        

#%%


# %%
