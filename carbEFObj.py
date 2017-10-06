# -*- coding: utf-8 -*-
from __future__ import division
import gdal
import os
import copy
import numpy

def GD2Numpy(gdt):
	if gdt==gdal.GDT_Byte:
		return numpy.dtype('b')
	if gdt>=gdal.GDT_UInt16 and gdt<=gdal_GDT_Int32:
		return numpy.dtype(int)
	if gdt>=gdal.GDT_Float32 or gdt<=GDT_Float64:
		return numpy.dtype(float)

class raster():
	"""
	Create a raster object.
	The object is created by using an existing file (wrapping its properties), or but passing parameters to create one.
	Read and write function are done by block.
	A raster can have several roles in CarbEF: activity, biomass, exception, disaggregation.
	It can support different types of operation: warping, reading a block, writing a block, delete
	"""

	roles = ['activity', 'biomass', 'exception', 'disaggregation', 'MFU_class', 'MFU_biomass']
	roleProperties = {'activity':{'fileType':'input', 'io':gdal.GA_ReadOnly},
					'biomass':{'fileType':'input', 'io':gdal.GA_ReadOnly},
					'exception':{'fileType':'input', 'io':gdal.GA_ReadOnly},
					'disaggregation':{'fileType':'input', 'io':gdal.GA_ReadOnly},
					'MFU_class':{'fileType':'output', 'io':gdal.GA_Update, 'dataType':gdal.GDT_Byte,'of':'GTiff','options':['compress=lzw','predictor=2','bigtiff=YES']},
					'MFU_biomass':{'fileType':'output', 'io':gdal.GA_Update, 'dataType':gdal.GDT_Float32,'of':'GTiff','options':['compress=lzw','bigtiff=YES']}
					}
	role=None
	overwrite=None
	path=None
	fname=None
	properties=None
	fid=None
	parameters={} #{'ns':ns, 'nl':nl,'nb':nb,'dataType':dataType,'geotransform','projection', initWidth=defaultValue}

	IORWTypes = ['ro','rw']

	def __init__(self, path, fname, role, overwrite=False, parameters=None):
		"""
		instantiate a raster object. Get its full path, carbEF role, and overwrite boolean.
		then triggers a validity test.
		parameters is only used for output files. It is mandatory for those files.
		Passing parameters for role['fileType']="input", triggers an error.
		If parameters has dataType, of, or options, these values overwrite the default properies for this role
		"""
		# note: unicode could be an issue
		self.role = role.lower()
		self.overwrite = overwrite
		self.path = path
		self.fname = fname

		if self.role not in self.roles:
			raise ValueError('carbEFObj.raster.__init__: role "{}" is unknown.'.format(self.role))

		self.properties = self.roleProperties[self.role]

		self._isValid() # return true or returns and error
		if self.properties['fileType'] == 'output':
			# output type raster must have some parameters defined, else they are read from the file
			if any(parameters) :
				# set properties default first
				# then can be overwritten by passing them in the parameters dictionary when instantiating the object, with __init__
				self.parameters["dataType"] = self.properties.get('dataType',None)
				self.parameters["of"] = self.properties.get('of', None)
				self.parameters["options"] = self.properties.get('options',None)
				self.parameters = parameters #set ns, nl, nb, dataType, geotransform, projection
			else:
				raise ValueError("carbEFObj.raster.__init__: missing parameters for creating this object")
		else: # open the file in read mode.
			self._openReadFile()

	def _isValid(self):
		""" different checks depending on the type (input or output) of file
		Input file must exist.
		Output should not exist: if overwrite, then delete first, else raise error
		return True or raise an error
		"""

		if self.properties['fileType'] == 'input':
			# must exist
			if not self._exists():
				raise IOError('Input file {} does not exist.'.format(os.path.join(self.path, self.fname)))
			else:
				return True
		elif self.properties['fileType'] == 'output':
			# if exists: if overwrite: delete, else raise error
			if self._exists():
				if self.overwrite:
					_delete()
				else:
					raise IOError("Output file {} exists, and overwrite set to {}".format(os.path.join(self.path, self.fname), self.overwrite))
			return True #else raise error

		else:
			raise ValueError('carbEFObj.raster._isValid: unknown fileType {}'.format(thisProperty['fileType']))

	def _exists(self):
		""" True if the file exists, i.e. found on the hard drive, False else
			Raise IOErrors
		"""
		try:
			if os.path.exists(os.path.join(self.path, self.fname) ):
				return True
			else:
				return False
		except IOError,e:
			raise IOError("carbEFObj.raster._exists: IOError {}".str(e))

	def _openReadFile(self):
		"""
		Opens a file, in read mode.
		"""
		try:
			if self.fid is None:
				self.fid = gdal.Open(os.path.join(self.path, self.fname), self.properties['io'])
			self.parameters['ns'] = self.fid.RasterXSize
			self.parameters['nl'] = self.fid.RasterYSize
			self.parameters['nb'] = self.fid.RasterCount
			self.parameters['dataType'] = self.fid.GetRasterBand(1).DataType
			self.parameters['projection'] = self.fid.GetProjection()
			self.parameters['geotransform'] = self.fid.GetGeoTransform()
		except:
			raise IOError('carbEFObj.raster._openFile: error while trying to open or access info of {}'.format(os.path.join(self.path, self.fname)))

	def _openWriteFile(self):
		"""
		Opens a file in write mode.
		Gets creation parameters from object instance definitions, uses function default in case of missing definition.
		"""
		try:
			if self.fid is None:
				of = self.properties.get('of','gtiff')
				options=self.properties.get('options',['compress=lzw','bigtiff=YES'])
				ns = self.parameters.get("ns", None)
				nl = self.parameters.get("nl", None)
				nb = self.parameters.get("nl", None)
				dt = self.parameters.get("dataType", None)
				geotrans = self.parameters.get("geotransform", None)
				proj = self.parameters.get("projection", None)

				drv = gdal.GetDriverByName(of)
				if ns is None or nl is None or nb is None or dt is None:
					raise ValueError("carbEFObj.raster._openWriteFile: image dimensions or dataType not set ns:{}, nl:{}, nb:{}, dataType: {}".format(ns, nl, nb, dt))
				if geotransform is None or proj is None:
					raise ValueError("carbEFObj.raster._openWriteFile: image projection or geotransform no set geotransform: {}, projection: {}".format(geotransform, projection))
				self.fid = drv.Create(os.path.join(self.path, self.fname), ns, nl, nb, dt, options=options)

				# shall we init the file?
				if self.parameters.get('initWidth', None) is not None:
					initRow = numpy.zeros((ns,1), dtype=GD2Numpy(dt)) + self.parameters.get('initWidth')
					for ib in xrange(nb): # shortest loop outside
						for il in xrange(nl):
							self.fid.GetRasterBand(ib+1).WriteArray(initRow, 0, il)

		except IOError,e:
			raise("carbEFObj.raster._openWriteFile: error when creating file {}".format(os.path.join(self.path, self.fname)))

	def readBlock(self, xoff, yoff, xwidth, ywidth, ib=1):
		if self.fid is None:
			self._openReadFile()
		if ib <= 0:
			raise('carbEFObj.raster.readBlock: ib must be >0, got {}'.format(ib))
		try:
			thisData = self.fid.GetRasterBand(ib).ReadAsArray(xoff,yoff,xwidth,ywidth)
			return thisData
		except:
			raise IOError('carbEFObj.raster.readBlock: error while accessing block with xoff:{}, yoff:{}, xwidth:{}, ywidth:{}, ib:{}'.format(xoff,yoff,xwidth,ywidth,ib))

	def writeBlock(self, thisData, xoff=0, yoff=0, ib=1):
		"""
		write a 2-d block, at position xoff, yoff, in band ib
		thisData MUST be 2d
		"""
		if self.fid is None:
			self._openWriteFile(self)
		if ib <= 0:
			raise('carbEFObj.raster.readBlock: ib must be >0, got {}'.format(ib))
		try:
			self.fid.GetRasterBand(ib).WriteArray(thisData, xoff, yoff)
		except IOError,e:
			raise("carbEFObj.raster.writeBlock: IOError when writting block of shape {} at position xoff:{} yoff:{} in file {}".format(thisData.shape, xoff, yoff, os.path.join(self.path, self.fname)))

	def updateBlockMasked(self, thisData, xoff=0, yoff=0, ib=1, nodata=0):
		"""
		update a block. Read existing data, and merge with thisData, using nodata as a transparent value in thisData.
		"""
		# read data at the same place
		xWdidth, yWidth = thisData.shape
		data = self.fid.GetRasterBand(ib).ReadAsArray(xoff, yoff, xWidth, yWdith)
		# combine by masking
		mask = thisData != nodata
		data[mask] = thisData[mask]
		# rewrite
		self.fid.GetRasterBand(ib).WriteArray(data, xoff, yoff)
