import gdal
import numpy

infile='E:/tmp/palette/Classif33y_roadless_Congo.tif'
outfile='E:/tmp/palette/Classif33y_roadless_Congo_paletted.tif'

fid=gdal.Open(infile, gdal.GA_ReadOnly)
ns=fid.RasterXSize
nl=fid.RasterYSize
dt=fid.GetRasterBand(1).DataType

drv=gdal.GetDriverByName("GTiff")
ds=drv.Create(outfile, ns, nl, 1, dt, options=['compress=lzw','bigtiff=IF_SAFER'])
ds.SetProjection(fid.GetProjection())
ds.SetGeoTransform(fid.GetGeoTransform())

data = fid.GetRasterBand(1).ReadAsArray(0,0,ns,nl).astype(numpy.byte)
ds.GetRasterBand(1).WriteArray(data, 0,0)
ds.GetRasterBand(1).SetRasterColorInterpretation(gdal.GCI_PaletteIndex)
c = gdal.ColorTable()
ctable = [[10, (0,80,0)],[21,(30,130,0)],
	[22,(30,130,0)],[23,(100,160,0)],
	[24,(100,160,0)],[31,(180,210,60)],
	[32,(180,210,60)],[33,(180,210,60)],
	[34,(180,210,60)],[40,(255,255,155)],
	[41,(255,235,30)],[42,(255,215,30)],
	[43,(255,200,20)],[44,(255,180,15)],
	[45,(255,160,10)],[46,(255,140,10)],
	[47,(255,120,10)],[48,(255,100,10)],
	[49,(255,80,10)],[51,(255,60,0)],
	[52,(255,20,0)],[61,(170,80,80)],
	[62,(145,90,65)],[63,(120,95,50)],
	[71,(0,77,168)],[72,(0,157,200)],
	[73,(32,178,170)],[74,(102,205,170)],
	[81,(51,99,51)],[82,(98,161,80)],
	[83,(188,209,105)],[84,(255,228,148)],
	[85,(255,208,128)],[86,(250,180,150)],
	[87,(204,163,163)],[91,(255,255,255)],
	[92,(209,255,115)],[93,(152,181,142)],
	[100,(0,0,0)]]

for cid in range(0, len(ctable)):
 	c.SetColorEntry(ctable[cid][0], ctable[cid][1])

ds.GetRasterBand(1).SetColorTable(c)
ds.FlushCache()
ds = None
fid=None