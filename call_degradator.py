# -*- coding: utf-8 -*-
import os
import degradator

#
# use degradator for a series of files.
#

indir='//ies.jrc.it/H03/Forobs_Export/verhegghen_export/RECAREDD/dataset_RoC_exercice/1_activity_map'
outdir='E:/tmp/'
for fname in ['Likouala_recentchangesCongo_eq_area.tif', 'Sangha_recentchangesCongo_eq_area.tif']:
	print 'Processing {}'.format(fname)
	inputFile = os.path.join(indir, fname)
	outputFileCount = os.path.join(outdir,'count_weighted_easeInOutCubic_{}'.format(fname))
	outputFileVal = os.path.join(outdir,'percent_weighted_easeInOutCubic_{}'.format(fname))
	print outputFileCount

	try:
		myDegradator = degradator.degradator()
		if not myDegradator.openIO(inputFile, outputFileCount, outputFileVal):
			sys.exit(1)

		#myDegradator.doDegradator(fidIn, fidOutCount, fidOutVal, linearLaw, 50.0, 100.0)
		#myDegradator.doDegradator(fidIn, fidOutCount, fidOutVal, easeOutCubic, 50.0, 100.0)
		myDegradator.doDegradator(myDegradator.easeInOutCubic, 50.0, 100.0)
	except IOError, e:
		raise IOError("IOError {}".format(str(e)))
	except Exception, e:
		raise

	fidIn=None
	fidOutCount=None
	fidOutVal=None
#