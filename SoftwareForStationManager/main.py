from PyQt5.QtWidgets import QApplication
from QStationManager import QStationManager  # Assuming you have a separate file defining QStationManager class
from XMLParser.XMLParser import XMLParser
import sys

def main():
    app = QApplication(sys.argv)

    q_station_manager = QStationManager(None)  # Pass None as parent for the main window
    q_station_manager.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
