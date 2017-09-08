import gdal
import gdalconst
import numpy
import sys
import os.path
import geotransform

def doCutRescale(name, lstFid, inFile, rootDir, rescale, outDir, xoff, yoff, nsCut, nlCut):
	thisGT = lstFid[name].GetGeoTransform()
	(ULlon, ULlat) = geotransform.pixelToMap(xoff, yoff, thisGT)
	#(LRlon, LRlat) = geotransform.pixelToMap(xoff + ns, yoff+nl, thisGT)
	outGT = (ULlon, thisGT[1], thisGT[2], ULlat, thisGT[4], thisGT[5])
	nb = lstFid[name].RasterCount

	outDrv = gdal.GetDriverByName('gtiff')
	outDs = outDrv.Create( "{}/subset_{}".format(outDir, inFile[name]), nsCut, nlCut, nb, gdalconst.GDT_Byte, options=['compress=lzw', 'bigtiff=yes'])
	outDs.SetProjection(lstFid[name].GetProjection())
	outDs.SetGeoTransform(outGT)
	rangeOut = float(rescale[name][3]-rescale[name][2])
	rangeIn = float(rescale[name][1]-rescale[name][0])

	for ib in xrange(nb):
		for il in xrange(nlCut):
			data = numpy.ravel( lstFid[name].GetRasterBand(1+ib).ReadAsArray(xoff, il+yoff, nsCut, 1) )
			wfinite = numpy.isfinite(data)
			dataOut = numpy.zeros(ns) + rescale[name][4]
			if wfinite.any():
				wtp = (data >= rescale[name][0]) * (data <= rescale[name][3]) * (wfinite)
				if wtp.any():
					dataOut[wtp] = rangeOut*(data[wtp] - rescale[name][0])/rangeIn
					outDs.GetRasterBand(ib+1).WriteArray(dataOut.reshape(1,-1), 0, il)

	outDs = None


# automatically aubset a series of images
rootDir='E:/data/tanzania/GEE_export/kmeans_optique_radar/'
inFile = {'ndviTS':'ndvi_2016_3monthsSteps_subsetRadar.tif', 'ndviMinMaxAmplitude':'ndvi_2016_minMaxAmplitude_subsetRadar.tif', 'radarMin':'radarLIN_min_Tanzania_2016.vrt', 'radarMean':'radarLIN_mean_Tanzania_2016.vrt', 'radarMax':'radarLIN_max_Tanzania_2016.vrt'}
inFid = {'ndviTS':None, 'ndviMinMaxAmplitude':None, 'radarMin':None, 'radarMean':None, 'radarMax':None}
scale = {'ndviTS':[0,1,1,255,0], 'ndviMinMaxAmplitude':[0,1,1,255,0], 'radarMin':[-15,-0.5,1,255,0], 'radarMean':[-15,-0.5,1,255,0], 'radarMax':[-15,-0.5,1,255,0]}

for ii in inFile:
	thisFid = gdal.Open(rootDir + inFile[ii], gdalconst.GA_ReadOnly)
	inFid[ii] = thisFid

ns=inFid['ndviTS'].RasterXSize / 2
nl=inFid['ndviTS'].RasterYSize / 2
xoff = 0
yoff = 0
outDir='E:/data/tanzania/GEE_export/kmeans_optique_radar/subset_1/'
for name in inFid:
	print 'processing ',name
	doCutRescale(name, inFid, inFile, rootDir, scale, outDir, xoff, yoff, ns, nl)

print 'done'
