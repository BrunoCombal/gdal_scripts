# -*- coding: utf-8 -*-
from __future__ import division
import gdal
import os
import copy
import numpy

ks=3 #kernel size
detectedCode = 3

def linearLaw(x, minVal, maxVal):
	return minVal + x*(maxVal - minVal)/8.0

def openIO(inputFile, outputFileCount, outputFileVal):
	fidIn=None
	fidOutCount=None
	fidOutVal=None

	try:
		fidIn = gdal.Open(inputFile, gdal.GA_ReadOnly)
		ns = fidIn.RasterXSize
		nl = fidIn.RasterYSize
		proj = fidIn.GetProjection()
		gtrans = fidIn.GetGeoTransform()
		
		fidOutCount = gdal.GetDriverByName("gtiff").Create(outputFileCount, ns, nl, 1, gdal.GDT_Byte, options=['compress=lzw','predictor=2','bigtiff=yes'])
		fidOutCount.SetProjection(proj)
		fidOutCount.SetGeoTransform(gtrans)

		fidOutVal = gdal.GetDriverByName("gtiff").Create(outputFileVal, ns, nl, 1, gdal.GDT_Float32, options=['compress=lzw','predictor=3','bigtiff=yes'])
		fidOutVal.SetProjection(proj)
		fidOutVal.SetGeoTransform(gtrans)
	except IOError, e:
		raise("Error when opening files, {}".format(e))


	return fidIn, fidOutCount, fidOutVal

def doDegradator(fidIn, fidOutCount, fidOutVal, law, *args, **kwargs):

	ns = fidIn.RasterXSize
	nl = fidIn.RasterYSize

	for il in xrange(1, nl-ks//2):
		countGrids = numpy.zeros(ns)+255
		thisStrip = fidIn.GetRasterBand(1).ReadAsArray(0, il-1, ns, ks)

		for ii in xrange(ks//2, ns-ks//2):
			if thisStrip[ks//2][ii] == detectedCode:
				thisCell = thisStrip[0:ks, ii- ks//2:ii+ks//2 + 1]
				countGrids[ii] = numpy.sum( thisCell == detectedCode)-1
				#print ii, il, thisCell.shape

		fidOutCount.GetRasterBand(1).WriteArray(countGrids.reshape(1,-1), 0, il)
		outVal = [ law(y, *args, **kwargs) if y != 255 else -1 for y in countGrids ]
		fidOutVal.GetRasterBand(1).WriteArray(numpy.array(outVal).reshape(1,-1), 0, il)


if __name__=="__main__":
	inputFile='E:/impact/IMPACT/DATA/sangha/clip_offset_Sangha_recentchangesCongo_eq_area.tif'
	outputFileCount='E:/tmp/test_count.tif'
	outputFileVal='e:/tmp/test_value.tif'

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


	doDegradator(fidIn, fidOutCount, fidOutVal, linearLaw, 50, 100)