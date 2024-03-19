from PyQt5.QtWidgets import QApplication
from QStationManager import QStationManager  # Assuming you have a separate file defining QStationManager class
from XMLParser.XMLParser import XMLParser
import sys
XML_PATH = "xmlExample.xml"

def main():
    app = QApplication(sys.argv)
    xml_base_classes = XMLParser(XML_PATH).station_manager_list
    q_station_manager = QStationManager(None, xml_base_classes)  # Pass None as parent for the main window
    q_station_manager.showFullScreen()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
