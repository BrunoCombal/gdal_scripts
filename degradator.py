# -*- coding: utf-8 -*-
from __future__ import division
import gdal
import os
import copy
import numpy


class degradator():
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
	# pointers to open files
	fidIn=None
	fidOutCount=None
	fidOutVal=None


	# linear law, get a pixel count x, and rescale it between min and max.
	# x: 0-maxCount
	# val: minVal - maxVal
	# maxCount is a general parameter
	def linearLaw(self, x, minVal, maxVal):
		return minVal + x*(maxVal - minVal)/float(self.maxCount)
	# easing functions: 
	# visual examples: http://easings.net/fr
	# definitions: https://gist.github.com/gre/1650294
	# note: javascript y=(--t)*t*t translates into t=t-1, y=t*t*t
	def easeOutCubic(x, minVal, maxVal):
		t = x/float(self.maxCount) - 1
		y = t*t*t+1
		return minVal + y*(maxVal-minVal)

	def easeInOutCubic(self, x, minVal, maxVal):
		t = x/float(self.maxCount)
		if t<0.5:
			y = 4*t*t*t
		else:
			y=(t-1)*(2*t-2)*(2*t-2)+1
		return minVal + y*(maxVal-minVal)

	# open files for reading and writing.
	def openIO(self, inputFile, outputFileCount, outputFileVal):

		try:
			self.fidIn = gdal.Open(inputFile, gdal.GA_ReadOnly)
			if self.fidIn is None:
				raise IOError("Could not open input file {}".format(inputFile))
			ns = self.fidIn.RasterXSize
			nl = self.fidIn.RasterYSize
			proj = self.fidIn.GetProjection()
			gtrans = self.fidIn.GetGeoTransform()
			if self.fidIn is None:
				print "could not open input file {}".format(inputFile)
				return False
		except IOError:
			raise IOError("Error while opening input file {}".format(inputFile))

		try:
			self.fidOutCount = gdal.GetDriverByName("gtiff").Create(outputFileCount, ns, nl, 1, gdal.GDT_Byte, options=['compress=lzw','predictor=2','bigtiff=yes'])
			if self.fidOutCount is None:
				raise IOError("Could not open output file {}".format(outputFileCount))
			self.fidOutCount.SetProjection(proj)
			self.fidOutCount.SetGeoTransform(gtrans)
			self.fidOutCount.GetRasterBand(1).SetNoDataValue(self.nodataCount)

			self.fidOutVal = gdal.GetDriverByName("gtiff").Create(outputFileVal, ns, nl, 1, gdal.GDT_Float32, options=['compress=lzw','predictor=3','bigtiff=yes'])
			if self.fidOutVal is None:
				raise IOError("Could not open output file {}".format(outputFileVal))
			self.fidOutVal.SetProjection(proj)
			self.fidOutVal.SetGeoTransform(gtrans)
			self.fidOutVal.GetRasterBand(1).SetNoDataValue(self.nodataVal)

			if self.fidOutCount is None:
				print "could not open output file {}".format(outputFileCount)
				return False
			if self.fidOutVal is None:
				print "could not open output file {}".format(outputFileVal)
				return False


		except IOError, e:
			raise

		return True

	def doDegradator(self, law, *args, **kwargs):

		ns = self.fidIn.RasterXSize
		nl = self.fidIn.RasterYSize
		gdal.TermProgress(0)

		for il in xrange(1, nl-self.ks//2):
			countGrids = numpy.zeros(ns) + self.nodataCount
			thisStrip = self.fidIn.GetRasterBand(1).ReadAsArray(0, il-1, ns, self.ks)
			gdal.TermProgress(il/nl)

			for ii in xrange(self.ks//2, ns-self.ks//2):
				if thisStrip[self.ks//2][ii] in self.selectionCodes: #== detectedCode:
					thisCell = thisStrip[0:self.ks, ii- self.ks//2:ii+self.ks//2 + 1]
					if thisStrip[self.ks//2][ii] == self.TNT1:
						countGrids[ii] = self.weights[self.TNT1] * (numpy.sum( thisCell == self.TNT1)-1) + \
							self.weights[self.NTNT] * (numpy.sum(thisCell == self.NTNT))
					if thisStrip[self.ks//2][ii] == self.TNT2:
						countGrids[ii] = self.weights[self.TNT2] * (numpy.sum(thisCell == self.TNT2)-1) + \
							self.weights[self.TNT1] * (numpy.sum(thisCell == self.TNT1)) + \
							self.weights[self.NTNT] * (numpy.sum(thisCell == self.NTNT))

			self.fidOutCount.GetRasterBand(1).WriteArray(countGrids.reshape(1,-1), 0, il)
			outVal = [ law(y, *args, **kwargs) if y != self.nodataCount else self.nodataVal for y in countGrids ]
			self.fidOutVal.GetRasterBand(1).WriteArray( numpy.array(outVal).reshape(1,-1), 0, il )
		gdal.TermProgress(1)

#