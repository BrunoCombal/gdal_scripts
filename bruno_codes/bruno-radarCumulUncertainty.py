import gdal
import gdalconst
import numpy
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly

# see http://osgeo-org.1560.x6.nabble.com/gdal-dev-Real-and-quot-raster-quot-coordinates-td3749761.html
def mapToPixel(mx,my,gt): 
    if gt[2]+gt[4]==0: #Simple calc, no inversion required 
        px = (mx - gt[0]) / gt[1] 
        py = (my - gt[3]) / gt[5] 
    else: 
        px,py=ApplyGeoTransform(mx,my,InvGeoTransform(gt)) 
    return int(px+0.5),int(py+0.5) 

def pixelToMap(px,py,gt): 
    mx,my=ApplyGeoTransform(px,py,gt) 
    return mx,my 

def ApplyGeoTransform(inx,iny,gt): 
    ''' Apply a geotransform 
        @param  inx       Input x coordinate (double) 
        @param  iny       Input y coordinate (double) 
        @param  gt        Input geotransform (six doubles) 
        @return outx,outy Output coordinates (two doubles) 
    ''' 
    outx = gt[0] + inx*gt[1] + iny*gt[2] 
    outy = gt[3] + inx*gt[4] + iny*gt[5] 
    return (outx,outy)
    
def InvGeoTransform(gt_in):
    # we assume a 3rd row that is [1 0 0] 
    # Compute determinate 
    det = gt_in[1] * gt_in[5] - gt_in[2] * gt_in[4] 

    if( abs(det) < 0.000000000000001 ): 
        return 

    inv_det = 1.0 / det 

    # compute adjoint, and divide by determinate 
    gt_out = [0,0,0,0,0,0] 
    gt_out[1] =  gt_in[5] * inv_det 
    gt_out[4] = -gt_in[4] * inv_det 

    gt_out[2] = -gt_in[2] * inv_det 
    gt_out[5] =  gt_in[1] * inv_det 

    gt_out[0] = ( gt_in[2] * gt_in[3] - gt_in[0] * gt_in[5]) * inv_det 
    gt_out[3] = (-gt_in[1] * gt_in[3] + gt_in[0] * gt_in[4]) * inv_det 

    return gt_out


# input files
inFile1='E:/data/tanzania/GEE_export/radar_3months/radar_Tanzania_2015_3monthstep_cumulated.tif'
inFile2='E:/data/tanzania/GEE_export/radar_3months/radar_Tanzania_2016_3monthstep_cumulated.tif'
inFileS='E:/data/tanzania/GEE_export/ndvi_3months/ndvi_2016_minMaxAmplitude_fromImpact.tif'
inFileSynth = 'E:/data/tanzania/GEE_export/ndvi_3months/ndvi_2016_3monthsSteps.tif' 
outSelectMask = 'E:/data/tanzania/GEE_export/ndvi_3months/selection_mask.tif'

fid1 = gdal.Open(inFile1, gdalconst.GA_ReadOnly)
fid2 = gdal.Open(inFile2, gdalconst.GA_ReadOnly)
fidS = gdal.Open(inFileS, gdalconst.GA_ReadOnly)
fidSynth = gdal.Open(inFileSynth, gdalconst.GA_ReadOnly)

ns = fid1.RasterXSize
nl = fid1.RasterYSize
nb = 1
selectThreshold = 900 # better to select on NDVI
gtRadar = fid1.GetGeoTransform()
gtNdvi = fidS.GetGeoTransform()
nsNdvi = fidS.RasterXSize
nlNdvi = fidS.RasterYSize
nbNdvi = fidSynth.RasterCount
(lonRadar, latRadar) = pixelToMap(0,0,gtRadar)
(xoff, yoff) = mapToPixel(lonRadar, latRadar, gtNdvi)

outDrv = gdal.GetDriverByName('GTiff')
outMask = outDrv.Create(outSelectMask, ns, nl, 1, gdalconst.GDT_Byte, options=['compress=lzw','BIGTIFF=IF_NEEDED'])
outMask.SetProjection(fidS.GetProjection())
outMask.SetGeoTransform(gtRadar)

xdata=None
ydata=None
for il in xrange(0,nl,1):
    data1 = numpy.ravel(fid1.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
    data2 = numpy.ravel(fid2.GetRasterBand(1).ReadAsArray(0, il, ns, 1))
    # select: read in the bigger image, with offsets
    dataSmin = numpy.ravel(fidS.GetRasterBand(1).ReadAsArray(xoff, il+yoff, ns, 1))
    dataSmax = numpy.ravel(fidS.GetRasterBand(2).ReadAsArray(xoff, il+yoff, ns, 1))
    ndviCount = numpy.zeros(ns)
    for ib in range(nbNdvi):
        thisNdvi = numpy.ravel(fidSynth.GetRasterBand(ib+1).ReadAsArray(xoff, il+yoff, ns, 1))
        wndvi = thisNdvi > 0.4
        if wndvi.any():
            ndviCount[wndvi] = ndviCount[wndvi]+1
    #dataSAmp = numpy.ravel(fidS.GetRasterBand(3).ReadAsArray(xoff, il+yoff, ns, 1))
    #print data1.size, dataS.size
    wtk = (dataSmin > 0.2) * (dataSmax > 0.7) * (ndviCount > 2)
    outMask.GetRasterBand(1).WriteArray(wtk.reshape(1,-1),0,il)
    #wtk = ndviCount > 2

    if wtk.any():
        if xdata is None:
            xdata = numpy.array(data1[wtk])
            ydata = numpy.array(data2[wtk])
        else:
            xdata = numpy.append(xdata, data1[wtk])
            xdata = numpy.append(ydata, data2[wtk])

print 'data read'
outMask = None

# linear fit
z=numpy.polyfit(xdata,ydata,1)
print 'linear fit ',z
p=numpy.poly1d(z)
# compute r2
ybar = numpy.sum(ydata)/len(ydata)
yhat = p(xdata)
ssreg = numpy.sum((yhat-ybar)**2)
sstot = numpy.sum((ydata - ybar)**2) 
print '---- linear regression ----'
print 'number of data',len(xdata)
print 'r2=',ssreg/sstot
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
ax1.hist(xdata-ynew, normed=False, facecolor='red', alpha=0.5)
ax1.grid(True)

# now we plot
#ax2 = plt.subplot(2,1,2)
#ax2.plot(xdata, ydata,'o')
#ax2.plot(xdata, ynew, 'ro')
#ax2.plot([0,1250],[p(0),p(1250)])
#ax2.set_xlim([0,1250])
#ax2.set_ylim([0,1250])
plt.show()


print 'data plotted'