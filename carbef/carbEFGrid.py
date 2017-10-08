# -*- coding: utf-8 -*-
from __future__ import division
import gdal
import os
import copy
import numpy
import carbEFObj

class gridAuto():
	""" A gridAuto object is defined from a starting coordinate, and a reference raster.
	More raster can be added to extract values.
	The object returns a block for a series of raster images.
	"""
	rasters = None

	grid = {'ulx':None, 'uly':None, 'xOffset':None,'yOffset':None,'cellXWidth':None, 'cellYWidth':None}

	def __init__(self, raster, gridUlx, gridUly, gridXOffset, gridYOffset, cellXWidth, cellYWidth):
		if isinstance(raster, carbEFObj.raster):
			self.rasters['reference'] = raster

		self.grid['ulx']=gridUlx
		self.grid['uly']=gridUly
		self.grid['xOffset']=gridXOffset
		self.grid['yOffset']=gridYOffset
		self.grid['cellXWidth']=cellXWidth
		self.grid['cellYWidth']=cellYWidth

		self._createGrid()
		self.ii = 0
		self.jj = 0

	def _createGrid(self):
		self.nXCell = 0
		self.nYCell = 0

	def addRaster(self, raster, name):
		if isinstance(raster, carbEFObj.raster):
			self.rasters['name'] = raster

	def first(self):
		""" reset the pointer to the first item
		"""
		self.ii=0
		self.jj=0

	def next(self):
		""" move to the next grid cell.
		Returns False is out of grid.
		"""
		self.ii += 1
		if self.ii >= self.nXCell:
			self.jj += 1
		if self.jj>=self.nYCell:
			return False
		return True

	def infoCell(self):
		""" Show the current cell
		"""
		return 'nXCell: {}, nYCell: {}, ii: {}, jj:{}'.format(nXCell, nYCell, self.ii, self.jj)

	def get(self, name='reference'):
		"""returns value for file "name", for the current cell
		"""
		if not name in rasters.keys():
			raise ValueError("carbEFGrid.gridAuto.get: unknown raster identifier {}".format(name))
		subset = rasters[name].readBlock(self.grid['xOffset']+self.ii*self.cellXWidth,
			self.grid['yOffset']+self.jj*self.cellYWidth, 
			self.cellXWidth, self.cellYWidth, ib=1)
		return subset

		

