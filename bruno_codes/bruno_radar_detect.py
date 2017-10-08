import fastdtw

import gdal
import gdalconst
import numpy
import sys
import os.path
import geotransform
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly
reportLevels = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# report according to a progression level
def report(i, N, lastReport=None, message=''):

	if lastReport is None:
		lastReport = -1
	if N == 0:
		lastReport = -1
		return lastReport
	thisLevel = int(100*(i/float(N)))
	if thisLevel in reportLevels and thisLevel>lastReport:
		lastReport = thisLevel
		print '{}% ({}/{}): {}'.format(int(100*(i/float(N))), i, N, message)
	return lastReport

# compute cumulated differences between two time series
def doCumulDiff(name, lstFid, outDir):
	ns = lstFid[indicator][0].RasterXSize
	nl = lstFid[indicator][0].RasterYSize
	nb = 1
	outDrv = gdal.GetDriverByName('gtiff')
	outDs = outDrv.Create('{}/cumulDiff_{}.tif'.format(outDir, indicator), ns, nl, 1, gdalconst.GDT_Byte, options=['compress=lzw', 'bigtiff=yes'])
	outDs.SetProjection(lstFid[indicator][0].GetProjection())
	outDs.SetGeoTransform(lstFid[indicator][0].GetGeoTransform())

	gdal.TermProgress = gdal.TermProgress_nocb

# detect change
def doDetectChange(indicator, lstFid, threshold, outDir):
	ns = lstFid[indicator][0].RasterXSize
	nl = lstFid[indicator][0].RasterYSize
	nb = 1
	outDrv = gdal.GetDriverByName('gtiff')
	outDs = outDrv.Create('{}/change_{}.tif'.format(outDir, indicator), ns, nl, 1, gdalconst.GDT_Byte, options=['compress=lzw', 'bigtiff=yes'])
	outDs.SetProjection(lstFid[indicator][0].GetProjection())
	outDs.SetGeoTransform(lstFid[indicator][0].GetGeoTransform())

	gdal.TermProgress = gdal.TermProgress_nocb
	print 'Processing ',indicator

	for il in xrange(nl):
		data0 = lstFid[indicator][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1)
		data1 = lstFid[indicator][1].GetRasterBand(1).ReadAsArray(0, il, ns, 1)
		change = numpy.zeros( (1,ns) )
		wtp = numpy.isfinite(data0) * numpy.isfinite(data1)
		if wtp.any():
			change[wtp] = (data0[wtp] < threshold) * (data1[wtp] > threshold)
			outDs.GetRasterBand(1).WriteArray(change, 0, il)
		gdal.TermProgress(il/nl)
	gdal.TermProgress(1)
	outDs = None

# Dynamic Time Warping
def doDTW(name, lstFid, myMask, outDir):
	ns = lstFid[name][0].RasterXSize
	nl = lstFid[name][0].RasterYSize
	nb = [lstFid[name][0].RasterCount]
	nb.append(lstFid[name][1].RasterCount)

	outDrv = gdal.GetDriverByName('gtiff')
	outDs = outDrv.Create( os.path.join(outDir, 'dtw_{}.tif'.format(name)), ns, nl, 1, gdalconst.GDT_Float32, options=['compress=lzw', 'bigtiff=yes'] )
	outDs.SetProjection(lstFid[name][0].GetProjection(1))
	outDs.SetGeoTransform(lstFid[name][0].SetProjection(1))

	gdal.TermProgress = gdal.TermProgress_nocb
	print 'Processing ',name

	for il in xrange(nl):
		data0=numpy.zeros( (nb[0], ns) )
		data1=numpy.zeros( (nb[1], ns) )
		for ib in xrange(nb[0]):
			data0[ib,:] = numpy.ravel( lstFid[name][0].GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1) )
		for ib in xrange(nb[1]):
			data1[ib,:] = numpy.ravel( lstFid[name][1].GetRasterBand(ib+1).ReadAsArray(0, il, ns, 1) )
		data0Mask = numpy.prod(numpy.isfinite(data0), 0 ).ravel()
		data1Mask = numpy.prod(numpy.isfinite(data1), 0 ).ravel()

		outDTW = numpy.zeros( ns )
		# get Mask: first date
		maskData = numpy.ravel( lstFid[myMask['name']][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1) )
		isfinite = numpy.isfinite(maskData)
		thisMask = numpy.zeros(ns)
		thisMask[isfinite] = (maskData[isfinite] < myMask['threshold']) * data0Mask[isfinite] * data1Mask[isfinite]

		for ii in xrange(ns):
			if thisMask[ii]:
				try:
					result = fastdtw.fastdtw(numpy.ravel(data0[:,ii]), numpy.ravel(data1[:,ii]))
					outDTW[ii] = result[0]
				except:
					print 'Error on line {}, column {}'.format(il, ii)
					print data0[:,ii]
					print data1[:,ii]
		outDs.GetRasterBand(1).WriteArray(outDTW.reshape(1,-1), 0, il)
		gdal.TermProgress(il/nl)

	gdal.TermProgress(1)
	outDS = None

