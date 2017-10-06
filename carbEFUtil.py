# -*- coding: utf-8 -*-
import gdal
import os
import copy
from __future__ import division
import carbEFObj

def rasterAlign(outPath, outFname, outType, refNL, refNS, refProjection, refGeotransform, rasterIN, resampleType='near'):
	"""lit un objet raster, cree un fichier warped, avec les memes proprietes, 
		puis le transforme en objet raster.
	"""

	# check type:
	if isinstance(rasterIN, raster):
		self.rasterIN = rasterIN
	else:
		raise("carbEFObj.rasterWarp.__init__: rasterIN must be an instance of raster.")

	ul = pixelToMap(0, 0, refGeotransform)
	lr = pixelToMap(refNS, refNL, refGeotransform)
	outputBounds = ( min(ul[0], lr[0]), min(ul[1],lr[1]), max(ul[0],lr[0]), max(ul[1],lr[1]) )
	inDatatype = rasterIN.parameters['dataType']
	role = rasterIN.role

	imgToAlign = os.path.join(rasterIN.path, rasterIN.fname)
	aligned = os.path.join(outPath, outFname)

	try:
		if outType is not None:
			print 'Warp casting {} to data type {}'.format(imgToAlign, outType)
			gdal.Warp(aligned, imgToAlign, dstSRS = refProjection, dstNodata = 0,\
					outputBounds = outputBounds, outputBoundsSRS = refProjection,\
					xRes=abs(refGeotransform[1]), yRes=abs(refGeotransform[5]), \
					outputType = outType,\
					resampleAlg = resampleType, format='Gtiff', options=['compress=lzw','bigtiff=YES'])

		else:
			print 'Warp keeps {} original data type as input data type {}'.format(imgToAlign, inDatatype)
			gdal.Warp(aligned, imgToAlign, dstSRS=proj, dstNodata = 0,\
					outputBounds=outputBounds, outputBoundsSRS=refProjection,\
					xRes=abs(refGeotransform[1]), yRes=abs(refGeotransform[5]),\
					resampleAlg=resampleType, format='Gtiff', options=['compress=lzw','bigtiff=YES'])
	except:
		raise("cabEFUtil.rasterAlign: error when warping images")

	alignedRaster = raster(outPath, outFname, role)

	return alignedRaster

