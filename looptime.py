from datetime import datetime


a=0
longRange=1000000
shortRange=10
t1 = datetime.now()
for ii in xrange(longRange):
	for jj in xrange(shortRange):
		a=1
t2 = datetime.now()
delta=t2-t1
print delta.total_seconds()