# compute difference, if reflectance lower than condition
def doCondDiff(name, condition, lstFid, outDir):
	ns = lstFid[name][0].RasterXSize
	nl = lstFid[name][0].RasterYSize
	print 'ns=', ns
	print 'nl=', nl
	outDrv = gdal.GetDriverByName('gtiff')
	outDs = outDrv.Create('{}/cond_diff_{}.tif'.format(outDir, name), ns, nl, 1, gdalconst.GDT_Float32, options=['compress=lzw', 'bigtiff=yes'])
	outDs.SetProjection(lstFid[name][0].GetProjection())
	outDs.SetGeoTransform(lstFid[name][0].GetGeoTransform())

	gdal.TermProgress = gdal.TermProgress_nocb
	print 'Processing ',name

	for il in xrange(nl):
		data0 = lstFid[name][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1)
		data1 = lstFid[name][1].GetRasterBand(1).ReadAsArray(0, il, ns, 1)
		cond = lstFid[condition[name]][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1)
		diff = numpy.zeros( (1,ns) )
		wtp = numpy.isfinite(data0) * numpy.isfinite(data1) * numpy.isfinite(cond)
		if wtp.any():
			wcond = cond[wtp] < condition['threshold']
			if wcond.any():
				diff[1, wtp[wcond]] = data1[wtp[wcond]] - data0[wtp[wcond]]
				outDs.GetRasterBand(1).WriteArray(diff, 0, il)
		gdal.TermProgress(il/nl)

	gdal.TermProgress(1)

	outDs = None

