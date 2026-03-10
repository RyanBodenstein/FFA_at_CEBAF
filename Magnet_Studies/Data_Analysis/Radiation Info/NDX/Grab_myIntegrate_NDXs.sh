#!/bin/bash
unset noclobber
#myfilename=`date +'%Y-%m-%d_'`$3
myfilename=$1'_'$2'_'$3

#echo $myfilename.'lksjdf'

# North Linac Gammas
# Currently only including those relevant to LDRD Study, not full list.

myIntegrate -c INX0L04_gDsRt -b $1 -e $2 > '0L04_Gamma_'$myfilename'.txt'
myIntegrate -c INX0L05_gDsRt -b $1 -e $2 > '0L05_Gamma_'$myfilename'.txt'
myIntegrate -c INX1L07_gDsRt -b $1 -e $2 > '1L07_Gamma_'$myfilename'.txt'
myIntegrate -c INX1L11_gDsRt -b $1 -e $2 > '1L11_Gamma_'$myfilename'.txt'
myIntegrate -c INX1L15_gDsRt -b $1 -e $2 > '1L15_Gamma_'$myfilename'.txt'
myIntegrate -c INX1L23_gDsRt -b $1 -e $2 > '1L23_Gamma_'$myfilename'.txt'
myIntegrate -c INX1L24_gDsRt -b $1 -e $2 > '1L24_Gamma_'$myfilename'.txt'
myIntegrate -c INX1L26_gDsRt -b $1 -e $2 > '1L26_Gamma_'$myfilename'.txt'

# North Linac Neutrons
# Currently only including those relevant to LDRD Study, not full list.

myIntegrate -c INX1L07_nDsRt -b $1 -e $2 > '1L07_Neutron_'$myfilename'.txt'
myIntegrate -c INX1L11_nDsRt -b $1 -e $2 > '1L11_Neutron_'$myfilename'.txt'
myIntegrate -c INX1L15_nDsRt -b $1 -e $2 > '1L15_Neutron_'$myfilename'.txt'
myIntegrate -c INX1L23_nDsRt -b $1 -e $2 > '1L23_Neutron_'$myfilename'.txt'
myIntegrate -c INX1L24_nDsRt -b $1 -e $2 > '1L24_Neutron_'$myfilename'.txt'
myIntegrate -c INX1L26_nDsRt -b $1 -e $2 > '1L26_Neutron_'$myfilename'.txt'

# South Linac Gammas
# Currently only including those relevant to LDRD Study, not full list.

myIntegrate -c INX2L04_gDsRt -b $1 -e $2 > '2L04_Gamma_'$myfilename'.txt'
myIntegrate -c INX2L07_gDsRt -b $1 -e $2 > '2L07_Gamma_'$myfilename'.txt'
myIntegrate -c INX2L08_gDsRt -b $1 -e $2 > '2L08_Gamma_'$myfilename'.txt'
myIntegrate -c INX2L17_gDsRt -b $1 -e $2 > '2L17_Gamma_'$myfilename'.txt'
myIntegrate -c INX2L22_gDsRt -b $1 -e $2 > '2L22_Gamma_'$myfilename'.txt'
myIntegrate -c INX2L23_gDsRt -b $1 -e $2 > '2L23_Gamma_'$myfilename'.txt'
myIntegrate -c INX2L24_gDsRt -b $1 -e $2 > '2L24_Gamma_'$myfilename'.txt'

# South Linac Neutrons
# Currently only including those relevant to LDRD Study, not full list.

# South Linac Gammas
# Currently only including those relevant to LDRD Study, not full list.

myIntegrate -c INX2L04_nDsRt -b $1 -e $2 > '2L04_Neutron_'$myfilename'.txt'
myIntegrate -c INX2L07_nDsRt -b $1 -e $2 > '2L07_Neutron_'$myfilename'.txt'
myIntegrate -c INX2L08_nDsRt -b $1 -e $2 > '2L08_Neutron_'$myfilename'.txt'
myIntegrate -c INX2L17_nDsRt -b $1 -e $2 > '2L17_Neutron_'$myfilename'.txt'
myIntegrate -c INX2L22_nDsRt -b $1 -e $2 > '2L22_Neutron_'$myfilename'.txt'
myIntegrate -c INX2L23_nDsRt -b $1 -e $2 > '2L23_Neutron_'$myfilename'.txt'
myIntegrate -c INX2L24_nDsRt -b $1 -e $2 > '2L24_Neutron_'$myfilename'.txt'

# 2S01
# Currently only including those relevant to LDRD Study, not full list.

myIntegrate -c INX2S01_gDsRt -b $1 -e $2 > '2S01_Gamma_'$myfilename'.txt'
myIntegrate -c INX2S01_nDsRt -b $1 -e $2 > '2S01_Neutron_'$myfilename'.txt'
