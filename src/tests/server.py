import bluetooth
import csv
import threading
import os
import time

csv_file = None
class SaveData(threading.Thread):
	def __init__(self,data,file):
		threading.Thread.__init__(self)
		self.data = data
		self.file = file
	def run(self):
		csv_file = open(self.file, 'a', newline='')
		writer = csv.writer(csv_file)
		writer.writerow(self.data)
		csv_file.close()

if __name__ == "__main__":
	# BT MAC ADDR da raspberry ou do cliente?
	bd_addr = "00:18:E4:40:00:06"
	port = 1
	sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

	# Subject information
	subject_name = input("Type the name of the subject: ")
	subject_age = int(input("Type the age of the subject: "))
	subject_sex = input("Masculine or Femine subject?(M/F)? ")
	subject_stat = input("Is the subject a detected parkinsonian?[Y or n]: ")

	try:
		if not os.path.exists("data/"):
			os.makedirs("data/")
		open("data/{}.csv".format(subject_name), 'w+').close()
		f = open("data/{}.head".format(subject_name),'w+')
		f.write("name: {}\n".format(subject_name)+
			"age: {}\n".format(subject_age)+
			"sex: {}\n".format(subject_sex)+
			"parkinsonian? {}\n".format(subject_stat))
		f.close()
	except:
		print("ERROR CREATING CSV DATA FILE!!")

	path = "data/"+subject_name+".csv"
	while (True):
		sock.connect((bd_addr, port))
		print('Connected')
		# sock.settimeout(1.0)
		
		s = input()
		sock.sendall(s.encode('ASCII'))
		data = ''
		try:
			while (True):
				data += sock.recv(64).decode('ASCII')
				if '#' in data:
					data = data.split('#')
					data1 = data[0]
					data = data[1]

					if data1 == "ok":
						sock.sendall('c')
					elif data1 == "stop" or "stop" in data or "SudoStop" in data:
						csv_file.close()
						for i in range(10):
							print("Saving and finishing data saving..."+str(i))
							time.sleep(1)
						break
					else:
						dataLine = data1.split(',')
						saveData = SaveData(list(dataLine),path)
						saveData.start()
						saveData.join()
		except Exception as inst:
			print(type(inst))  # the exception instance
			print(inst.args)  # arguments stored in .args
			print(inst)
			print("Erro!!!")
			sock.close()

		sock.close()
