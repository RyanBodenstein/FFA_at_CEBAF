# This is a python script which calls some other libraries I wrote
# The script automatically generates a bmad lattice for FFA2 with random errors.

###############################################################################
# script library dependencies
###############################################################################
# Import basic libraries
import numpy as np
from numpy import pi
import random
import sys
# import my library of physical elements
import ele
# import library of beam parameters
import passes

###############################################################################
# script parameters
###############################################################################

Nerr = 50 # number of incidental errors in the lattice
Ncells = 63 # number of periodic cells to consider

wpass = 1 # which pass am I looking at?

#name the file to write the lattice to
# latname = 'CEBAF/ffa2_errors/ffa2_'+str(wpass)+'_'+str(Nerr)+'errors.lat'
latname = 'CEBAF/ffa2_errors/ffa2_'+str(wpass)+'_'+str(Nerr)+'errors.lat'
def pass_init(): # which pass do I want to write out?
    passes.pass1_params()

###############################################################################
# constant machine parameters
###############################################################################
#%%
ang_bf = 0.0282919900228071  # focusing magnet bend angle
len_bf = 2.38269760837842  # focusing magnet length
fld_bf = -0.732732732732733  # focusing magnet 'bending field'
grd_bf = -32.8078078078078  # focusing magnet 'focusing gradient'

ang_bd = 0.0210733759567303  # defocusing magnet bend angle
len_bd = 1.31330817709767  # defocusing magnet length
fld_bd = -0.990189900342083  # defocusing magnet 'bending field'
grd_bd = 43.3933933933934  # defocusing magnet 'focusing gradient'

lo = 0.14142135623731  # drift length parameter

# focusing magnet sagittal offset
sag_bf = 0.5*len_bf*np.sinc(0.25*ang_bf/pi)*np.sin(0.25*ang_bf)
# change in BF path length due to sagittal offset
dz_bf = 0.5*len_bf*(1-np.sinc(0.5*ang_bf/pi))
# change in BF physical length due to sagittal offset
dl_bf = dz_bf/np.cos(0.5*ang_bf)
# change in BF radial offset due to sagittal offset
dx_bf = dz_bf*np.tan(0.5*ang_bf)

# defocusing magnet sagittal offset
sag_bd = 0.5*len_bd*np.sinc(0.25*ang_bd/pi)*np.sin(0.25*ang_bd)
# change in BD path length due to sagittal offset
dz_bd = 0.5*len_bd*(1-np.sinc(0.5*ang_bd/pi))
# change in BD physical length due to sagittal offset
dl_bd = dz_bd/np.cos(0.5*ang_bd)
# change in BD radial offset due to sagittal offset
dx_bd = dz_bd*np.tan(0.5*ang_bd)



###############################################################################
# Name and 'initialize' machine parts
###############################################################################

# string that contains all the marker definitions
markerdef = 'MO1: Marker \nMO2: Marker \nMO3: Marker \nmar.beg: marker \nmar.end: marker' 

Ndr = 3*Ncells  # number of drifts in a cell times the number of cells
drifts = [None]*Ndr # array to contain all the drifts
for i in range(Ncells):  # instantialize all the drifts and name them according to their cell
    drifts[3*i] = ele.o0f(str(i+1))
    drifts[3*i+1] = ele.ofd(str(i+1))
    drifts[3*i+2] = ele.od0(str(i+1))

Nbm = 2*Ncells # number of magnets in a cell times the number of cells
mags = [None]*Nbm # array to contain all the magnets
for i in range(Ncells):  # instantialize all the magnets and name them according to their cell
    mags[2*i] = ele.bf('bf_'+str(i+1))
    mags[2*i+1] = ele.bd('bd_'+str(i+1))



###############################################################################
# Error sizes
###############################################################################

lerr = .001 # error with dimension length, in meters
aerr = .00004 # error with dimension angle, in radians
ferr = .0001
gerr = .01


###############################################################################
# categorize the errors; how many are there of each kind?
###############################################################################

nme = random.randint(0,Nerr) # number of errors on magnets
print('nme = '+str(nme))
nde = Nerr-nme # number of errors on drifts
# print('nde = '+str(nde))

