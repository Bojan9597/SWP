import spidev
import gpiod
import time
import os
import sys
import fcntl
import ctypes
from PyQt5.QtCore import QObject, pyqtSignal
from AntennaGenius.QAntennaGenius.QAntennaGeniusWidget import QAntennaGeniusWidget
from XMLParser.XMLClasses import XML_AntennaGenius
# from UI_ControlBoardReader import UI_ControlBoardReader
from QSSFileHelper import QSSFileHelper
from PyQt5.QtWidgets import QMainWindow, QFrame, QGridLayout
from PyQt5.QtCore import pyqtSlot
from XMLParser.XMLParser import *

BUTTONNUMBER = 33

class QStationManager(QMainWindow):
    def __init__(self, parent, xml_base_classes=None):
        super().__init__(parent)
        self.xml_base_classes = xml_base_classes
        # self.ui_ControlBoardReader = UI_ControlBoardReader()
        # self.ui_ControlBoardReader.controlBoardSignal.connect(self.handleButtonPress)
        # self.ui_ControlBoardReader.controlBoardReader()
        self.antenna_genius_widgets = []

        self.container = None
        self.grid_layout = None
        self.buttonEventHandlers = [ButtonEventHandler() for _ in range(BUTTONNUMBER)]

        self.initialize_station_manager()
        self.update_grid_layout_based_on_xml_file()
        # self.ui_ControlBoardReader.hi()
    
    # i need destructor
    def __del__(self):
        pass

    def initialize_station_manager(self):
        self.container = QFrame()
        qss_file_helper = QSSFileHelper("qssFiles/QStationManagerStyles.qss")
        q_station_manager_container_properties = qss_file_helper.extract_style_properties("QFrame#Container.default")
        self.container.setStyleSheet(q_station_manager_container_properties)
        self.grid_layout = QGridLayout(self.container)
        self.setCentralWidget(self.container)
        self.setFixedSize(800, 480)

    def update_grid_layout_based_on_xml_file(self):
        try:
            for xml_base_class in self.xml_base_classes:
                if isinstance(xml_base_class, XML_AntennaGenius):
                    antenna_genius_data = xml_base_class
                    q_antenna_genius_widget = QAntennaGeniusWidget(self.container, antenna_genius_data)

                    for button_id, command in antenna_genius_data.buttons:
                        print("Button ID:", button_id, "Button command:", command)
                        button_id = int(button_id)
                        self.buttonEventHandlers[button_id].buttonID = button_id
                        self.buttonEventHandlers[button_id].command = command
                        self.buttonEventHandlers[button_id].qwSender = q_antenna_genius_widget

                    self.antenna_genius_widgets.append(q_antenna_genius_widget)
                    self.grid_layout.addWidget(q_antenna_genius_widget, antenna_genius_data.position[0], antenna_genius_data.position[1])
                else:
                    print("Failed to process XML_AntennaGeniusDataClass")

        except Exception as e:
            print("Error in QStationManager constructor:", e)

        self.container.move(500, 10)

    @pyqtSlot(int)
    def handleButtonPress(self, buttonID):
        if 0 <= buttonID < len(self.buttonEventHandlers):
            buttonEventHandler = self.buttonEventHandlers[buttonID]
            print("Button", buttonID, "pressed")
            print("Command:", buttonEventHandler.command)
            print("Callback executed")
            if buttonEventHandler.qwSender is not None:
                buttonEventHandler.qwSender.client_thread.client.send_command(buttonEventHandler.command)

class ButtonEventHandler:
    def __init__(self):
        self.buttonID = 999
        self.command = ""
        self.qwSender = None
