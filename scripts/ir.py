#!/usr/bin/python

import lirc
sockid = lirc.init('irremote')

while True:
	code = lirc.nextcode()
	if (len(code) > 0):
		code = code[0]
		if(code == 'MENU'):
			print 'Ha presionado el boton Menu!'
		elif(code == 'BACK'):
			print 'Ha presionado el boton Back!'
		elif(code == 'SELECT'):
			print 'Ha presionado el boton Select!'
		elif(code == 'NUMBER_0'):
			print 'Ha presionado el boton 0!'
		elif(code == 'NUMBER_1'):
			print 'Ha presionado el boton 1!'
		elif(code == 'NUMBER_2'):
			print 'Ha presionado el boton 2!'
		elif(code == 'NUMBER_2'):
			print 'Ha presionado el boton 2!'
		elif(code == 'NUMBER_3'):
			print 'Ha presionado el boton 3!'
		elif(code == 'NUMBER_4'):
			print 'Ha presionado el boton 4!'
		elif(code == 'NUMBER_5'):
			print 'Ha presionado el boton 5!'
		elif(code == 'NUMBER_6'):
			print 'Ha presionado el boton 6!'
		elif(code == 'NUMBER_7'):
			print 'Ha presionado el boton 7!'
		elif(code == 'NUMBER_8'):
			print 'Ha presionado el boton 8!'
		elif(code == 'NUMBER_9'):
			print 'Ha presionado el boton 9!'
	pass