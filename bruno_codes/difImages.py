import gdal
import gdalconst
import numpy
import math


# compute Ref - Target
fileR='E:/data/tanzania/GEE_export/radar_3months/radar_Tanzania_2015_3monthstep_cumulated.tif'
fileT='E:/data/tanzania/GEE_export/radar_3months/radar_Tanzania_2016_3monthstep_cumulated.tif'
outDiff = 'E:/data/tanzania/GEE_export/radar_3months/radar_Tanzania_diff_cumulated_2015-2016_LOG.tif'

# open inputs
fidR = gdal.Open(fileR, gdalconst.GA_ReadOnly)
fidT = gdal.Open(fileT, gdalconst.GA_ReadOnly)
ns = fidR.RasterXSize
nl = fidR.RasterYSize
nb = 1
proj = fidR.GetProjection()
gtrans = fidR.GetGeoTransform()

# open outputs
outDrv =  gdal.GetDriverByName('GTiff')
outDs = outDrv.Create(outDiff, ns, nl, 1, gdalconst.GDT_Float32,  options=['compress=lzw','BIGTIFF=YES'])
outDs.SetProjection(proj)
outDs.SetGeoTransform(gtrans)

for il in xrange(0,nl,50):
    dataRNan = fidR.GetRasterBand(1).ReadAsArray(0, il, ns, 1)
    dataR = numpy.ma.masked_array(dataRNan, numpy.isnan(dataRNan))
    dataTNan = fidT.GetRasterBand(1).ReadAsArray(0, il, ns, 1)
    dataT = numpy.ma.masked_array(dataTNan, numpy.isnan(dataTNan))
    dataRLIN = numpy.ma.masked_array([10**x for x in dataR], numpy.isnan(dataRNan))
    dataTLIN = numpy.ma.masked_array([10**x for x in dataT], numpy.isnan(dataTNan))
    diff = dataRLIN - dataTLIN
    print diff[~diff.mask]
    wtk = diff[~diff.mask] > 0.01
    diff[~diff.mask][wtk] = numpy.log10(diff[~diff.mask][wtk])
    print diff[~diff.mask]
    outDs.GetRasterBand(1).WriteArray(numpy.ma.asarray(diff.reshape(1,-1)), 0, il)
    
outDs = None
print 'done'

