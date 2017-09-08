import gdal
import gdalconst
import numpy
import sys

gdal.TermProgress = gdal.TermProgress_nocb

rootDir = 'E:/data/tanzania/GEE_export/radar_3months/'
listFile = ['radar_Tanzania_2015-01-01_2015-03-31_0_0.tif', 'radar_Tanzania_2015-04-01_2015-06-30_0_0.tif','radar_Tanzania_2015-07-01_2015-09-30_0_0.tif','radar_Tanzania_2015-10-01_2015-12-31_0_0.tif']
lstFid = []
outFile = 'radar_Tanzania_cumulDB_2015_3monthSteps.tif'

for ifile in listFile:
    thisFid = gdal.Open(rootDir+ifile, gdalconst.GA_ReadOnly)
    if thisFid is not None:
        lstFid.append(thisFid)
    else:
        print 'error opening {}'.format(ifile)
        sys.exit(1)
        
ns = thisFid.RasterXSize
nl = thisFid.RasterYSize
nb = 1
outDrv = gdal.GetDriverByName('gtiff')
outDs = outDrv.Create(rootDir+outFile, ns, nl, nb, gdalconst.GDT_Float32, options=['compress=lzw','BIGTIFF=YES'])
outDs.SetProjection(thisFid.GetProjection())
outDs.SetGeoTransform(thisFid.GetGeoTransform())

gdal.TermProgress(0.0)
for il in xrange(0, nl, 1):
    dataNan=numpy.zeros((len(lstFid), ns))
    for iband in range(len(lstFid)):
        dataNan[iband, :]= numpy.ravel(lstFid[iband].GetRasterBand(1).ReadAsArray(0, il, ns, 1))
    data = numpy.ma.masked_array(dataNan, numpy.isnan(dataNan))
    data[~data.mask] = [10**x for x in data[~data.mask]]
    cumul = numpy.ma.MaskedArray.sum(data, 0)
    cumul[~cumul.mask] = numpy.log10(cumul[~cumul.mask])
    outDs.GetRasterBand(1).WriteArray(numpy.ma.asarray(cumul.reshape(1,-1)), 0, il)
    gdal.TermProgress(il/nl)
    
gdal.TermProgress(1.0)
outDs = None
