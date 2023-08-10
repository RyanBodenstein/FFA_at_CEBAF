# corr-aperture.py
# this is a python script which will find the 
# 'dynamic' acceptance aperture of each FFA arc
# for CEBAF:
#
# To do so, I'll use the optics taken from the 
# closed orbit solution at each energy, and 
# vary "particle_start[x,px]" to find the acceptance 
# aperture in that phase plane.

# this version uses the correctors to adjust as well.
# import statements
import pytao
from pytao import Tao

# import matplotlib as mpl
# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# define some constants to make life livable
in1 = 'python data_parameter '
taodx = '@orbit.xval[77] design_value'
taomx = '@orbit.xval[77] model_value'
taodpx = '@orbit.pxval[77] design_value'
taompx = '@orbit.pxval[77] model_value'

x0 = np.zeros(6)
resetx = [None]*6
px0 = np.zeros((6,16))
resetpx = [None]*6

dx0 = .001 # initial size of aperture step
dpx0 = .001 # initial size of aperture step
dx = dx0
dpx = dpx0


tao = Tao("-init tao.init -noplot") # initialize Tao in this folder



for i in range(1,7):
    # first generate strings to issue to tao
    stringx = in1 + str(i) + taodx
    stringpx = in1 + str(i) +taodpx
    # get the design particle_start[x] for each universe
    x0[i-1] = float(tao.cmd(str(stringx))[0].lstrip('1;'))
    # generate a string to reset to design
    resetx[i-1] = 'set particle_start '+str(i)+'@x = '+str(x0[i-1])
    # get the design particle_start[px] for each universe
    px0[i-1] = [float(tao.cmd(str(stringpx))[0].lstrip('1;')) for j in range(16)]
    # generate a string to reset to design
    resetpx[i-1] = 'set particle_start '+str(i)+'@px = '+str(px0[i-1][0])



x_max_in = np.array(x0)
x_min_in = np.array(x0)





for i in range(1,7):
    # commands to move the start in x
    cxp = 'change '+str(i)+'@particle_start x ' # add to x0
    cxm = 'change '+str(i)+'@particle_start x -' # subtract from x0
    # command to return the value of the orbit at the end of the lattice
    ovalx = in1 + str(i) + taomx
    print('now calculating x_max for uni '+str(i))
    # for really set the limiting value from tao
    ival = in1 + str(i) + '@orbit.xval[76] model_value'
    while (dx >= 10**(-6)): # step in successively finer increments
        
        cxpd = cxp + str(dx) # command to increment
        cxmd = cxm + str(dx) # command to decrement

        tao.cmd(str(cxpd),raises=False) # issue command to increment
        
        # now grab the value at the end of the lattice
        xval = float(tao.cmd(str(ovalx))[0].lstrip('1;'))

        if(xval !=0): # check if the particle made it through
            x_max_in[i-1] = float(tao.cmd(str(ival))[0].lstrip('1;')) # update the aperture limit
        
        else: # if it didn't, go back and make the step smaller
            # tao.cmd('run_optimizer de', raises = False)
            tao.cmd('run_optimizer lmdif', raises = False)
            xval = float(tao.cmd(str(ovalx))[0].lstrip('1;'))
            if (xval != 0):
                x_max_in[i-1] = float(tao.cmd(str(ival))[0].lstrip('1;')) # update the aperture limit
            else: 
                tao.cmd(str(cxmd))
                dx = dx/10
    dx = dx0 # after each universe, reset the step size

# print('\n now the other side\n')


for i in range(1,7):
    # commands to move the start in x
    cxp = 'change '+str(i)+'@particle_start x ' # add to x0
    cxm = 'change '+str(i)+'@particle_start x -' # subtract from x0
    # command to return the value of the orbit at the end of the lattice
    ovalx = in1 + str(i) + taomx
    print('now calculating x_min for uni '+str(i))
    # for really set the limiting value from tao
    ival = in1 + str(i) + '@orbit.xval[76] model_value'
    while (dx >= 10**(-6)): # step in successively finer increments
        
        cxpd = cxp + str(dx) # command to increment
        cxmd = cxm + str(dx) # command to decrement

        tao.cmd(str(cxmd),raises=False) # issue command to increment
        
        # now grab the value at the end of the lattice
        xval = float(tao.cmd(str(ovalx))[0].lstrip('1;'))
        
        if(xval !=0): # check if the particle made it through
            x_min_in[i-1] = float(tao.cmd(str(ival))[0].lstrip('1;')) # update the aperture limit
        
        else: # if it didn't, go back and make the step smaller
            # tao.cmd('run_optimizer de', raises = False)
            tao.cmd('run_optimizer lmdif', raises = False)
            xval = float(tao.cmd(str(ovalx))[0].lstrip('1;'))
            if (xval != 0):
                x_max_in[i-1] = float(tao.cmd(str(ival))[0].lstrip('1;')) # update the aperture limit
            else: 
                tao.cmd(str(cxpd))
                dx = dx/10


    dx = dx0 # after each universe, reset the step size
            

