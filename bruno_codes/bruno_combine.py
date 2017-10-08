import gdal
import numpy
gdal.TermProgress = gdal.TermProgress_nocb
# combine radar and optical
# the reason of this script: "QGis raster calculator" can't load in memory very large files: processing line by line

radarCumul = 'E:/data/publication_s1_s2/combined/Tanzania/radarMin_5_31_Tanzania_2016_0_0.vrt'
ndviCumul = 'E:/data/publication_s1_s2/combined/Tanzania/ndviThreshCum_0_65_Tanzania_2016_0_0.vrt'

output='E:/data/publication_s1_s2/combined/Tanzania/combine.tif'


radarFID = gdal.Open(radarCumul, gdal.GA_ReadOnly)
ndviCumul = gdal.Open(ndviCumul, gdal.GA_ReadOnly)
ns = radarFID.RasterXSize
nl = radarFID.RasterYSize
print ns, nl
geotrans = radarFID.GetGeoTransform()
projection = radarFID.GetProjection()
print geotrans
print projection

# create output
outDrv = gdal.GetDriverByName('Gtiff')
outDs = outDrv.Create(output, ns, nl, 1, gdal.GDT_Byte, options=['compress=lzw','bigtiff=yes'])
outDs.SetProjection(projection)
outDs.SetGeoTransform(geotrans)

gdal.TermProgress(0)
for il in xrange(nl):
	gdal.TermProgress(il/float(nl))
	thisRadar = numpy.ravel(radarFID.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
	thisNdvi  = numpy.ravel(ndviCumul.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
	maskData = (thisRadar >0 ) * (thisNdvi >= 2)
	maskData = maskData.astype(int)
	#print maskData.shape, min(maskData), max(maskData)
	outDs.GetRasterBand(1).WriteArray(maskData.reshape(1,-1), 0, il)

gdal.TermProgress(1)
# close files
outDs = None
radarFid = None
ndviCumul = None
