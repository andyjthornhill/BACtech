from PyQt5 import QtWidgets, uic
import sys, os
import BAC0
from collections import defaultdict

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

class Ui(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('BACTech.ui', self)
        
        self.bacnet = None
        self.ipAddress = ""
        self.subMask = ""
        self.port = ""
        
        self.connectButton = self.findChild(QtWidgets.QPushButton, 'connectButton')
        self.connectButton.clicked.connect(self.connectButtonPressed) 
        self.scanButton = self.findChild(QtWidgets.QPushButton, 'scanButton')
        self.scanButton.clicked.connect(self.scanButtonPressed) 
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton')
        self.sendButton.clicked.connect(self.sendButtonPressed) 
        self.helpButton = self.findChild(QtWidgets.QPushButton, 'helpButton')
        self.helpButton.clicked.connect(self.helpButtonPressed) 
        self.ipInput = self.findChild(QtWidgets.QLineEdit, 'ipInput')
        self.subMaskInput = self.findChild(QtWidgets.QLineEdit, 'subMaskInput')
        self.portInput = self.findChild(QtWidgets.QLineEdit, 'globalIpInput') 
        self.maxInput = self.findChild(QtWidgets.QLineEdit, 'maxInput') 
        self.minInput = self.findChild(QtWidgets.QLineEdit, 'minInput')
        self.pointType = self.findChild(QtWidgets.QComboBox, 'pointSelect')
        self.pointNum = self.findChild(QtWidgets.QSpinBox, 'pointNum')
        self.analogVal = self.findChild(QtWidgets.QSpinBox, 'analogInput')
        self.binaryVal = self.findChild(QtWidgets.QComboBox, 'binaryInput')
        self.priorityVal = self.findChild(QtWidgets.QComboBox, 'priorityInput')
        
        self.scanButton.setEnabled(False)
        self.sendButton.setEnabled(False)

        self.show()

    """
    Connect BACtech to the BACnet network
    TODO: 
        Auto-detect IP address from Ethernet Adapter
        Allow for input of slash notation and standard notation for subnet mask (/24 or 255.255.255.0)
    """
    def connectButtonPressed(self):
        #Pull data provided by user
        self.ipAddress = self.ipInput.text() #IP address
        self.subMask = self.subMaskInput.text() #Subnet mask (slash notation)
        self.port = self.portInput.text() #UDP port
        str = self.ipAddress + self.subMask + ":" + self.port

        #Build connection through the adapter matching with the provided IP address:
        print("Connecting using: " + str)
        self.bacnet = BAC0.lite(str)

        #Allow user to Detect/Scan devices
        self.scanButton.setEnabled(True)
        
    """
    Detects all devices on BACnet network (both IP and MS/TP devices)
    TODO:
        Utilize existing data from Alerton Compass device manager (different button maybe?)
    """
    def scanButtonPressed(self):
        print("SCANNING")
        self.bacnet.discover() #discovers all devices and networks
        devices = self.bacnet.devices #format = [(name, description, ip/mstp network, inst)]

        #Print Found devices
        for i in devices:
            print(i[3])
        
        #allow user to send data
        self.sendButton.setEnabled(True)
        

    """
    Takes a range of device instances and returns a list of all addresses of devices found within that range
    """
    def instanceToAddr(self, min, max):
        devices = self.bacnet.devices
        addrs = []
        n = 0
        for i in range(min,max+1):
            for dev in devices:
                if(i == dev[3]):
                    addrs.append(dev[2])
                    n += 1
        return addrs

    """
    Handles all functionality when the send button is pressed
    """
    def sendButtonPressed(self):
        #Pull data provided by user
        #Device Instance Range
        min = int(self.minInput.text())
        max = int(self.maxInput.text())

        #Point to adjust
        point = self.pointType.currentText()
        pointnum = str(self.pointNum.value())
        
        #Data for the point
        binary = self.binaryVal.currentText()
        analog = int(self.analogVal.value())
        
        #Priority array value
        priority = int(self.priorityVal.currentText())


        #Converting given data to a string that can be used to send the data
        value = " presentValue"
        if(point == "AV"):
            point = "analogValue"
            if(analog == 0 and binary == "NULL"): value += " " + binary
            else: value += " " + str(analog)
        elif(point == "BV"):
            point = "binaryValue"
            value += " " + str(binary)
        elif(point == "AO"):
            point = "analogOutput"
            if(analog == 0 and binary == "NULL"): value += " " + binary
            else: value += " " + str(analog)
        elif(point  == "BO"):
            point = "binaryOutput"
            value += " " + str(binary)
        point += " " + pointnum
        point += value

        #Get range of address from range of device instances
        addrs = self.instanceToAddr(min, max)

        #Iterates through range of addresses and sends the pointdata to each device found in range
        print("Sending data to " + str(len(addrs)) + " devices")
        print(point)
        for i in addrs:
            #EX: 1100:5 analogValue 90 presentValue 70
            self.bacnet.write(i + " " + point + value)
        
    """
    TODO: Open window listing instructions (PDF? TXT? Popup?)
    """
    def helpButtonPressed(self):
        return



app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.setWindowTitle("BACtech")
app.exec_()