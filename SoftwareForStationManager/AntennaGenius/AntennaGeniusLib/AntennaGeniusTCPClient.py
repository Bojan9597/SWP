from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket
import re
from collections import defaultdict
import time
from AntennaGenius.AntennaGeniusLib.AntennaGeniusUDPListener import UdpListener

class AntennaGeniusTCPClient(QObject):
    # Define signals
    AntennaGeniusConnectionLANResponse = "AG"
    AntennaGeniusConnectionWANResponse = "AG AUTH"
    ResponseTimeoutForWANAuhtentication = 2

    regularResponsesDict = defaultdict(list)
    regularSuccesufulResponsePattern = r"R(\d+)\|(\d+)\|(.*?)$"
    statusSuccesufulResponsePattern = r"S(\d+)\|(\d+)\|(.*?)$"

    # Signals
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    errorOccurred = pyqtSignal(str)
    regularResponseReceived = pyqtSignal(int, list, int)
    statusResponseReceived = pyqtSignal(str)

    def __init__(self, ip_address, port, auth_code="", serial_number=""):
        super().__init__()
        self.ip_address = ip_address
        self.port = port
        self.auth_code = auth_code
        self.serial_number = serial_number
        self.socket = QTcpSocket()
        self.socket.readyRead.connect(self.process_response)
        self.socket.errorOccurred.connect(self.handle_error)
        self.socket.disconnected.connect(self.disconnect)
        self.connected_status = False
        self.sequence_number = 1
        self.timer = QTimer()
        self.timer.timeout.connect(self.attempt_connection)
        self.udp_listener = UdpListener(self.serial_number)

        self.udp_listener.data_received.connect(self.on_udp_data_received)
        
        self.auth_sent = False  # Flag to track if authentication command has been sent
        self.socket.connected.connect(self.onConnected)

        if self.ip_address != None:
            self.timer.start(5000)  # Start the timer with a 5-second interval
            self.attempt_connection()
        else:
            self.udp_listener.run()

        self.responseTime = time.time()

    def on_udp_data_received(self, ip_address):
        self.ip_address = ip_address
        self.timer.start(5000)
        self.udp_listener.data_received.disconnect(self.on_udp_data_received)
        self.attempt_connection()
        

    def onConnected(self):
        self.timer.stop()
        self.connected_status = True
        self.connected.emit()

    def attempt_connection(self):
        if self.socket.state() == QAbstractSocket.ConnectedState:
            self.timer.stop()
            return

        if self.socket.state() == QAbstractSocket.ConnectingState:
            return

        try:
            self.socket.connectToHost(QHostAddress(self.ip_address), int(self.port))

        except Exception as e:
            self.errorOccurred.emit(str(e))
            print(f"Error occurred: {e}")
            print("Retrying...")

    def process_response(self):
        self.responseTime = time.time()
        while self.socket.bytesAvailable():
            data = self.socket.readAll().data().decode('utf-8')
            for response in data.split("\n"):
                if response:
                    if response.startswith("R"):
                        match = re.match(self.regularSuccesufulResponsePattern, response)
                        if match:
                            if match.group(3) != "":
                                self.regularResponsesDict[match.group(1)].append(match.group(3))
                                if match.group(3).startswith("conf") or match.group(3).startswith("info") or match.group(3).startswith("network") or match.group(3).startswith("stack") or match.group(3).startswith("port"):
                                    self.regularResponsesDict[match.group(1)].append(match.group(3))
                                    self.regularResponseReceived.emit(int(match.group(1)), self.regularResponsesDict[match.group(1)], int(match.group(2)))
                                    self.regularResponsesDict[match.group(1)] = []
                            else:
                                self.regularResponsesDict[match.group(1)].append(match.group(3))
                                self.regularResponseReceived.emit(int(match.group(1)), self.regularResponsesDict[match.group(1)], int(match.group(2)))
                                self.regularResponsesDict[match.group(1)] = []
                    elif response.startswith("S"):
                        self.statusResponseReceived.emit(response[3:])
                    else:
                        if not self.auth_sent and self.AntennaGeniusConnectionWANResponse in response:
                            self.send_command(f"auth code={self.auth_code}")
                            self.auth_sent = True

    def disconnect(self):
        try:
            if self.timer != None or self.socket != None:
                self.timer.start(5000)
                self.socket.disconnectFromHost()
                self.connected_status = False
                self.disconnected.emit()  # Emit disconnected signal
        except Exception as e:
            print(f"Error occurred: {e}")

    def isConnected(self):
        return self.connected_status
    
    def get_next_sequence_number(self):
        self.sequence_number = (self.sequence_number+1)%250
        return self.sequence_number

    def send_command(self, command):
        sequence_number = self.get_next_sequence_number()
        if not self.isConnected():
            print("Not connected to the device.")
            return
        full_command = f"C{sequence_number}|{command}\r\n"
        try:
            bytes_sent = self.socket.write(full_command.encode())
            if bytes_sent == -1:
                print("Error sending command.")
                if self.socket != None or self.timer != None:
                    self.disconnect()
            return sequence_number
        except Exception as e:
            print(f"Exception in send_command function: {e}")
            return sequence_number

    def handle_error(self, socket_error):
        error_message = self.socket.errorString()
        self.errorOccurred.emit(error_message)
