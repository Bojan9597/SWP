from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from QSSFileHelper import QSSFileHelper  
import os
class AntennaListWidget(QWidget):
    def __init__(self, labelTextStyles):
        super().__init__()
        self.layout = QHBoxLayout()
        self.fill_labels(labelTextStyles)
        self.setLayout(self.layout)

    def fill_labels(self, labelTextStyles):
        portAText, antennaName, portBText, isTransmittingAndSelected = labelTextStyles
        portAStyle = ""
        portBStyle = ""

        portALabel = QLabel(portAText[0])
        antennaLabel = QLabel(antennaName[0])
        portBLabel = QLabel(portBText[0])

        if isTransmittingAndSelected == "TXsetAndAntennaSelectedA":
            portAStyle = "TXsetAndAntennaSelected"
        else:
            portAStyle = labelTextStyles[0][1]

        antennaStyle = labelTextStyles[1][1]

        if isTransmittingAndSelected == "TXsetAndAntennaSelectedB":
            portBStyle = "TXsetAndAntennaSelected"
        else:
            portBStyle = labelTextStyles[2][1]
        os1 = (os.getcwd()) 
        qss_file_helper = QSSFileHelper("qssFiles/AntennaListWIdgetStyles.qss")

        antennaProperties = qss_file_helper.extract_style_properties(f"QLabel#AntennaLabel.{antennaStyle}")
        portAProperties = qss_file_helper.extract_style_properties(f"QLabel#PortLabel.{portAStyle}")
        portBProperties = qss_file_helper.extract_style_properties(f"QLabel#PortLabel.{portBStyle}")

        portALabel.setStyleSheet(portAProperties)
        antennaLabel.setStyleSheet(antennaProperties)
        portBLabel.setStyleSheet(portBProperties)

        self.layout.addWidget(portALabel)
        self.layout.addWidget(antennaLabel)
        self.layout.addWidget(portBLabel)