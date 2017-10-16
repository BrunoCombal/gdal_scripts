# -*- coding: utf-8 -*-
import os
import degradator

#
# use degradator for a series of files.
#

indir='E:/tmp' #'//ies.jrc.it/H03/Forobs_Export/verhegghen_export/RECAREDD/dataset_RoC_exercice/1_activity_map'
outdir='E:/tmp/'

fname='Likouala_recentchangesCongo_eq_area_subset.tif'
print 'Processing {}'.format(fname)
inputFile = os.path.join(indir, fname)
outputFileCount = os.path.join(outdir,'count_weighted_easeInOutCubicOBJ_{}'.format(fname))
outputFileVal = os.path.join(outdir,'percent_weighted_easeInOutCubicOBJ_{}'.format(fname))
print outputFileCount
myDegradator1 = degradator.degradator(inputFile, outputFileCount, outputFileVal)
#myDegradator.doDegradator(fidIn, fidOutCount, fidOutVal, linearLaw, 50.0, 100.0)
#myDegradator.doDegradator(fidIn, fidOutCount, fidOutVal, easeOutCubic, 50.0, 100.0)
myDegradator1.doDegradator(myDegradator1.easeInOutCubic, 50.0, 100.0)

fname='Sangha_recentchangesCongo_eq_area_subset.tif'
print 'Processing {}'.format(fname)
inputFile = os.path.join(indir, fname)
outputFileCount = os.path.join(outdir,'count_weighted_easeInOutCubicOBJ_{}'.format(fname))
outputFileVal = os.path.join(outdir,'percent_weighted_easeInOutCubicOBJ_{}'.format(fname))
print outputFileCount
myDegradator2 = degradator.degradator(inputFile, outputFileCount, outputFileVal)
myDegradator2.doDegradator(myDegradator2.easeInOutCubic, 50.0, 100.0)

