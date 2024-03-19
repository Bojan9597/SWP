import spidev
import RPi.GPIO as GPIO
import time
import os
import sys
import ctypes
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

# Define constants
SPI_DEVICE = "/dev/spidev0.1"
SPI_MODE = 0b01
SPI_BITS_PER_WORD = 8
SPI_SPEED_HZ = 100000

LED_DATA_SIZE = 24 * 3
LEDARRAYSIZE = 24
BUTTONNUMBER = 33
ENCODERNUMBER = 12
PHYSICALBUTTONNUMBER = 24
POLLING_TIME_MS = 100

send_board = None

class ControlBoard(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("LED_buffer", ctypes.c_uint8 * LED_DATA_SIZE),
        ("encoder_count", ctypes.c_int8 * ENCODERNUMBER),
        ("buttons", ctypes.c_uint8 * 6),
        ("dummy", ctypes.c_uint8)
    ]

class UI_ControlBoardReader(QObject):
    buttonPressed = pyqtSignal(int)
    controlBoardSignal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.counter = 0

        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 1)
            self.spi.mode = SPI_MODE
            self.spi.bits_per_word = SPI_BITS_PER_WORD
            self.spi.max_speed_hz = SPI_SPEED_HZ
        except FileNotFoundError:
            print("Error: SPI device not found")

        self.send_board = ControlBoard()
        self.receive_board = ControlBoard()

        self.rgbArray = [self.LED_pixel() for _ in range(LEDARRAYSIZE)]
        self.buttonArray = [False] * BUTTONNUMBER
        self.encoderArray = [0] * ENCODERNUMBER

        self.buttonMapping = [
            (3, 32), (3, 16), (3, 8), (3, 4), (3, 2), (3, 1),
            (2, 32), (2, 16), (2, 8), (2, 4), (2, 2), (2, 1),
            (0, 2), (0, 1), (0, 8), (0, 4), (0, 32), (0, 16),
            (1, 2), (1, 1), (1, 8), (1, 4), (1, 32), (1, 16),
            (4, 1), (4, 2), (4, 4), (4, 8), (4, 16), (4, 32),
            (5, 1), (5, 2), (5, 4)
        ]

        # Initialize SPI file descriptor and buffer length
        self.spi_fd = None
        self.control_board_size = ctypes.sizeof(ControlBoard())
        self.buffer_len = self.control_board_size + 1

    # Define nested LED_pixel class
    class LED_pixel:
        def __init__(self):
            self.red = 0
            self.green = 0
            self.blue = 0

    # Define interrupt handler function
    def handle_interrupt(self, event):
        self.counter += 1
        global send_board
        # print("Interrupt occurred:", event)
        # print("Counter:", self.counter)

        # Transmit data over SPI
        send_board_bytes = bytearray(self.control_board_size+1)
        self.spi.xfer(send_board_bytes)

        # Receive data over SPI and update receive_board
        in_buffer = bytes(self.spi.readbytes(self.buffer_len+1)) 
        writable_buffer = ctypes.create_string_buffer(in_buffer[2:])
        self.receive_board = ControlBoard.from_buffer(writable_buffer)
        
        # for byte in ctypes.string_at(ctypes.addressof(self.receive_board), ctypes.sizeof(self.receive_board)):
            # print(f"{byte:4d}", end="")
        
        for i in range(BUTTONNUMBER):
            if self.receive_board.buttons[self.buttonMapping[i][0]] == self.buttonMapping[i][1]:
                print("Button", i, "pressed")
                if not self.buttonArray[i]:
                        self.buttonArray[i] = True
                        self.controlBoardSignal.emit(i)
                else:
                    print("Callback not set")
            else:
                self.buttonArray[i] = False
                
        for i in range(PHYSICALBUTTONNUMBER):
            if self.receive_board.buttons[self.buttonMapping[i][0]] == self.buttonMapping[i][1]:
                self.send_board.LED_buffer[i * 3] = 255
                self.send_board.LED_buffer[i * 3 + 1] = 255
                self.send_board.LED_buffer[i * 3 + 2] = 255
            else:
                self.send_board.LED_buffer[i * 3] = 0
                self.send_board.LED_buffer[i * 3 + 1] = 0
                self.send_board.LED_buffer[i * 3 + 2] = 0

        out_buffer = bytearray(self.send_board)

        for i in range(ENCODERNUMBER):
            self.encoderArray[i] += self.receive_board.encoder_count[i]

        for i in range(LEDARRAYSIZE):
            self.send_board.LED_buffer[i * 3] = self.rgbArray[i].red
            self.send_board.LED_buffer[i * 3 + 1] = self.rgbArray[i].green
            self.send_board.LED_buffer[i * 3 + 2] = self.rgbArray[i].blue


        self.spi.xfer(out_buffer)
    
    def controlBoardReader(self):
        try:
            self.spi_fd = os.open(SPI_DEVICE, os.O_RDWR)
        except FileNotFoundError:
            print("Error: SPI device not found")
            return -1

        try:
            # Configure SPI settings
            self.spi.mode = SPI_MODE
            self.spi.bits_per_word = SPI_BITS_PER_WORD
            self.spi.max_speed_hz = SPI_SPEED_HZ

            # Set up GPIO interrupt for control board events
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(17, GPIO.RISING, callback=self.handle_interrupt, bouncetime=1)

            os.close(self.spi_fd)

        except Exception as e:
            print("An error occurred:", e)

    def __del__(self):
        pass

# Define main function
# def main():
    # app = QApplication(sys.argv)

    # # Create an instance of UI_ControlBoardReader
    # control_board_reader = UI_ControlBoardReader()

    # # Set global send_board variable
    # global send_board
    # send_board = control_board_reader.send_board

    # # Start reading control board
    # control_board_reader.controlBoardReader()

    # sys.exit(app.exec_())

# # Execute main function if the script is run directly
# if __name__ == "__main__":
    # main()
