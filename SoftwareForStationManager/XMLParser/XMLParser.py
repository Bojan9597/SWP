import xml.etree.ElementTree as ET
from XMLParser.XMLClasses import *

class XMLParser:
    def __init__(self, path_to_xml):
        try:
            self.tree = ET.parse(path_to_xml)
            self.root = self.tree.getroot()
        except FileNotFoundError:
            print("Error: XML file not found.")
            return

        self.station_manager_list = []
        self.process_antenna_genius()

    def process_antenna_genius(self):
        for antenna_genius_elem in self.root.findall('antennaGenius'):
            ip = antenna_genius_elem.get('ip')
            password = antenna_genius_elem.get('password')
            serial_number = antenna_genius_elem.get('serialNumber')
            port = antenna_genius_elem.get('port')
            positionX = antenna_genius_elem.get('positionX')
            positionY = antenna_genius_elem.get('positionY')

            antenna_genius = XML_AntennaGenius(ip, password, serial_number, port, positionX, positionY)

            for button_elem in antenna_genius_elem.findall('buttons/button'):
                button_number = button_elem.get('buttonNumber')
                button_command = button_elem.text.strip()  # Get the text content of the button element
                antenna_genius.buttons.append((button_number, button_command))
            
            self.station_manager_list.append(antenna_genius)

        if self.station_manager_list:
            print("XML parsed successfully.")
        else:
            print("Error: No antenna genius data found in the XML file.")