# generate array of x values spanning the aperture for each universe
xvals = [[x_min_in[i-1]+j*(x_max_in[i-1]-x_min_in[i-1])/15 for j in range(16)] for i in range(1,7)]



px_max_in = np.array(px0)
px_min_in = np.array(px0)


for i in range(1,7): # loop over universes
    for j in range(len(xvals[i-1])): #loop over the resolution in x
        print('now calculating px_max for uni '+str(i),'and xval #'+str(j))
        tao.cmd(str(resetpx[i-1]),raises = False) # set momentum to closed orbit for that universe
        # command to set the start x
        sx = 'set particle_start '+str(i)+'@x = '+str(xvals[i-1][j])
        # print(sx)
        tao.cmd(str(sx), raises=False)
        # commands to increment the momentum
        cpxp = 'change '+str(i)+'@particle_start px '
        cpxm = 'change '+str(i)+'@particle_start px -'
        # command to get the orbit at the lattice exit
        ovalx = in1 + str(i) + taomx
        ovalp = in1 + str(i) + taompx
        # for really set the limiting value from tao
        ival = in1 + str(i) + '@orbit.pxval[76] model_value'
        while (dpx >= 10**(-6)): 
            cpxpd = cpxp + str(dpx)
            cpxmd = cpxm + str(dpx)
            tao.cmd(str(cpxpd),raises=False) 
            val = float(tao.cmd(str(ovalx))[0].lstrip('1;'))
            if(val !=0):
                px_max_in[i-1][j] = float(tao.cmd(str(ival))[0].lstrip('1;'))
            else:
                # tao.cmd('run_optimizer de', raises = False)
                tao.cmd('run_optimizer lmdif', raises = False)
                pxval = float(tao.cmd(str(ovalx))[0].lstrip('1;'))
                if (pxval != 0):
                    px_max_in[i-1][j] = float(tao.cmd(str(ival))[0].lstrip('1;'))
                else: 
                    tao.cmd(str(cpxmd))
                    dpx = dpx/10

        dpx = dpx0




# this is the same as the last guy with + and - switched.
for i in range(1,7):
    for j in range(len(xvals[i-1])):
        print('now calculating px_min for uni '+str(i),'and xval #'+str(j))
        tao.cmd(str(resetpx[i-1]), raises=False)
        sx = 'set particle_start '+str(i)+'@x = '+str(xvals[i-1][j])
        tao.cmd(str(sx), raises=False)
        cpxp = 'change '+str(i)+'@particle_start px '
        cpxm = 'change '+str(i)+'@particle_start px -'
        ovalx = in1 + str(i) + taomx
        
        # for really set the limiting value from tao
        ival = in1 + str(i) + '@orbit.pxval[76] model_value'
        while (dpx >= 10**(-6)):
            cpxpd = cpxp + str(dpx)
            cpxmd = cpxm + str(dpx)
            tao.cmd(str(cpxmd),raises=False)
            val = float(tao.cmd(str(ovalx))[0].lstrip('1;'))
            if(val !=0):
                px_max_in[i-1][j] = float(tao.cmd(str(ival))[0].lstrip('1;'))
            else:
                # tao.cmd('run_optimizer de', raises = False)
                tao.cmd('run_optimizer lmdif', raises = False)
                pxval = float(tao.cmd(str(ovalx))[0].lstrip('1;'))
                if (pxval != 0):
                    px_max_in[i-1][j] = float(tao.cmd(str(ival))[0].lstrip('1;'))
                else: 
                    tao.cmd(str(cpxpd),raises=False)
                    dpx = dpx/10

        dpx = dpx0



# print those lovely results to a file, please
for i in range(1,7):
    filename = 'Apert/East_Uni_'+str(i)+'_corr.dat'
    output_df = pd.DataFrame({'x': xvals[i-1],'pxmin': px_min_in[i-1],'pxmax': px_max_in[i-1]})
    output_df.to_csv(path_or_buf=filename, sep = ',')