nfe = random.randint(0,nme) # number of field errors
# print('nfe = '+str(nfe))
nge = random.randint(0,nme-nfe) # number of gradient erros
# print('ndge = '+str(nge))
nxe = random.randint(0,nme-nfe-nge) # number of x_offset errors
# print('nxe = '+str(nxe))
nye = random.randint(0,nme-nfe-nge-nxe) # numberof y_offset errors
# print('nye = '+str(nye))
nae = random.randint(0,nme-nfe-nge-nxe-nye) # number of angle errors
# print('nae = '+str(nae))
nmle = nme-nfe-nge-nxe-nye-nae  # number of magnet length errors
# print('nmle = '+str(nmle))

# print(str(nmle+nae+nye+nxe+nge+nfe+nde))

#%%
###############################################################################
# declare all the errors on the magnets
###############################################################################

# set magnetic field errors
field_errors = [] # stores the position of field_errors
i = 0
while i < nfe: 
    ix = random.randint(0,Nbm-1) # grab a random magnet
    # make sure the magnet hasn't been altered yet
    if mags[ix].db == 0:
        # add or subtract the differential
        mags[ix].db = ferr*((-1)**random.randrange(2))
        field_errors.append(mags[ix].name) # store the position of the error 
        i = i+1 # increment


# set gradient errors
grad_errors = [] # stores the position of gradient errors
i = 0
while i < nge: 
    ix = random.randint(0, Nbm-1)  # grab a random magnet
    # make sure the magnet hasn't been altered yet
    if mags[ix].db1g == 0:
        # add or subtract the differential
        mags[ix].db1g = gerr*((-1)**random.randrange(2))
        grad_errors.append(mags[ix].name)  # store the position of the error
        i = i+1  # increment

# set x_offset errors
x_errors = [] # stores the position of x_offset errors
i = 0
while i < nxe: 
    ix = random.randint(0, Nbm-1)  # grab a random magnet
    if mags[ix].dx == 0:  # make sure the magnet hasn't been altered yet
        # add or subtract the differential
        mags[ix].dx = lerr*((-1)**random.randrange(2))
        x_errors.append(mags[ix].name)  # store the position of the error
        i = i+1  # increment

# set y_offset errors
y_errors = [] # stores the position of y_offset errors
i = 0
while i < nye:
    ix = random.randint(0, Nbm-1)  # grab a random magnet
    if mags[ix].y == 0:  # make sure the magnet hasn't been altered yet
        # add or subtract the differential
        mags[ix].y = lerr*((-1)**random.randrange(2))
        y_errors.append(mags[ix].name)  # store the position of the error
        i = i+1  # increment

# set tilt errors
angle_errors = [] # stores the position of angular errors
i = 0
while i < nae: 
    ix = random.randint(0, Nbm-1)  # grab a random magnet
    # make sure the magnet hasn't been altered yet
    if mags[ix].da == 0:
        # add or subtract the differential
        mags[ix].da = aerr*((-1)**random.randrange(2))
        angle_errors.append(mags[ix].name)  # store the position of the error
        i = i+1  # increment

# set magnet length errors
l_errors = [] # stores the position of length errors
i = 0
while i < nmle:
    ix = random.randint(0, Nbm-1)  # grab a random magnet
    # make sure the magnet hasn't been altered yet
    if mags[ix].dl == 0:
        # add or subtract the differential
        mags[ix].dl = lerr*((-1)**random.randrange(2))
        l_errors.append(mags[ix].name)  # store the position of the error
        i = i+1  # increment


###############################################################################
# declare all the errors on the drifts
###############################################################################

drift_errors = [] # stores the position of drift errors
i = 0
while i < nde: 
    ix = random.randint(0, Ndr-1) # grab a random drift
    if drifts[ix].dl == 0:  # make sure the drift hasn't been altered yet
        # add or subtract the differential
        drifts[ix].dl = lerr*((-1)**random.randrange(2))
        drift_errors.append(drifts[ix].name)  # store the position of the error
        i = i+1  # increment

