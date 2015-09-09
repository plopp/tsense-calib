# -*- coding: utf-8 -*-
from Tkinter import *
import time
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
modbus = ModbusClient('192.168.1.9')
import matplotlib
#matplotlib.use('QT4Agg')
import numpy as np
import matplotlib.pyplot as plt
from PyQt4 import QtCore,QtGui


tsense_arr = [10,11,12,13,14,15,16,17,18,19]
variable_arr = []

root = Tk()
root.wm_title("Kalibrering tSense SenseAir")
root.minsize(width=(int(len(tsense_arr)/(len(tsense_arr)/4))-1)*200, height=666)
root.maxsize(width=666, height=666)
Label(root, text="Adressen står på en dymolapp i underkant på varje givare.", justify="left", anchor="w").place(x=10,y=10)

for addr in tsense_arr:
	variable_arr.append([StringVar(),StringVar(),StringVar()])

yarr_ppm = []
yarr_temp = []
yarr_hum = []

for addr in tsense_arr:
	yarr_ppm.append(np.zeros(1000))
	yarr_temp.append(np.zeros(1000))
	yarr_hum.append(np.zeros(1000))



def readModbus():
	for idx,addr in enumerate(tsense_arr):
		rr = modbus.read_input_registers(3,3, unit=addr)
		#print "%s\t Unit: %d\tCO2: %.0f ppm\tTemp: %.2f C\t Hum: %.2f RH" % (time.asctime(time.localtime()),addr,rr.registers[0],rr.registers[1]/100.0,rr.registers[2]/100.0)
		tup = (time.time(),rr.registers[0],rr.registers[1]/100.0,rr.registers[2]/100.0)

		variable_arr[idx][0].set(str(rr.registers[0]))
		variable_arr[idx][1].set(str(rr.registers[1]/100.0))
		variable_arr[idx][2].set(str(rr.registers[2]/100.0))

		yarr_ppm[idx][:-1] = yarr_ppm[idx][1:]
		yarr_ppm[idx][-1:] = np.array(tup[1])

		yarr_temp[idx][:-1] = yarr_temp[idx][1:]
		yarr_temp[idx][-1:] = np.array(tup[2])

		yarr_hum[idx][:-1] = yarr_hum[idx][1:]
		yarr_hum[idx][-1:] = np.array(tup[3])
	# set the new data

	#root.update_idletasks()
	root.after(500, readModbus)

def callback(_in):
	fig = plt.figure(''.join(["Address ",str(_in)]))
	#ax = fig.add_subplot(111)
	ax1 = fig.add_subplot(311)
	ax1.set_title("CO2")
	ax1.set_ylabel("ppm")
	ax2 = fig.add_subplot(312)
	ax2.set_title("Temp")
	ax2.set_ylabel("deg C")
	ax3 = fig.add_subplot(313)
	ax3.set_title("Hum")
	ax3.set_ylabel("%RH")
	ax3.set_xlabel("Samples")

	x = np.arange(1000)
	idx = tsense_arr.index(_in)



	li1, = ax1.plot(x,yarr_ppm[idx])
	li2, = ax2.plot(x,yarr_temp[idx])
	li3, = ax3.plot(x,yarr_hum[idx])
	fig.canvas.draw()
	plt.show(block=False)

	li1.set_ydata(yarr_ppm[idx])
	li2.set_ydata(yarr_temp[idx])
	li3.set_ydata(yarr_hum[idx])

	fig.canvas.draw()
	#QtGui.qApp.processEvents()

def close(_in):
	plt.close()

for idx,addr in enumerate(tsense_arr):
	group = LabelFrame(root, text=''.join(["Addr ",str(addr)]), padx=5, pady=5)
	group.place(x=(idx%4)*195+10,y=(idx/4)*110+40,width=195,height=110)

	Label(group, text="CO2:", justify="left", anchor="w").grid(row=1,column=1, sticky='w')
	Label(group, textvariable=variable_arr[idx][0], justify="right", anchor="e", width=10).grid(row=1,column=2, sticky='e')
	Label(group, text="ppm", justify="left", anchor="w").grid(row=1,column=3, sticky='w')

	Label(group, text="Temp:", justify="left", anchor="w").grid(row=2,column=1, sticky='w')
	Label(group, textvariable=variable_arr[idx][1], justify="right", anchor="e").grid(row=2,column=2, sticky='e')
	Label(group, text="°C", justify="left", anchor="w").grid(row=2,column=3, sticky='w')

	Label(group, text="Hum:", justify="left", anchor="w").grid(row=3,column=1, sticky='w')
	Label(group, textvariable=variable_arr[idx][2], justify="right", anchor="e").grid(row=3,column=2, sticky='e')
	Label(group, text="%RH", justify="left", anchor="w").grid(row=3,column=3, sticky='w')
	Button(group, text="Graph", command= lambda j=addr: callback(j)).grid(row=4,column=1, sticky='w')

	# label2 = Label(group, text="Temperature", justify="left", anchor="w")
	# label2 = Label(group, text="<Value>", justify="right", anchor="e")
	# label2.pack(side=RIGHT)

	# label3 = Label(group, text="Humidity", justify="left", anchor="w")
	# label3.pack()
	# label3 = Label(group, text="<Value>", justify="right", anchor="e")
	# label3.pack(side=RIGHT)


root.after(500, readModbus)
root.mainloop()