# compare a distribution to a reference, and find linear regression
# we assume that the mean for the trees should not change too much
def doAlignDistr(name, lstFid, threshold, ndviTS, outDir, dataType='db', maskForestFile=None):
	ns = lstFid[name][0].RasterXSize
	nl = lstFid[name][0].RasterYSize
	outDrv = gdal.GetDriverByName('gtiff')
	outDs = outDrv.Create('{}/{}_aligned.tif'.format(outDir, name), ns, nl, 1, gdalconst.GDT_Float32, options=['compress=lzw', 'bigtiff=yes'])
	outDs.SetProjection(lstFid[name][0].GetProjection())
	outDs.SetGeoTransform(lstFid[name][0].GetGeoTransform())

	# we assume that the NDVI image covers the radar image
	gtRadar = lstFid[name][0].GetGeoTransform()
	gtNdvi = lstFid[ndviTS][0].GetGeoTransform()
	nsNdvi = lstFid[ndviTS][0].RasterXSize
	nlNdvi = lstFid[ndviTS][0].RasterYSize
	nbNDVI = lstFid[ndviTS][0].RasterCount
	(lonRadar, latRadar) = geotransform.pixelToMap(0, 0, gtRadar)
	(xoff, yoff) = geotransform.mapToPixel(lonRadar, latRadar, gtNdvi)


	print 'Processing ',name
	if dataType != 'db':
		print 'Input data not modified before polyfit'

	xdata = None
	ydata = None
	progress = report(0, 0, None, 'Starting')
	for il in xrange(0, nl, 50):
		data0Db = numpy.ravel(lstFid[name][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
		data1Db = numpy.ravel(lstFid[name][1].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
		radarMask = numpy.isfinite(data0Db) * numpy.isfinite(data1Db)

		dataN = numpy.zeros( (nbNDVI, ns) )
		dataNMask = numpy.ones(ns, dtype=bool) # must be true on all bands
		dataThresholdCount = numpy.zeros(ns)
		dataNmax = numpy.zeros( ns )
		dataNmin = numpy.zeros( ns )
		for ib in xrange(nbNDVI):
			dataN[ib, :] = lstFid[ndviTS][0].GetRasterBand( ib+1 ).ReadAsArray( 0+xoff, il+yoff, ns, 1)
			dataNMask = dataNMask * numpy.isfinite(dataN[ib,:]) * radarMask

		maskForest = None
		if maskForestFile is not None:
			maskForest = numpy.ravel(lstFid[maskForestFile][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1)) > 0

		if xdata is not None:
			progress = report(il, nl, progress, '\nxdata.size={}\nydata.size={}\n'.format(xdata.size, ydata.size))
		else:
			progress = report(il, nl, progress, '\nno data collected\n')


		if dataNMask.any():
			dataNmax[dataNMask] = numpy.max( dataN[:, dataNMask], 0 )
			#dataNmin[dataNMask] = numpy.min(dataN[dataNMask], 0)
			dataThresholdCount[dataNMask]  = numpy.sum( dataN[:, dataNMask] > 0.6, 0 )

			wForest = dataNMask  * ( dataNmax > 0.75 ) * ( dataThresholdCount > 1 ) 
			if maskForest is not None:
				wForest = wForest * maskForest

			if wForest.any():
				# get radar data where the forest is
				#data0Db = data0 #numpy.ravel(lstFid[name][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
				#data1Db = data1 #numpy.ravel(lstFid[name][1].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
				if dataType=='db':
					wtp = radarMask
					if wtp.any():
						thisData = 10*10**(data0Db[wtp])
						data0Db[wtp] = thisData
						thisData = 10*10**(data1Db[wtp])
						data1Db[wtp] = thisData
				if xdata is None:
					xdata = numpy.ravel(data0Db[wForest])
					ydata = numpy.ravel(data1Db[wForest])
				else:
					xdata = numpy.append( xdata, numpy.ravel(data0Db[wForest]) )
					ydata = numpy.append( ydata, numpy.ravel(data1Db[wForest]) )



	xdata = numpy.array(xdata)
	ydata = numpy.array(ydata)
	print '__________________________'
	print xdata.shape
	print ydata.shape
	print numpy.min(xdata), numpy.max(xdata), numpy.mean(xdata)
	print numpy.min(ydata), numpy.max(ydata), numpy.mean(ydata)
	ax1 = plt.subplot(1,1,1)
	ax1.plot(xdata,ydata,'o')
	#ax1.hist(ynew, 50, normed=False, facecolor='green', alpha=0.5)
	#ax1.hist(xdata, 50, normed=False, facecolor='blue', alpha=0.5)
	#ax1.hist(ydata, 50, normed=False, facecolor='green', alpha=0.5)
	#ax1.hist(xdata-ynew, normed=False, facecolor='red', alpha=0.5)
	ax1.grid(True)
	plt.show()
	print '__________________________'
	
	# linear fit
	z = numpy.polyfit(xdata, ydata, 1)
	print 'linear fit ',z
	p = numpy.poly1d(z)
	# compute r2
	ybar = numpy.sum(ydata)/len(ydata)
	yhat = p(xdata)
	ssreg = numpy.sum( (yhat - ybar)**2 )
	sstot = numpy.sum( (ydata - ybar)**2 ) 
	print '---- linear regression ----'
	print 'number of data',len(xdata)
	print 'r2=', ssreg/sstot
	print '--- distributions ---'
	xmean = xdata.mean()
	ymean = ydata.mean()
	xstd = xdata.std()
	ystd = ydata.std()
	print 'dist 1 (x): mean {}, std {}'.format(xmean, xstd)
	print 'dist 2 (y): mean {}, std {}'.format(ymean, ystd)

	ynew = xmean + (ydata - ymean)*(xstd/ystd)
	print 'transformation: y(i) = {0} + {2}(x(i) - {1})'.format(ymean, xmean, ystd/xstd)

	ax1 = plt.subplot(1,1,1)
	ax1.hist(ynew, 50, normed=False, facecolor='green', alpha=0.5)
	ax1.hist(xdata, 50, normed=False, facecolor='blue', alpha=0.5)
	ax1.hist(xdata-ynew, 50, normed=False, facecolor='red', alpha=0.5)
	ax1.grid(True)
	#plt.show()

	return {"xmean":xmean, "xstd":xstd, "ymean":ymean, "ystd":ystd}

# first realign data, asusming forest should not change much, then compute difference
def doDiffCorrected(name, lstFid, linearCorr, threshold, outDir, typeDiff=None):
	ns = lstFid[name][0].RasterXSize
	nl = lstFid[name][0].RasterYSize
	outDrv = gdal.GetDriverByName('gtiff')
	outName = '{}/corrected_diff_{}.tif'.format(outDir, name)
	if typeDiff is not None:
		outName='{}/corrected_diff_{}_{}.tif'.format(outDir, name, typeDiff)
	outDs = outDrv.Create(outName, ns, nl, 1, gdalconst.GDT_Float32, options=['compress=lzw', 'bigtiff=yes'])
	outDs.SetProjection(lstFid[name][0].GetProjection())
	outDs.SetGeoTransform(lstFid[name][0].GetGeoTransform())

	try:
  		progress = gdal.TermProgress_nocb
	except:
	  	progress = gdal.TermProgress
  	sys.stdout.flush()

	for il in xrange(nl):
		data0 = numpy.ravel(lstFid[name][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
		data1Org = numpy.ravel(lstFid[name][1].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
		wtp = numpy.isfinite(data0) * numpy.isfinite(data1Org) * (data0 < threshold) * (data1Org > threshold)
		data1 = numpy.zeros(ns)
		thisDiff = numpy.zeros(ns) - 9999
		if wtp.any():
			data1[wtp] = linearCorr['xmean'] + (data1Org[wtp] - linearCorr['ymean'])*(linearCorr['xstd']/linearCorr['ystd'])
			if typeDiff is None:
				thisDiff[wtp] = data1[wtp] - data0[wtp]
			else:
				thisDiff[wtp] = (data1[wtp] - data0[wtp])/(data0[wtp])
			outDs.GetRasterBand(1).WriteArray(thisDiff.reshape(1, -1), 0, il)
		progress(il/nl)
		sys.stdout.flush()
	progress(1)

	outDs = None

# get a file, and a reference file (lstFid[ndviTS]) to select pixels
def doStats(infile, lstFid):
	inFid = gdal.Open(infile, gdalconst.GA_ReadOnly)
	ns = inFid.RasterXSize
	nl = inFid.RasterYSize

	gtRadar = inFid.GetGeoTransform()
	gtNdvi = lstFid['ndviTS'][0].GetGeoTransform()
	nsNdvi = lstFid['ndviTS'][0].RasterXSize
	nlNdvi = lstFid['ndviTS'][0].RasterYSize
	nbNDVI = lstFid['ndviTS'][0].RasterCount
	(lonRadar, latRadar) = geotransform.pixelToMap(0, 0, gtRadar)
	(xoff, yoff) = geotransform.mapToPixel(lonRadar, latRadar, gtNdvi)

	collection = None
	for il in xrange(nl):
		forestMask = numpy.ravel(lstFid['forestMask'][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1))

		selectData = numpy.ravel(lstFid['ndviTS'][0])
		dataNMask = numpy.ones(ns, dtype=bool)
		dataN = numpy.zeros( (nbNDVI, ns) )
		for ib in xrange(nbNDVI):
			dataN[ib, :] = lstFid['ndviTS'][0].GetRasterBand( ib+1 ).ReadAsArray( 0+xoff, il+yoff, ns, 1)
			dataNMask = dataNMask * numpy.isfinite(dataN[ib,:]) 

		dataNmax = numpy.zeros(ns)
		dataThresholdCount = numpy.zeros(ns)
		if dataNMask.any():
			dataNmax[dataNMask] = numpy.max( dataN[:, dataNMask], 0 )
			#dataNmin[dataNMask] = numpy.min(dataN[dataNMask], 0)
			dataThresholdCount[dataNMask]  = numpy.sum( dataN[:, dataNMask] > 0.6, 0 )

			wForest = dataNMask * ( dataNmax > 0.7 ) * ( dataThresholdCount > 2 ) * (forestMask > 0)

			if wForest.any():
				data = numpy.ravel(inFid.GetRasterBand(1).ReadAsArray(0, il, ns, 1))[wForest]
				wtk = data != -9999 # radar mean difference should not be -9999
				if wtk.any():
					if collection is None:
						collection = data[wtk]
					else:
						collection = numpy.append(collection, data[wtk])

	# stats!
	print 'Statistics on {}, with {} points'.format(infile, collection.size)
	print 'min: {}, mean:{}, max: {}, std: {}'.format(numpy.min(collection), numpy.mean(collection), numpy.max(collection), numpy.std(collection))

# compute diff between 2 dates
def doDiff(name, lstFid, outDir):
	ns = lstFid[name][0].RasterXSize
	nl = lstFid[name][1].RasterYSize
	outName = '{}/diff_{}.tif'.format(outDir, name)
	outNameMask = '{}/diff_{}_mask.tif'.format(outDir, name)
	outDrv = gdal.GetDriverByName('gtiff')
	outDs = outDrv.Create(outName, ns, nl, 1, gdalconst.GDT_Float32, options=['compress=lzw', 'bigtiff=yes'])
	outDs.SetProjection(lstFid[name][0].GetProjection())
	outDs.SetGeoTransform(lstFid[name][0].GetGeoTransform())
	outDsMask = outDrv.Create(outNameMask, ns, nl, 1, gdalconst.GDT_Byte, options=['compress=lzw', 'bigtiff=yes'])
	outDsMask.SetProjection(lstFid[name][0].GetProjection())
	outDsMask.SetGeoTransform(lstFid[name][0].GetGeoTransform())

	for il in xrange(nl):
		data0 = numpy.ravel(lstFid[name][0].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
		data1 = numpy.ravel(lstFid[name][1].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
		wtp = numpy.isfinite(data0) * numpy.isfinite(data1)
		diff = numpy.zeros(ns) - 9999
		mask = numpy.zeros(ns)
		if wtp.any():
			diff[wtp] = data1[wtp] - data0[wtp]
			mask[wtp] = (data0[wtp] < -5.31) * (data1[wtp] > -5.31) * (diff[wtp] > 0.8)
		outDs.GetRasterBand(1).WriteArray(diff.reshape(1,-1), 0, il)
		outDsMask.GetRasterBand(1).WriteArray(mask.reshape(1,-1), 0, il)

	outDs = None
	outDsMask = None

# compute a Forest mask using radar and optica conditions
def doGreenForestMask(lstFid, yearRadar, outDir):
	radarFid = lstFid['max'][yearRadar]
	ns = radarFid.RasterXSize
	nl = radarFid.RasterYSize
	outDrv = gdal.GetDriverByName('gtiff')
	outDs = outDrv.Create( os.path.join(outDir, 'maskGreenForest_ro.tif'), ns, nl, 1, gdalconst.GDT_Byte, options=['compress=lzw', 'bigtiff=yes'])
	outDs.SetProjection(radarFid.GetProjection())
	outDs.SetGeoTransform(radarFid.GetGeoTransform())

	# we assume that the NDVI image covers the radar image
	gtRadar = radarFid.GetGeoTransform()
	gtNdvi = lstFid['ndviTS'][0].GetGeoTransform()
	nsNdvi = lstFid['ndviTS'][0].RasterXSize
	nlNdvi = lstFid['ndviTS'][0].RasterYSize
	nbNDVI = lstFid['ndviTS'][0].RasterCount
	(lonRadar, latRadar) = geotransform.pixelToMap(0, 0, gtRadar)
	(xoff, yoff) = geotransform.mapToPixel(lonRadar, latRadar, gtNdvi)

	# loop over images
	for il in xrange(0,nl):
		# radar
		data = numpy.ravel(radarFid.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
		wfinite = numpy.isfinite(data)
		mask = numpy.zeros(ns)
		if wfinite.any():
			mask[wfinite] = data[wfinite] < -5.31
		# optical
		optic = numpy.zeros(ns)
		for ib in xrange(lstFid['ndviTS'][0].RasterCount):
			thisOptic = numpy.ravel(lstFid['ndviTS'][0].GetRasterBand(1).ReadAsArray(xoff, il+yoff, ns, 1) )
			wfinite = numpy.isfinite(thisOptic)
			logicOptic = thisOptic[wfinite] > 0.7
			optic[wfinite] = optic[wfinite] + logicOptic.astype(int)
		# must meet two conditions: radar max < -5.31 and 2 times NDVI > 0.7
		mask = mask * ( optic > 1)
		outDs.GetRasterBand(1).WriteArray(mask.reshape(1, -1), 0, il)
	outDs = None


# main code
if __name__ == '__main__':
	rootDir = 'E:/data/tanzania/GEE_export/radarLIN2months/'
	outDir = rootDir + 'out/'

	inFile = { 'variance':[ rootDir+'radarLIN_variance_Tanzania_2015.vrt', rootDir+'radarLIN_variance_Tanzania_2016.vrt' ],
		'min':[ rootDir+'radarLIN_min_Tanzania_2015.vrt', rootDir+'radarLIN_min_Tanzania_2016.vrt' ], 
		'max':[ rootDir+'radarLIN_max_Tanzania_2015.vrt', rootDir+'radarLIN_max_Tanzania_2016.vrt' ],
		'mean':[ rootDir+'radarLIN_mean_Tanzania_2015.vrt', rootDir+'radarLIN_mean_Tanzania_2016.vrt' ],
		'ts':[ rootDir + 'timeSeries/radarLIN_Tanzania_2015_2monthStep.vrt', rootDir + 'timeSeries/radarLIN_Tanzania_2016_2monthStep.vrt' ],
		'ndviTS':[ 'E:/data/tanzania/GEE_export/ndvi_3months/ndvi_2016_3monthsSteps.tif'],
		'forestMask':['E:/data/tanzania/forest_strata_from_unredd.tif']
		}
	inFid = {'variance':[], 'min':[], 'max':[], 'mean':[], 'ts':[], 'ndviTS':[], 'forestMask':[]}

	for ii in inFile:
		for jj in inFile[ii]:
			thisFid = gdal.Open(jj, gdalconst.GA_ReadOnly)
			inFid[ii].append(thisFid)


	# compute relative difference
	#for ii in inFid:
	#	doRelativeDiff(ii, inFid[ii][0], inFid[ii][1], outDir)
	#doDiff('mean', inFid, outDir)

	#linearCorr = doAlignDistr('mean', inFid, -5.31, 'ndviTS', outDir, dataType='keep', maskForestFile='forestMask')
	#doDiffCorrected('mean', inFid, linearCorr, -5.31, outDir, typeDiff='relative')

	#doStats('E:/data/tanzania/GEE_export/radarLIN2months/out/corrected_diff_mean_relative.tif', inFid)

	#doDetectChange('max', inFid, -5.31, outDir)
	#doCondDiff(name, {'name':'mean','threshold':-5.31}, inFid, outDir)

	#doDTW('ts',inFid, {'name':'max', 'threshold':-5.31}, outDir)

	doGreenForestMask(inFid, 0, outDir)