import gdal
import gdalconst
import numpy
import math

# compute minmax from a vrt
inFile='E:/data/tanzania/GEE_export/ndvi_3months/ndvi_2015-10-01_2015-12-31.tif'
# output has 3 bands: min, max, amplitude
outFile='E:/data/tanzania/GEE_export/ndvi_3months/ndvi_2015_dec_jan_gt_0_2.tif'
threshold = 0.2

fidIn = gdal.Open(inFile, gdalconst.GA_ReadOnly)
ns = fidIn.RasterXSize
nl = fidIn.RasterYSize
nb = 1
outDrv = gdal.GetDriverByName('GTiff')
fidOut = outDrv.Create(outFile, ns, nl, 1, gdalconst.GDT_Byte, options=['compress=lzw'])
fidOut.SetProjection(fidIn.GetProjection())
fidOut.SetGeoTransform(fidIn.GetGeoTransform())

for il in xrange(nl):
    data =numpy.ravel(fidIn.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
    mask = data > threshold
    fidOut.GetRasterBand(1).WriteArray(mask.reshape(1,ns), 0, il)
        
fidOut = None
print 'done'
