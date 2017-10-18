import gdal
import gdalconst


dataRoot = 'E:/data/tanzania/GEE_export/radar_2months/'
file = [dataRoot+'radar_2015.vrt', dataRoot+'radar_2016.vrt']
fid = []
mask = dataRoot + 'mask_forest.tif'
threshold = 170
outFile = dataRoot + 'dtw.tif'

for ifile in file:
    thisFid = gdal.Open(ifile, gdalconst.GA_ReadOnly)
    fid.append(thisFid)

maskFid = gdal.Open(mask, gdalconst.GA_ReadOnly)

ns = thisFid.RasterXSize
nl = thisFid.RasterYSize
nb = fid[0].RasterCount
projection = thisFid.GetProjection()
geotrans = thisFid.GetGeoTransform()

outDrv = gdal.GetDriverByName('GTiff')
outDS = outDrv.Create(outFile, ns, nl, 1, gdalconst.GDT_Byte, ['compress=lzw'])

indexNS = numpy.arange(ns)

for il in xrange(nl):
    maskData = numpy.ravel(maskFid.GetRasterBand(1).ReadAsArray(0, il, ns, 1) )
    whereToKeep = maskData >= threshold
    dtwData = numpy.zeros(ns)
    if whereToKeep.any():
        dataRefIn = numpy.zeros( (nb, ns) )
        dataChangeIn = numpy.zeros( (nb, ns) )
        for ib in xrange(nb):
            dataRefIn[ib, :] = numpy.ravel(fid[0].GetRasterBand(1+ib).ReadAsArray(0, il, ns, 1).astype(float))
            dataChangeIn[ib, :] = numpy.ravel(fid[1].GetRasterBand(1+ib).ReadAsArray(0, il, ns, 1).astype(float))
        # let's process the mask
        for ii in indexNS[whereToKeep]:
            dtwData[ii] = fastdtw( numpy.ravel(dataRefIn[:, ii]), numpy.ravel(dataChangeIn[:, ii]) )[0]
            
    outDS.GetRasterBand(1).WriteArray(dtwData.reshape(1,ns), 0, il)
        
outDs = None

