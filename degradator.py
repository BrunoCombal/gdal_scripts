# -*- coding: utf-8 -*-
from __future__ import division
import gdal
import os
import copy
import numpy

ks = 3 #kernel size
nodataCount=255
nodataVal=-1
#detectedCode = 3
ND = 0
TT = 1
NTNT = 2
TNT1 = 3
TNT2 = 4
selectionCodes = [TNT1, TNT2]
weights = {ND:0, TT:0, NTNT:2, TNT1:1, TNT2:1}
maxCount = (ks * ks - 1) *max(ND, TT, NTNT, TNT1, TNT2)
gdal.TermProgress = gdal.TermProgress_nocb


# linear law, get a pixel count x, and rescale it between min and max.
# x: 0-maxCount
# val: minVal - maxVal
# maxCount is a general parameter
def linearLaw(x, minVal, maxVal):
	return minVal + x*(maxVal - minVal)/float(maxCount)
# easing functions: 
# visual examples: http://easings.net/fr
# definitions: https://gist.github.com/gre/1650294
# note: javascript y=(--t)*t*t translates into t=t-1, y=t*t*t
def easeOutCubic(x, minVal, maxVal):
	t = x/float(maxCount) - 1
	y = t*t*t+1
	return minVal + y*(maxVal-minVal)
def easeInOutCubic(x, minVal, maxVal):
	t = x/float(maxCount)
	if t<0.5:
		y = 4*t*t*t
	else:
		y=(t-1)*(2*t-2)*(2*t-2)+1
	return minVal + y*(maxVal-minVal)

# open files for reading and writing.
def openIO(inputFile, outputFileCount, outputFileVal):
	fidIn=None
	fidOutCount=None
	fidOutVal=None

	try:
		fidIn = gdal.Open(inputFile, gdal.GA_ReadOnly)
		if fidIn is None:
			raise("Could not open input file {}".format(inputFile))
		ns = fidIn.RasterXSize
		nl = fidIn.RasterYSize
		proj = fidIn.GetProjection()
		gtrans = fidIn.GetGeoTransform()
	except IOError:
		raise("Error while opening input file {}".format(inputFile))

	try:
		fidOutCount = gdal.GetDriverByName("gtiff").Create(outputFileCount, ns, nl, 1, gdal.GDT_Byte, options=['compress=lzw','predictor=2','bigtiff=yes'])
		if fidOutCount is None:
			raise("Could not open output file {}".format(outputFileCount))
		fidOutCount.SetProjection(proj)
		fidOutCount.SetGeoTransform(gtrans)
		fidOutCount.GetRasterBand(1).SetNoDataValue(nodataCount)

		fidOutVal = gdal.GetDriverByName("gtiff").Create(outputFileVal, ns, nl, 1, gdal.GDT_Float32, options=['compress=lzw','predictor=3','bigtiff=yes'])
		if fidOutVal is None:
			raise("Could not open output file {}".format(outputFileVal))
		fidOutVal.SetProjection(proj)
		fidOutVal.SetGeoTransform(gtrans)
		fidOutVal.GetRasterBand(1).SetNoDataValue(nodataVal)

	except IOError, e:
		raise("Error when opening files, {}".format(e))


	return fidIn, fidOutCount, fidOutVal

def doDegradator(fidIn, fidOutCount, fidOutVal, law, *args, **kwargs):

	ns = fidIn.RasterXSize
	nl = fidIn.RasterYSize
	gdal.TermProgress(0)

	for il in xrange(1, nl-ks//2):
		countGrids = numpy.zeros(ns) + nodataCount
		thisStrip = fidIn.GetRasterBand(1).ReadAsArray(0, il-1, ns, ks)
		gdal.TermProgress(il/nl)

		for ii in xrange(ks//2, ns-ks//2):
			if thisStrip[ks//2][ii] in selectionCodes: #== detectedCode:
				thisCell = thisStrip[0:ks, ii- ks//2:ii+ks//2 + 1]
				if thisStrip[ks//2][ii] == TNT1:
					countGrids[ii] = weights[TNT1] * (numpy.sum( thisCell == TNT1)-1) + \
						weights[NTNT] * (numpy.sum(thisCell == NTNT))
				if thisStrip[ks//2][ii] == TNT2:
					countGrids[ii] = weights[TNT2] * (numpy.sum(thisCell == TNT2)-1) + \
						weights[TNT1] * (numpy.sum(thisCell == TNT1)) + \
						weights[NTNT] * (numpy.sum(thisCell == NTNT))
				#print ii, il, thisCell.shape

		fidOutCount.GetRasterBand(1).WriteArray(countGrids.reshape(1,-1), 0, il)
		outVal = [ law(y, *args, **kwargs) if y != nodataCount else nodataVal for y in countGrids ]
		fidOutVal.GetRasterBand(1).WriteArray(numpy.array(outVal).reshape(1,-1), 0, il)
	gdal.TermProgress(1)
#
# main calls the code for a series of files
#
if __name__=="__main__":

	indir='//ies.jrc.it/H03/Forobs_Export/verhegghen_export/RECAREDD/dataset_RoC_exercice/1_activity_map'
	outdir='E:/tmp/'
	for fname in ['Likouala_recentchangesCongo_eq_area.tif', 'Sangha_recentchangesCongo_eq_area.tif']:
		print 'Processing {}'.format(fname)
		inputFile = os.path.join(indir, fname)
		outputFileCount = os.path.join(outdir,'count_weighted_easeInOutCubic_{}'.format(fname))
		outputFileVal = os.path.join(outdir,'percent_weighted_easeInOutCubic_{}'.format(fname))
		print outputFileCount

		try:
			fidIn, fidOutCount, fidOutVal = openIO(inputFile, outputFileCount, outputFileVal)
			if fidIn is None:
				print "could not open input file {}".format(inputFile)
				sys.exit(1)
			if fidOutCount is None:
				print "could not open output file {}".format(outputFileCount)
				sys.exit(1)
			if fidOutVal is None:
				print "could not open output file {}".format(outputFileVal)
				sys.exit(1)


			#doDegradator(fidIn, fidOutCount, fidOutVal, linearLaw, 50.0, 100.0)
			#doDegradator(fidIn, fidOutCount, fidOutVal, easeOutCubic, 50.0, 100.0)
			doDegradator(fidIn, fidOutCount, fidOutVal, easeInOutCubic, 50.0, 100.0)
		except IOError, e:
			raise("IOError {}".format(e))
		except Exception, e:
			raise("Error {}".format(e))

		fidIn=None
		fidOutCount=None
		fidOutVal=None
