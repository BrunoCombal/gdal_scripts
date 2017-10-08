import gdal
import gdalconst
import numpy
import sys

#inFile = 'E:/data/tanzania/GEE_export/radarLIN2months/out/corrected_diff_mean.tif'
#inFile = 'E:/data/tanzania/GEE_export/radarLIN2months/out/corrected_diff_mean.tif'
inFile = 'E:/data/tanzania/GEE_export/radarLIN2months/radarLIN_mean_Tanzania_2016.vrt'
inFid = gdal.Open(inFile, gdalconst.GA_ReadOnly)
maskFile = 'E:/data/tanzania/GEE_export/forest_samples_mask.tif'
maskFid = gdal.Open(maskFile, gdalconst.GA_ReadOnly)
#outFile = 'E:/data/tmp/corrected_diff_mean_gt_0.854.tif'
#outFile = 'E:/data/tanzania/GEE_export/forest_samples_mask.tif'

ns = inFid.RasterXSize
nl = inFid.RasterYSize

#outDrv = gdal.GetDriverByName('gtiff')
#outDs = outDrv.Create(outFile, ns, nl, 1, gdalconst.GDT_Byte, ['compress=lzw','bigtiff=yes'])
#outDs.SetProjection(inFid.GetProjection())
#outDs.SetGeoTransform(inFid.GetGeoTransform())

gdal.TermProgress = gdal.TermProgress_nocb
#mask = numpy.zeros(ns)
total = 0
NTotal = 0
lineHeight = 1
collection = None
for il in xrange(0, nl, lineHeight):
	try:
		mask = numpy.ravel(maskFid.GetRasterBand(1).ReadAsArray(0, il, ns, lineHeight))
		wtsum = mask > 0
		if wtsum.any():
			data = numpy.ravel(inFid.GetRasterBand(1).ReadAsArray(0, il, ns, lineHeight))
			NTotal = NTotal + numpy.sum(wtsum)
			total = total + sum( data[wtsum] )
			if collection is None:
				collection = numpy.array(data[wtsum])
			else:
				collection = numpy.append(collection, numpy.ravel(data[wtsum]))
		#mask = data > 0.854
		#outDs.GetRasterBand(1).WriteArray(mask.reshape(1,-1), 0, il)
			if NTotal > 0:
				print il, total, NTotal, total/NTotal

		#gdal.TermProgress(il/nl)
	except:
		print 'Error!', il
		print data
		print 'return from error'
		#print wtp

print total, NTotal, total/NTotal
collection = numpy.array(collection)
print collection.shape
print 'Collection.size = {}; min = {}, mean = {}, max = {}, std = {}'.format(collection.size, collection.min(), collection.mean(), collection.max(), collection.std())

gdal.TermProgress(1)
outDs = None