# print('nde = '+str(nde))
# print('len(drift_errors) = '+str(len(drift_errors)))
# print('nfe = '+str(nfe))
# print('len(field_errors) = '+str(len(field_errors)))
# print('nge = '+str(nge))  # number of gradient erros
# print('len(grad_errors) = '+str(len(grad_errors)))
# print('nxe = '+str(nxe))  # number of x_offset errors
# print('len(x_errors) = '+str(len(x_errors)))
# print('nye = '+str(nye))  # numberof y_offset errors
# print('len(y_errors) = '+str(len(y_errors)))
# print('nae = '+str(nae)) # number of angle errors
# print('len(angle_errors) = '+str(len(angle_errors)))
# print('nmle = '+str(nmle))  # number of magnet length errors
# print('len(l_errors) = '+str(len(l_errors)))

# print(str(nmle+nae+nye+nxe+nge+nfe+nde))
# print(len(drift_errors)+len(field_errors)+len(grad_errors)+len(x_errors)+len(y_errors)+len(angle_errors)+len(l_errors))
#%%
###############################################################################
# make one array that holds the lattice
###############################################################################

lat = [] # array to hold the lattice
for i in range(Ncells): # in groups of 5 (cell size) match the lattice element to the array it lives in
    lat.append(drifts[3*i])
    lat.append(mags[2*i])
    lat.append(drifts[3*i+1])
    lat.append(mags[2*i+1])
    lat.append(drifts[3*i+2])


# does the lattice come together the way I want it to?
# for i in range(len(drifts)):
#     print(lat[i])

#%%%

###############################################################################
# At last, we print the whole thing out
###############################################################################

orig_stdout = sys.stdout # save reference to terminal print

with open(latname, 'a+') as f:
    sys.stdout = f # make all the following print statements write to the lattice file

    print('! '+latname)
    print('! '+'Arc FFA2')
    print('! '+'FFA2 pass '+str(wpass)+' with random errors in the lattice')
    print('\n')

    # print the beam parameters for the current pass
    print('! The beam parameters come from the tuning of the ideal lattice')
    pass_init()

    print('! The lattice has the following errors;')
    print('! note that the sign of the error is also random.')
    print('\n')
    # print comments labeling field errors
    if nfe > 0:
        for i in range(len(field_errors)):
            print('! ' + field_errors[i] +
                ' has a magnetic field error of size '+str(ferr))
        print('!--')

    # print comments labeling gradient errors
    if nge > 0:
        for i in range(len(grad_errors)):
            print('! ' + grad_errors[i] +
                ' has a magnetic gradient error of size '+str(gerr))
        print('!--')

    # print comments labeling x_offset errors
    if nxe > 0:
        for i in range(len(x_errors)):
            print('! ' + x_errors[i]+
                ' has an x_offset error of size '+str(lerr))
        print('!--')

    # print comments labeling y_offset errors
    if nye > 0:
        for i in range(len(y_errors)):
            print('! ' + y_errors[i] +
                ' has a y_offset error of size '+str(lerr))
        print('!--')

    # print comments labeling tilt errors
    if nae > 0:
        for i in range(len(angle_errors)):
            print('! ' + angle_errors[i] +
                ' has a tilt error of size '+str(aerr))
        print('!--')

    # print comments labeling magnet length errors
    if nmle > 0:
        for i in range(len(l_errors)):
            print('! ' + l_errors[i] +
                ' has a magnet length error of size '+str(lerr))
        print('!--')

    # print comments labeling drift length errors
    if nde > 0:
        for i in range(len(drift_errors)):
            print('! ' + drift_errors[i] +
                ' has a drift length error of size '+str(lerr))
        print('!--')


    print('\n')
    print('!----------------------------------------------------')
    print('\n')


    # print out the element definitions for the physical lattice elements
    for i in range(len(lat)):
        lat[i].ele_def() # since we cleverly gave all the element classes the same method names

    print(markerdef) # print out the marker definitions last.

    print('\n')
    print('!----------------------------------------------------')
    print('\n')

    # print out the structure of the lattice
    print('FFA2: line = (mar.beg, ')
    for i in range(len(lat)):
        lat[i].lat_seg()
    print('           '+'mar.end)\n')

    # tell Bmad to use the ugly trollop you just built.
    print('use, FFA2')
    sys.stdout = orig_stdout # put things back the way they were, just in case.
