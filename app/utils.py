import harfang as hg

def Clamp(val, low1, high1):
	return min(max(val, low1), high1)

def RangeAdjust(val, low1, high1, low2, high2):
	return low2 + (val - low1) * (high2 - low2) / (high1 - low1)

def EaseInOutQuick(x):
	x = Clamp(x, 0.0, 1.0)
	return	(x * x * (3 - 2 * x))

def Map(value, min1, max1, min2, max2):
    return min2 + (value - min1) * (max2 - min2) / (max1 - min1)

def MetersPerSecondToKMH(meterspersecond):
	return meterspersecond * 3.6 # * 3600 to get the time in hours / 1000 to get in kilometers

def KMHtoMPS(kmh):
	return kmh / 3.6

def NodeGetPhysicsMass(node):
    n = node.GetCollisionCount()
    mass = 0
    for i in range(n):
        col = node.GetCollision(i)
        mass = mass + col.GetMass()

    return mass

def NodeGetPhysicsCenterOfMass(node):
    mass = NodeGetPhysicsMass(node)
    n = node.GetCollisionCount()
    center_of_mass = hg.Vec3(0,0,0)
    for i in range(n):
        col = node.GetCollision(i)
        mass_ratio = col.GetMass() / mass
        center_of_mass = center_of_mass + (hg.GetTranslation(col.GetLocalTransform()) * mass_ratio)

    return center_of_mass
