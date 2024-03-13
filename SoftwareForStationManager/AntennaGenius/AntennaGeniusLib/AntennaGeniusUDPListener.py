from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtNetwork import QUdpSocket
from PyQt5.QtWidgets import QApplication
import sys
import re
from time import sleep
from PyQt5.QtCore import QObject

class UdpListener(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, serial_number, parent=None):
        super(UdpListener, self).__init__(parent)
        self.serial_number = serial_number
        self.udp_socket = QUdpSocket()

    def run(self):
        self.udp_socket.bind(9007)
        self.udp_socket.readyRead.connect(self.read_pending_datagrams)

    def read_pending_datagrams(self):
        while self.udp_socket.hasPendingDatagrams():
            datagram_size = self.udp_socket.pendingDatagramSize()
            data, sender_host, sender_port = self.udp_socket.readDatagram(datagram_size)
            ip_address = self.extract_ip_address(data)
            if (self.serial_number + " ") in data.decode():
                if ip_address is not None:
                    self.data_received.emit(ip_address)
                    return


    def extract_ip_address(self, data_stream):
        data_stream = data_stream.decode()
        ip_address_match = re.search(r'ip=([0-9.]+)', data_stream)
        if ip_address_match:
            return ip_address_match.group(1)
        else:
            return None
