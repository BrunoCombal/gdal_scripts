import gdal
import gdalconst
import numpy

dataRoot='/Volumes/OSGeo9.0/radar_2months/'
file=dataRoot+'radar_2015.vrt'
outFile=dataRoot+'mask_forest.tif'

thisFid = gdal.Open(file, gdalconst.GA_ReadOnly)
    
ns = thisFid.RasterXSize
nl = thisFid.RasterYSize
nb = thisFid.RasterCount
projection = thisFid.GetProjection()
geotrans = thisFid.GetGeoTransform()
print ns, nl, nb
print projection
print geotrans

outDrv = gdal.GetDriverByName('GTiff')
outDS = outDrv.Create(outFile, ns, nl, 1, gdalconst.GDT_Byte, ['compress=LZW'])
outDS.SetProjection(projection)
outDS.SetGeoTransform(geotrans)

for il in xrange(nl):
    data = numpy.zeros((nb,ns))
    for iband in range(nb):
        data[iband, :]=numpy.ravel(thisFid.GetRasterBand(iband+1).ReadAsArray(0, il, ns, 1))
        
    # compute max
    thisMax = numpy.ravel(numpy.max(data, 0)).reshape(1,ns)
    # define mask
    #mask = thisMax > 126
    # write it
    outDS.GetRasterBand(1).WriteArray( thisMax.reshape(1, ns), 0, il)
    
outDS = None

    
