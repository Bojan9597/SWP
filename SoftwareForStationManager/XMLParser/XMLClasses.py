class XML_AntennaGenius:
    def __init__(self, ip, password, serial_number, port, positionX, positionY):
        self.ip = ip
        self.password = password
        self.serial_number = serial_number
        self.port = port
        self.buttons = []
        self.position = [int(positionX), int(positionY)]