global pError
global gCurrent
global gTarget
global gP
global gI
global gD
global integral
global pError

def alooksisPID(kP, kI, kD, target, current, dT):
	global pError
	global integral
	error = target - current
	integral = integral + (error * dT)
	derivative = (error - pError) / dT
	output = (kP * error) + (kI * integral) + (kD * derivative)
	pError = error
	return output

gP = 0.2358
gI = 0.2358
gD = 0.118
gCurrent = 0
gTarget = 4000
integral = 0
pError = 0

while (gCurrent > gTarget + 1/(gTarget*100)) | (gCurrent < gTarget - 1/(gTarget*100)):
	gCurrent = alooksisPID(gP, gI, gD, gTarget, gCurrent, 1)
	print (gCurrent)
	#print (pError)
print (gCurrent)
print ("done")

gTarget = 5000

while (gCurrent > gTarget + 1/(gTarget*100)) | (gCurrent < gTarget - 1/(gTarget*100)):
	gCurrent = alooksisPID(gP, gI, gD, gTarget, gCurrent, 1)
	print (gCurrent)
	#print (pError)

gTarget = 2000

while (gCurrent > gTarget + 1/(gTarget*100)) | (gCurrent < gTarget - 1/(gTarget*100)):
	gCurrent = alooksisPID(gP, gI, gD, gTarget, gCurrent, 1)
	print (gCurrent)
	#print (pError)