# -*- coding: utf-8 -*-
from __future__ import division
import gdal
import ogr
import os
import copy
import numpy
import carbEFObj
import carbEFCoord

class gridAuto():
	""" A gridAuto object is defined from a starting coordinate, and a reference raster.
	More raster can be added, so that the code can extract their values.
	The object returns a block for a series of raster images.
	"""
	rasters = None

	grid = {'ulx':None, 'uly':None, 'xOffset':None, 'yOffset':None, 'cellXWidth':None, 'cellYWidth':None}

	def __init__(self, raster, gridUlx, gridUly, gridXOffset, gridYOffset, cellXWidth, cellYWidth, keep=False):
		if isinstance(raster, carbEFObj.raster):
			self.rasters['reference'] = raster

		self.grid['ulx'] = gridUlx
		self.grid['uly'] = gridUly
		self.grid['xOffset'] = gridXOffset
		self.grid['yOffset'] = gridYOffset
		self.grid['cellXWidth'] = cellXWidth
		self.grid['cellYWidth'] = cellYWidth

		self._createGrid()
		self.ii = 0
		self.jj = 0

		self.keep = keep # if true keep the grid cells

	def _createGrid(self):
		self.nXCell = (raster['reference'].parameters['ns'] - self.grid['xOffset']) // self.grid['cellXWidth']
		self.nYCell = (raster['reference'].parameters['nl'] - self.grid['yOffset']) // self.grid['cellYWidth']
		self.indexMax = self.nXCell * self.nYCell
		self.index = 0

	def addRaster(self, raster, name):
		"""
		Class carbEFGrid assumes that the raster have the same projection
		and that their grids matches (pixels have the same size and
		coordinates, no shift in-between them)
		"""
		if isinstance(raster, carbEFObj.raster):
			self.rasters['name'] = raster

	def first(self):
		""" Reset the pointer to the first item
		index = ii * nXWidth + jj
		"""
		self.index=0

	def next(self):
		""" Move to the next grid cell.
		Returns False if out of grid.
		"""
		self.index += 1
		if self.index >= self.indexMax:
			return False
		return True

	def indexToXY(self, index, name):
		""" Convert current index index into the upper left pixel coordinate of the grid cell.
		Pass index as a variable, so it can be called from another loop, for example the save2shp function.
		"""
		ii = index // self.cellXWidth
		jj = index % self.cellYWidth

		if name=='reference':
			xStart = self.grid['xOffset'] + ii * self.cellXWidth
			yStart = self.grid['yOffset'] + jj * self.cellYWidth
		else:
			# convert reference ULX, ULY into raster[name] pixel coordinates
			refGT = raster['reference'].parameters['geotransform']
			# xShift and yShift can be negative, as there is xOffset and yOffset
			xShift, yShift = carbEFCoord.mapToPixel( refGT[0], refGT[3], raster[name].parameters['geotransform'] )
			xStart = xShift + self.grid['xOffset'] + ii * self.cellXWidth
			yStart = yShift + self.grid['yOffset'] + jj * self.cellYWidth
		return xStart, yStart

	def saveGrid(self, outpath, outfile):
		""" Save grid as a layer populated with polygons (as grid cells)
		Grid is created when parsing it: cells are saved by calling get.
		Save the grid at the end, after parsing the whole grid.
		Do not use the inner pointr, self.index, but another one
		"""
		for ii in xrange(self.nXCell * self.nYCell)


	def get(self, name='reference', ib=1):
		"""returns grid cell subset for file "name", for the current cell pointer.
		If the cell is not entirely in the image, returns None
		Allows to return data from a given band (ib)
		"""
		if not name in rasters.keys():
			raise ValueError("carbEFGrid.gridAuto.get: unknown raster identifier {}".format(name))
		if ib<=0:
			raise ValueError("carbEFGrid.gridAuto.get: band index must be >=1, got ib={}".format(name))

		xStart, yStart = self.indexToXY(self.index, name)

		if xStart<0 or yStart<0 or 
			xStart + self.cellXWidth >= self.rasters[name].parameters['ns'] or
			yStart + self.cellYWidth >= self.rasters[name].parameters['nl']:
			subset = None
		else:
			subset = rasters[name].readBlock(xStart, yStart, self.cellXWidth, self.cellYWidth, ib=1)

		return subset




class gridPolygons():
	""" Grid done from a series of polygons
	Polygons are irregular. User is responsible for the mesh consistency (minimal size, overlapping polygons)
	OBSOLETE
	"""
	rasters = None
	fidVector = None
	layers = None
	def __init__(self, raster, vectorpath, vectorfname):
		if isinstance(raster, carbEFObj.raster):
			self.rasters['reference'] = raster
		if not os.path.exists(os.path.join(vectorpath, vectorfname)):
			raise IOError("carbEFGrid.gridPolygons.__init__: vector filename not found on disk {}".format(os.path.join(vectorpath, vectorfname)))
		else:
			self.vectorpath = vectorpath
			self.vectorfname = vectorfname

	def _openvectorfile(self):
		try:
			self.fidVector = ogr.Open(os.path.join(self.vectorpath, self.vectorfname), gdal.GA_ReadOnly)
		except IOError,e:
			raise("_createGrid.gridPolygons._openvectorfile: error while trying to open vector file {}".format(os.path.join(self.vectorpath, self.vectorfname)))
		if self.fidVector is None:
			raise("_createGrid.gridPolygons._openvectorfile: after trying to open vector file {} no file identifier could be set".format(os.path.join(self.vectorpath, self.vectorfname)))

	def _analyseVector(self):
		""" From the vector file: get list of layers, keep in a list only layers of 
		"""
		if self.fidVector is None:
			self._openvectorfile()

		definition = self.fidVector.GetLayer().GetLayerDefn()
		for ii in range(definition.GetFieldCount()):
			layername=definition.GetFieldDefn(i).GetName()
			# if polygons only, append to the list
			if definition.GetFieldDefn(i).GetType() == 
			self.layers.append(layername)


