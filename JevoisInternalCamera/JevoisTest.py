ser = serial.Serial('/dev/ttyUSB0', 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False) #Tried with and without the last 3 parameters, and also at 1Mbps, same happens.
ser.flushInput()
ser.flushOutput()
While True:
  data_raw = ser.read()
  print(data_raw)
