import gdal
from gdalconst import *
import numpy

radar=u'E:/data/tanzania/GEE_export/composite_VV_VH_separate_ascending_descending_Tanzania_2015-05_2016-4_0_0-0000000000-0000000000.tif'
ndviFilenames = [u'E:/data/tanzania/GEE_export/composite_ndvi_Tanzania_2016-01_2016-03_0_0.tif', \
     u'E:/data/tanzania/GEE_export/composite_ndvi_Tanzania_2016-04_2016-06_0_0.tif',  \
     u'E:/data/tanzania/GEE_export/composite_ndvi_Tanzania_2016-07_2016-09_0_0.tif', \
     u'E:/data/tanzania/GEE_export/composite_ndvi_Tanzania_2016-10_2016-12_0_0.tif']
forestMask = u'E:/data/tanzania/tests/forestMask.tif'
ndviMask = u'E:/data/tanzania/tests/ndviMask.tif'

print ndviFilenames

radarMin = -10.9
ndviMin = 0.6

radarFH = gdal.Open(radar, GA_ReadOnly)
radarCRS = radarFH.GetProjection()
radarTrans = radarFH.GetGeoTransform()

ndviFH=[]
for ii in ndviFilenames:
    print ii
    thisFH = gdal.Open(ii, GA_ReadOnly)
    ndviFH.append(thisFH)
    
print 'all open'

ns = radarFH.RasterXSize
nl = radarFH.RasterYSize
outDrv = gdal.GetDriverByName('GTiff')
forestMaskFH = outDrv.Create(forestMask, ns, nl, 1, GDT_Byte, options=['compress=lzw'])
forestMaskFH.SetGeoTransform(radarTrans)
forestMaskFH.SetProjection(radarCRS)

print 'starting'
for il in xrange(nl):  
    dataR = numpy.ravel(radarFH.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
    inRadar = numpy.array(dataR > radarMin) 
    forestMaskFH.GetRasterBand(1).WriteArray(inRadar.reshape(1,ns),0,il)

radarFH = None
forestMaskFH = None

ns = ndviFH[0].RasterXSize
nl = ndviFH[1].RasterYSize
ndviMaskFH = outDrv.Create(ndviMask, ns, nl, 1, GDT_Byte, options=['compress=lzw'])
ndviMaskFH.SetGeoTransform(ndviFH[0].GetGeoTransform())
ndviMaskFH.SetProjection(ndviFH[0].GetProjection())

for il in xrange(nl):
    dataNdvi = numpy.zeros(ns)
    for iFH in ndviFH:
        thisNdvi= numpy.ravel(iFH.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
        dataNdvi += numpy.array(thisNdvi > ndviMin)
    ndviMaskFH.GetRasterBand(1).WriteArray(dataNdvi.reshape(1,ns), 0, il)

print 'done!'

ndviMaskFH = None
for ii in ndviFH: ii=None


