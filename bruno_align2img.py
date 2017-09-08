import gdal
import gdalconst


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

# align2img: warp image imgToAlign onto imgRef, to get a superimposable grid.
def align2img(imgRef, imgToAlign, aligned):

	# for infor, to be deleted
	alignFID = gdal.Open(imgToAlign, gdalconst.GA_ReadOnly)
	print alignFID.GetGeoTransform()



	# get info from reference file
	refFid = gdal.Open(imgRef, gdalconst.GA_ReadOnly)
	ns = refFid.RasterXSize
	nl = refFid.RasterYSize
	gt = refFid.GetGeoTransform()
	proj = refFid.GetProjection()
	ul = pixelToMap(0,0,gt)
	lr = pixelToMap(ns, nl, gt)
	outputBounds = ( min(ul[0], lr[0]), min(ul[1],lr[1]), max(ul[0],lr[0]), max(ul[1],lr[1]) )
	print outputBounds
	print gt[1], gt[5]

	gdal.Warp(aligned, imgToAlign, dstSRS=proj, dstNodata=0, outputBounds=outputBounds, outputBoundsSRS=proj, xRes=abs(gt[1]), yRes=abs(gt[5]), resampleAlg='bilinear' )

if __name__=="__main__":
	refFile = 'E:/impact/IMPACT/DATA/test_bruno_facet_2000-2014_5classes_eq_Area.tif'
	toWarp = 'E:/impact/IMPACT/DATA/ecozone_stratification_2.tif'

	align2img(refFile, toWarp, 'E:/impact/IMPACT/data/warped.tif')