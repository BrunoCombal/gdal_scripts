import gdal
import gdalconst
import numpy

# compute minmax from a vrt
inFile='E:/data/tanzania/GEE_export/ndvi_3months/ndvi_2016_3monthsSteps.vrt'
# output has 3 bands: min, max, amplitude
outFile='E:/data/tanzania/GEE_export/ndvi_3months/ndvi_2016_MinMeanMaxAmplitude.tif'

fidIn = gdal.Open(inFile, gdalconst.GA_ReadOnly)
print fidIn

ns = fidIn.RasterXSize
nl = fidIn.RasterYSize
nb = fidIn.RasterCount
print ns,nl,nb

dataType = gdalconst.GDT_Float32
print 'dataType ',dataType

outDrv = gdal.GetDriverByName('GTiff')
fidOut = outDrv.Create(outFile, ns, nl, 4, dataType, options=['compress=lzw', 'BigTiff=YES'])
#outDrv = gdal.GetDriverByName('HFA')
#fidOut = outDrv.Create(outFile, ns, nl, 3, dataType, options=['compress=YES','use_spill=YES'])
fidOut.SetProjection(fidIn.GetProjection())
fidOut.SetGeoTransform(fidIn.GetGeoTransform())


for il in xrange(nl):
    dataOrg = numpy.zeros( (nb, ns) )
    for ib in range(nb):
        dataOrg[ib, :]=fidIn.GetRasterBand(1+ib).ReadAsArray(0, il, ns, 1)
    data = numpy.ma.masked_array(dataOrg, numpy.isnan(dataOrg))
    thisMin = numpy.ma.MaskedArray.min(data, 0)
    thisMean = numpy.ma.MaskedArray.mean(data,0)
    thisMax = numpy.ma.MaskedArray.max(data,0)
    thisAmp = thisMax - thisMin
    #print thisAmp[ns/2-5 : ns/2+5]
    
    fidOut.GetRasterBand(1).WriteArray(numpy.ma.asarray(thisMin.reshape(1,ns)), 0, il)
    fidOut.GetRasterBand(2).WriteArray(numpy.ma.asarray(thisMean.reshape(1,ns)), 0, il)
    fidOut.GetRasterBand(3).WriteArray(numpy.ma.asarray(thisMax.reshape(1,ns)), 0, il)
    fidOut.GetRasterBand(4).WriteArray(numpy.ma.asarray(thisAmp.reshape(1,ns)), 0, il)

fidOut = None
print 'done'
