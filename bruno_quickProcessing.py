import gdal
import gdalconst
import numpy
import sys

inFile = 'E:/data/tanzania/unredd_land_use_2013.tif'
outFile = 'E:/data/tanzania/forest_strata_from_unredd.tif'

inFid = gdal.Open(inFile, gdalconst.GA_ReadOnly)
ns = inFid.RasterXSize
nl = inFid.RasterYSize

outDrv = gdal.GetDriverByName('gtiff')
outDs = outDrv.Create(outFile, ns, nl, 1, gdalconst.GDT_Byte, ['compress=lzw','bigtiff=yes'])
outDs.SetProjection(inFid.GetProjection())
outDs.SetGeoTransform(inFid.GetGeoTransform())

lstValues = [4, 3, 2, 1, ]

for il in xrange(0, nl, 1):
	try:
		data = numpy.ravel(inFid.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
		# now keep values in our list
		mask = numpy.zeros(ns)
		for ii in lstValues:
			mask = mask + (data == ii)
		
		outDs.GetRasterBand(1).WriteArray(mask.reshape(1,-1), 0, il)

	except:
		print 'Error!', il


outDs = None



