import numpy
import math

# source: https://en.wikipedia.org/wiki/Dynamic_time_warping

# input: source=array[1..n], target=array[1..m]
def DTWDistance(s, t):
    n=s.size
    m = t.size
    DTW = numpy.zeros((n+1,m+1))
    infinity = 1.e38
    
    # initialising
    for i in xrange(1, n+1, 1):
        DTW[i, 0] = infinity
    for i in xrange(1, m+1, 1):
        DTW[0, i] = infinity
    DTW[0, 0] = 0

    for i in xrange(1, n+1, 1):
        for j in xrange(1, m+1, 1):
            cost = math.fabs( s[i-1] - t[j-1] )
            DTW[i, j] = cost + min(DTW[i-1, j  ],  # insertion
                                       DTW[i  , j-1],  # deletion
                                       DTW[i-1, j-1])    #match
    
    return DTW[n, m]


source=numpy.array([0.1,0.2,0.3,0.3,0.28,0.25,0.26])
target=source
print DTWDistance(source, target)

target = numpy.array([0.1,0.21,0.29,0.31,0.28,0.25,0.26])
print DTWDistance(source, target)

target = numpy.array([0.1,0.21,0.29,0.36,0.28,0.25,0.16])
print DTWDistance(source, target)

target = numpy.array([0.2,0.3,0.3,0.28,0.25,0.26])
print DTWDistance(source, target)
