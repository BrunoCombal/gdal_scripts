# -*- coding: utf-8 -*-
import unittest
import carbEFObj

class test_carbef(unittest.TestCase):
	def setUp(self):
		self.path='./test_data/'
		self.fname='Sangha_recentchangesCongo_eq_area.tif'

	def tearDown(self):
		self.path=''
		self.fname=''
		activity=None
		del activity
		biomass=None
		del biomass
		exception=None
		del exception
		disag = None
		del disag


	def test_fileRoles2(self):
		activity = carbEFObj.raster(self.path, self.fname, 'activity')
		self.assertIsNotNone(activity)
	def test_fileRoles3(self):
		biomass = carbEFObj.raster(self.path, self.fname, 'biomass')
		self.assertIsNotNone(biomass)
	def test_fileRoles4(self):
		exception = carbEFObj.raster(self.path, self.fname, 'exception')
		self.assertIsNotNone(exception)
	def test_fileToles5(self):
		disag = carbEFObj.raster(self.path, self.fname, 'disaggregation')
		self.assertIsNotNone(disag)
	def test_parametersExist(self):
		activity = carbEFObj.raster(self.path, self.fname, 'activity')
		ok=True
		for ii in ['ns','nl','nb','dataType','geotransform','projection']:
			test = activity.parameters.get(ii, False)
			if not test: # ok set to False if key not found
				ok = False
		self.assertTrue(ok)
	def test_parametersValues(self):
		activity = carbEFObj.raster(self.path, self.fname, 'activity')
		ok = True
		for ii in ['ns','nl','nb','dataType','geotransform','projection']:
			test = activity.parameters.get(ii, False)
			if test is None: # if any value set to None, test fails
				ok = False
		self.assertTrue(ok)


if __name__ == '__main__':
    unittest.main()