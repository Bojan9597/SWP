from typing import List, Tuple

class VisualRepresentationAntennaGenius:
    def __init__(self):
        self.infoGetStruct = None  # AG_infoGetStruct object
        self.antennasToShow = []  # List of arrays containing pairs of label text and label style
        self.bandsToShow = ["", ""]  # Array of two strings
        self.outputsToShow = []  # List of arrays containing strings
        self.subRelayStruct = None  # AG_SubRelayStruct object
        self.antennaList = []  # List of AG_AntennaListElementStruct objects
        self.bandList = []  # List of AG_BandListElementStruct objects
        self.outputList = []  # List of AG_OutputListElementStruct objects
        self.groupList = []  # List of AG_GroupListElementStruct objects
        self.portGetStruct1 = None  # AG_PortGetStruct object
        self.portGetStruct2 = None  # AG_PortGetStruct object
