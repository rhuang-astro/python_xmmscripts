#!/bin/env python
#
# Python script to extract a spectrum from the MOS1 camera
import subprocess
import glob
import os

# EDIT HERE ========================================================
os.environ['SAS_ODF'] = os.path.abspath(glob.glob('../../rpcdata/*SUM.SAS')[0])
os.environ['SAS_CCF'] = os.path.abspath(glob.glob('../../rpcdata/ccf.cif')[0])

pattern = 12
srcregionfile = 'src.reg'
bkgregionfile = 'bkg.reg'

table = 'm1_clean.ds'
srcspc = 'm1_srcspc.ds'
srcimg = 'm1_srcimg.ds'
bkgspc = 'm1_bkgspc.ds'
bkgimg = 'm1_bkgimg.ds'
rmf = 'm1.rmf'
arf = 'm1.arf'
grpspec = 'm1spec.pha'

# ++++++ Change only if necessary +++++++++++++

# specgroup parameters
mincnts = 25
oversample = 3

# max MOS channels
maxchan = 11999

# Read region informations ----------------
src = open(srcregionfile)
srcregion = src.readlines()[-1].strip()
src.close()

bkg = open(bkgregionfile)
bkgregion = bkg.readlines()[-1].strip()
bkg.close()
# ----------------------------------------

# selection expression
srcexp='expression=#XMMEA_EM && PATTERN<={1} && FLAG==0 && ((X,Y) IN {0})'.format(srcregion, pattern)
bkgexp='expression=#XMMEA_EM && PATTERN<={1} && FLAG==0 && ((X,Y) IN {0})'.format(bkgregion, pattern)

#===================================================END of EDIT Block =====

# Extracts a source+background spectrum
subprocess.call(['evselect', 'table={0}:EVENTS'.format(table),
'withspectrumset=yes', 'spectrumset={0}'.format(srcspc),
'energycolumn=PI', 'withspecranges=yes', 'spectralbinsize=5',
'specchannelmax={0}'.format(maxchan), 'specchannelmin=0',
'withimageset=yes', 'imageset={0}'.format(srcimg),
'xcolumn=X', 'ycolumn=Y', srcexp])

# Scale the areas of src and bkg regions used
subprocess.call(['backscale', 'spectrumset={0}'.format(srcspc),
'withbadpixcorr=yes', 'badpixlocation={0}'.format(table)])

# Extracts a background spectrum
subprocess.call(['evselect', 'table={0}:EVENTS'.format(table),
'withspectrumset=yes', 'spectrumset={0}'.format(bkgspc),
'energycolumn=PI', 'withspecranges=yes', 'spectralbinsize=5',
'specchannelmax={0}'.format(maxchan), 'specchannelmin=0',
'withimageset=yes', 'imageset={0}'.format(bkgimg),
'xcolumn=X', 'ycolumn=Y', bkgexp])

# Scale the are of the bkg region used
subprocess.call(['backscale', 'spectrumset={0}'.format(bkgspc),
'withbadpixcorr=yes', 'badpixlocation={0}'.format(table)])

# Generates response matrix
subprocess.call(['rmfgen', 'rmfset={0}'.format(rmf),
'spectrumset={0}'.format(srcspc)])

# Generates ana Ancillary response file
subprocess.call(['arfgen', 'arfset={0}'.format(arf),
'spectrumset={0}'.format(srcspc), '--withrmfset=yes', 'detmaptype=psf',
'rmfset={0}'.format(rmf), 'badpixlocation={0}'.format(table)])

# Rebin the spectrum and link associated files
# can be replaced by grppha tool from HEASOFT
subprocess.call(['specgroup', 'spectrumset={0}'.format(srcspc),
'mincounts={0}'.format(mincnts), 'oversample={0}'.format(oversample),
'backgndset={0}'.format(bkgspc), 'rmfset={0}'.format(rmf),
'arfset={0}'.format(arf), 'groupedset={0}'.format(grpspec)])
