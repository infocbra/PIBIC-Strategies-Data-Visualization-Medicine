# This Python file uses the encoding: utf-8
import sys
import os
from patient import Patient
import utils
import time
import data_structure as ds
import threads as th
from datetime import datetime
from threading import Thread

from PySide2.QtCore import QObject, Slot, Signal
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

#Global variables
patient = None
path = ""
file_path = None
file_type = ".csv"
frequency = 50 #default frequency Hz
bufferSize = 60
sock = None
address = None
connected=False
signedUp = False
data_buffer = None
taskInterval = 30 #interval of realization of each task
header = "time,accx,accy,accz,gyx,gyy,gyz,temperature"
receiveThread = None
saveThread = None
showLog = False
tasks = ""

# Control of Patient sign up screen
class PatientWindow(QObject):
    def __init__(self):
        QObject.__init__(self)
    
    #patient data configuration of signal receiving
    patientData = Signal(bool,str)

    #receive data from frontend
    @Slot(str,bool,bool,str,bool,bool,str)
    def savePatientData(self,name,female,male,birthday,parkinsonian_y,parkinsonian_n,path):
        global signedUp, file_path, patient
        error=""
        success = True
        if(len(name)<2):
            error = 'Name was not inserted'
            success = False
        if(path=="Select folder to save data..."):
            error = 'Path was not selected'
            success=False
        else:
            name=str(name)
            sex = "Female" if female else "Male"
            birthday=str(birthday)
            parkisonian = True if parkinsonian_y else False
            path = str(path)
            patient=Patient(name,birthday,sex,parkisonian)
            signedUp = True
            file_path = str(utils.createFile(path,patient,file_type))
            
        self.patientData.emit(success,error)

class SettingsWindow(QObject):
    def __init__(self):
        QObject.__init__(self)

    searchDeviceSig = Signal(list)

    connectToDevice = Signal(bool,str)

    @Slot(bool)
    def updateLogView(self,log):
        global showLog
        showLog = bool(log)

    @Slot(str)
    def updateFrequency(self,freq):
        global frequency
        frequency = int(freq)

    @Slot(str)
    def updateHeader(self,head):
        global header
        header = str(head)
        print(header)

    @Slot(str)
    def updateBufferSize(self,buffer_size):
        global bufferSize
        bufferSize = int(buffer_size)

    @Slot()
    def searchDevice(self):
        listDevice = utils.findBluetoothDevices(5)
        print(listDevice)
        self.searchDeviceSig.emit(listDevice)

    @Slot(str)
    def connect(self,device):
        global sock
        global address
        global connected

        success = True
        
        name,addr = device.split('|')
        addr = addr.strip()
        name = name.strip()
        sock = utils.connectBluetooth(addr)

        if(sock==None):
            success=False
        address=addr
        connected = True if success else False

        global data_buffer, bufferSize
        data_buffer = ds.RingBuffer(bufferSize)

        self.connectToDevice.emit(success,name)

class CollectionWindow(QObject):
    def __init__(self):
        QObject.__init__(self)
    
    startSig = Signal(bool)
    updateGif = Signal(str)

    def changeGif(self,tasks,interval):
        gifPaths = {
            "rest": "../../images/gifs/rest.gif",
            "flexion": "../../images/gifs/flexion.gif",
            "ulnar deviation": "../../images/gifs/ulnar.gif",
            "radial deviation": "../../images/gifs/radial.gif",
            "against gravity": "../../images/gifs/against gravity.gif"
        }

        for i in range(len(tasks)):
            print(gifPaths[tasks[i].lower()])
            self.updateGif.emit(gifPaths[tasks[i].lower()])
            time.sleep(interval)
            self.updateGif.emit("../../images/gifs/countdown.gif")
            time.sleep(5.5)
        time.sleep(5)
        self.updateGif.emit("../../images/gifs/logo.gif")



    @Slot(str,list,bool,bool)
    def start(self,interval,taskss,showVideo,showAudio): #TODO function to start collection
        global file_path, patient, header,data_buffer,sock,tasks,taskInterval, receiveThread, saveThread, showLog
        sTime = datetime.now()
        tasks = taskss
        utils.createHeader(file_path,patient,interval,tasks,sTime,header) #file_path, patient, tsk_duration, tasks, startTime, header
        receiveThread = th.BluetoothAcquisitionThread(data_buffer, sock, showLog)
        saveThread = th.DataSavingThread(data_buffer, patient, file_path, showLog)
        receiveThread.start()
        saveThread.start()

        thread = Thread(target=self.changeGif,args=[tasks,taskInterval])
        thread.start()


    @Slot(str,list,bool,bool)
    def stop(self,interval,tasks,showVideo,showAudio): #TODO function to stop collection
        return 0


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    #Get Context
    patientWindow = PatientWindow()
    engine.rootContext().setContextProperty('save_patient',patientWindow)

    settingsWindow = SettingsWindow()
    engine.rootContext().setContextProperty('settings_backend',settingsWindow)

    collectWindow = CollectionWindow()
    engine.rootContext().setContextProperty('collect_backend',collectWindow)

    #Load qml file
    engine.load(os.path.join(os.path.dirname(__file__), "qml/main.qml"))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())