from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QWidget
from AntennaGenius.AntennaGeniusLib.AntennaGeniusAPI import AntennaGeniusAPI
from AntennaGenius.QAntennaGenius.AntennaListWidget import AntennaListWidget
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QListWidgetItem
from QSSFileHelper import QSSFileHelper

class QAntennaGeniusWidget(QWidget):
    def __init__(self, parent=None, antenna_genius_data=None):
        super().__init__(parent)
        self.main_layout = None
        self.first_vertical_layout = None
        self.second_vertical_layout = None
        self.left_list_widget = None
        self.client_thread = None
        self.antenna_list = []

        self._antenna_genius_data = antenna_genius_data
        self.setup_ui_not_connected()

        self.client_thread = AntennaGeniusAPI(antenna_genius_data.ip, antenna_genius_data.port, antenna_genius_data.password, antenna_genius_data.serial_number)
        self.client_thread.visualRepresentationAntennaGeniusMade.connect(self.updateVisualisation)
        self.client_thread.disconnectedApi.connect(self.setup_ui_not_connected)
        self.client_thread.updateOutputsToShowSignal.connect(self.updateOutputsToShow)
        self.client_thread.updateAntennasToShowSignal.connect(self.updateAntennasToShow)
        self.client_thread.updateBandsToShowSignal.connect(self.updateBandsToShow)
        # self.client_thread.run()

    # define destructor
    def __del__(self):
        self.client_thread.client.timer = None
        self.client_thread.client.socket = None
        self.client_thread.client.disconnect()
        self.client_thread.stop()

    def setup_ui_not_connected(self):
        self.emptyMainLayout()
        if self.main_layout is None:
            self.main_layout = QHBoxLayout()
        self.label = QLabel("Not Connected")
        self.main_layout.addWidget(self.label)
        self.setLayout(self.main_layout)

    def setup_ui_connected(self):
        self.emptyMainLayout()
        
        if self.main_layout is None:
            self.main_layout = QHBoxLayout()

        self.first_vertical_layout = QVBoxLayout()
        self.first_row_layout = QHBoxLayout()  # Use QHBoxLayout for the first row layout
        self.band_label_1 = QLabel("")
        self.band_label_2 = QLabel("")
        self.left_list_widget = QListWidget()

        # Apply style sheet to left list widget
        qss_file_helper = QSSFileHelper("qssFiles/listWidgetStyles.qss")
        list_widget_properties = qss_file_helper.extract_style_properties("QListWidget#item")
        self.left_list_widget.setStyleSheet(list_widget_properties)

        self.second_vertical_layout = QVBoxLayout()
        self.group_of_outputs_label = QLabel("Groups Of Outputs")

        # Apply style sheet to group of outputs label
        qss_file_helper_groups_of_output_labels = QSSFileHelper("qssFiles/BandLabelStyles.qss")
        qss_file_helper_groups_of_output_labels_properties = qss_file_helper_groups_of_output_labels.extract_style_properties("QLabel#Band.default")
        self.group_of_outputs_label.setStyleSheet(qss_file_helper_groups_of_output_labels_properties)

        self.right_list_widget = QListWidget()

        # Apply style sheet to right list widget
        self.right_list_widget.setStyleSheet(list_widget_properties)

        # Add widgets to layouts
        self.first_row_layout.addWidget(self.band_label_1)
        self.first_row_layout.addWidget(self.band_label_2)
        self.first_vertical_layout.addLayout(self.first_row_layout)
        self.first_vertical_layout.addWidget(self.left_list_widget)

        self.second_vertical_layout.addWidget(self.group_of_outputs_label)
        self.second_vertical_layout.addWidget(self.right_list_widget)

        self.main_layout.addLayout(self.first_vertical_layout)
        self.main_layout.addLayout(self.second_vertical_layout)

        self.setLayout(self.main_layout)



    def addOutputToListWidget(self, groupName, outputName, style):
        try:
            text = "Group: " + groupName + "->" + outputName

            listWidgetItem = QListWidgetItem(self.right_list_widget)
            labelItem = QLabel(text)

            qss_file_helper = QSSFileHelper("qssFiles/AntennaListWidgetOutputStyles.qss")
            qlistWidgetItemProperties = qss_file_helper.extract_style_properties("QListWidgetItem#Item." + style)

            labelItem.setStyleSheet(qlistWidgetItemProperties)
            listWidgetItem.setSizeHint(labelItem.sizeHint())

            self.right_list_widget.setItemWidget(listWidgetItem, labelItem)

        except Exception as e:
            print("Exception in addOutputToListWidget:", str(e))

    @pyqtSlot()
    def updateOutputsToShow(self):
        try:
            self.right_list_widget.clear()
            if not self.client_thread.visualRepresentationAntennaGenius.outputsToShow:
                return
            for outputToShow in self.client_thread.visualRepresentationAntennaGenius.outputsToShow:
                self.addOutputToListWidget( outputToShow[0], outputToShow[1], outputToShow[3])
        except Exception as e:
            print("Exception in updateOutputsToShow:", str(e))

    @pyqtSlot()
    def updateAntennasToShow(self):
        try:
            if self.left_list_widget is not None:
                self.left_list_widget.clear()
            if not self.client_thread.visualRepresentationAntennaGenius.antennasToShow:
                return
            for antennaToShow in self.client_thread.visualRepresentationAntennaGenius.antennasToShow:
                self.addAntennaListWidgetElement(antennaToShow)
        except Exception as e:
            print("Exception in updateAntennasToShow:", str(e))

    def addAntennaListWidgetElement(self, labelTextStyles):
        try:
            customItem = AntennaListWidget(labelTextStyles)
            listWidgetItem = QListWidgetItem(self.left_list_widget)
            listWidgetItem.setSizeHint(customItem.sizeHint())
            self.left_list_widget.setItemWidget(listWidgetItem, customItem)
        except Exception as e:
            print("Exception in addAntennaListWidgetElement:", str(e))

    @pyqtSlot()
    def updateBandsToShow(self):
        try:
            qss_file_helper = QSSFileHelper("qssFiles/BandLabelStyles.qss")
            band_label_properties = qss_file_helper.extract_style_properties("QLabel#Band.default")

            self.band_label_1.setText("Band: " + self.client_thread.visualRepresentationAntennaGenius.bandsToShow[0])
            self.band_label_2.setText("Band: " + self.client_thread.visualRepresentationAntennaGenius.bandsToShow[1])

            self.band_label_1.setStyleSheet(band_label_properties)
            self.band_label_2.setStyleSheet(band_label_properties)
        except Exception as e:
            print("Exception in updateBandsToShow:", str(e))

    @pyqtSlot()
    def updateAntennaGeniusWidgetWhenConnected(self):
        pass

    @pyqtSlot()
    def updateAntennaGeniusWidgetWhenNotConnected(self):
        pass

    @pyqtSlot()
    def updateAntennaGeniusWidget(self):
        pass

    def emptyMainLayout(self):
        pass

    def emptyMainLayout(self):
        if self.main_layout is not None:
            while self.main_layout.count():
                item = self.main_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sublayout = item.layout()
                    if sublayout is not None:
                        self.emptyMainLayout()

    @pyqtSlot()
    def updateVisualisation(self):
        self.setup_ui_connected()
        self.updateAntennasToShow()
        self.updateBandsToShow()
        self.updateOutputsToShow()