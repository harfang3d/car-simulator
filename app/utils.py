def clamp(val, low1, high1):
	return min(max(val, low1), high1)

def range_adjust(val, low1, high1, low2, high2):
	return low2 + (val - low1) * (high2 - low2) / (high1 - low1)

def EaseInOutQuick(x):
	x = clamp(x, 0.0, 1.0)
	return	(x * x * (3 - 2 * x))

def Map(value, min1, max1, min2, max2):
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1)

def metersPerSecondToKMH(meterspersecond):
	return meterspersecond * 3.6 # * 3600 to get the time in hours / 1000 to get in kilometers

def KMHtoMPS(kmh):
	return kmh / 3.6