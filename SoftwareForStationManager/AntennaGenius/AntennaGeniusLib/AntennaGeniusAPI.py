from PyQt5.QtCore import QThread
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from AntennaGenius.AntennaGeniusLib.AntennaGeniusTCPClient import AntennaGeniusTCPClient
from PyQt5.QtCore import QEventLoop
from AntennaGenius.AntennaGeniusLib.VisualRepresentationAntennaGenius import VisualRepresentationAntennaGenius
from AntennaGenius.AntennaGeniusLib.AntennaGeniusStructs import *
from typing import List
import re 
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket


class AntennaGeniusAPI(QObject):
    # Signals
    updateOutputsToShowSignal = pyqtSignal()
    updateAntennasToShowSignal = pyqtSignal()
    visualRepresentationAntennaGeniusMade = pyqtSignal()
    updateBandsToShowSignal = pyqtSignal()
    disconnectedApi = pyqtSignal()

    def __init__(self, ip_address, port, auth_code="", serial_number=""):
        super().__init__()
        self.ip_address = ip_address
        self.port = port
        self.auth_code = auth_code
        self.serial_number = serial_number
        self.client = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.ping)
        

        self.visualRepresentationAntennaGenius = VisualRepresentationAntennaGenius()
        self.client = AntennaGeniusTCPClient(self.ip_address, self.port, self.auth_code, self.serial_number)
        self.client.connected.connect(self.start_ping_timer)
        self.client.disconnected.connect(self.disconnectedApi.emit)
        self.client.errorOccurred.connect(lambda error: print(f"Error: {error}"))
        self.client.statusResponseReceived.connect(self.onStatusResponseReceived)
        self.client.connected.connect(self.run)

    def run(self):
        self.get_antenna_list()
        self.get_band_list()
        self.get_output_list()
        self.get_group_list()
        self.get_port(1)
        self.get_port(2)
        self.subscribe()
        self.get_antennas_to_show()
        self.get_bands_to_show()
        self.visualRepresentationAntennaGeniusMade.emit()

    def start_ping_timer(self):
        print("Connected")
        self.timer.start(5000)

    def ping(self):
        if time.time() - self.client.responseTime > 6:
            self.timer.stop()
            self.client.disconnect()
            
        if self.client.connected_status:
            self.client.send_command("ping")

    def get_antenna_list(self):
        
        loop = QEventLoop()
        seq_number = self.client.send_command("antenna list")
        @pyqtSlot(int, list, int)
        def handle_integer_response(integer_value, response, sucess):
            if integer_value == seq_number:
                antennaList = response
                self.visualRepresentationAntennaGenius.antennaList.clear()
                self.visualRepresentationAntennaGenius.antennaList = self.process_antenna_list(antennaList)
                loop.quit()
        self.client.regularResponseReceived.connect(handle_integer_response)
        loop.exec_()
        self.client.regularResponseReceived.disconnect(handle_integer_response)
    
    def process_antenna_list(self, antennaList):
        antennas = []
        for antenna_info in antennaList:
            if antenna_info == "":
                continue
            info = antenna_info.split()
            antenna_number = int(info[1])
            name = info[2].split('=')[1]
            tx = info[3].split('=')[1]
            rx = info[4].split('=')[1]
            inband = info[5].split('=')[1]
            antenna = AG_AntennaListElementStruct(antenna_number, name, tx, rx, inband)
            antennas.append(antenna)
        return antennas

    def get_band_list(self):
        loop = QEventLoop()
        seq_number = self.client.send_command("band list")
        @pyqtSlot(int, list, int)
        def handle_integer_response(integer_value, response, success):
            if integer_value == seq_number:
                bandList = response
                self.client.regularResponsesDict.pop(str(seq_number))                
                self.visualRepresentationAntennaGenius.bandList.clear()
                self.visualRepresentationAntennaGenius.bandList = self.process_band_list(bandList)
                loop.quit()
        self.client.regularResponseReceived.connect(handle_integer_response)
        loop.exec_()
        self.client.regularResponseReceived.disconnect(handle_integer_response)
    
    def process_band_list(self, bandList):
        bands = []
        for band_info in bandList:
            if band_info == "":
                continue
            info = band_info.split()
            band_number = int(info[1])
            name = info[2].split('=')[1]
            freq_start = float(info[3].split('=')[1])
            freq_stop = float(info[4].split('=')[1])
            band = AG_BandListElementStruct(band_number, name, freq_start, freq_stop)
            bands.append(band)
        return bands
    
    def get_output_list(self):
        loop = QEventLoop()
        seq_number = self.client.send_command("output list")
        @pyqtSlot(int, list, int)
        def handle_integer_response(integer_value, response, success):
            if integer_value == seq_number:
                outputList= response
                self.visualRepresentationAntennaGenius.outputList = self.process_output_list(outputList)
                loop.quit()
        self.client.regularResponseReceived.connect(handle_integer_response)
        loop.exec_()
        self.client.regularResponseReceived.disconnect(handle_integer_response)

    def process_output_list(self, outputList):
        outputs = []
        for output_info in outputList:
            if output_info == "":
                continue
            info = output_info.split()
            outputNumber = int(info[1])
            in_use = int(info[2].split('=')[1])
            group = int(info[3].split('=')[1])
            name = info[4].split('=')[1]
            state = info[5].split('=')[1]
            hotkey = info[6].split('=')[1]
            try:
                hotkey = hotkey
            except ValueError:
                hotkey = 0  # Set a default value or handle the error as needed
            trx = int(info[7].split('=')[1])
            output = AG_OutputListElementStruct(outputNumber, in_use, group, name, state, hotkey, trx)
            outputs.append(output)
        return outputs

    def get_port(self, port_number):
        loop = QEventLoop()
        seq_number = self.client.send_command(f"port get {port_number}")
        @pyqtSlot(int, list, int)
        def handle_integer_response(integer_value, response, success):
            if integer_value == seq_number:
                port_struct= response[0]
                if port_number == 1:
                    self.visualRepresentationAntennaGenius.portGetStruct1 = self.process_port_struct(port_struct)
                if port_number == 2:
                    self.visualRepresentationAntennaGenius.portGetStruct2 = self.process_port_struct(port_struct)
                loop.quit()
        self.client.regularResponseReceived.connect(handle_integer_response)
        loop.exec_()
        self.client.regularResponseReceived.disconnect(handle_integer_response)

    def process_port_struct(self, port_info):
        if port_info == "":
            return AG_PortGetStruct(None, None, None, None, None, None, None, None)
        info = port_info.split()
        port_number = int(info[1])
        port_auto = int(info[2].split('=')[1])
        source = info[3].split('=')[1]
        band = int(info[4].split('=')[1])
        rxant = int(info[5].split('=')[1])
        txant = int(info[6].split('=')[1])
        tx = int(info[7].split('=')[1])
        inhibit = int(info[8].split('=')[1])
        return AG_PortGetStruct(port_number, port_auto, source, band, rxant, txant, tx, inhibit)
    
    def get_group_list(self):
        loop = QEventLoop()
        seq_number = self.client.send_command("group list")
        @pyqtSlot(int, list, int)
        def handle_integer_response(integer_value, response, success):
            if integer_value == seq_number:
                groupList= response
                self.visualRepresentationAntennaGenius.groupList = self.process_group_list(groupList)
                loop.quit()
        self.client.regularResponseReceived.connect(handle_integer_response)
        loop.exec_()
        self.client.regularResponseReceived.disconnect(handle_integer_response)

    def process_group_list(self, outputList):
        groups = []
        for group_info in outputList:
            if group_info == "":
                continue
            info = group_info.split()
            groupNumber = int(info[1])
            in_use = int(info[2].split('=')[1])
            name = info[3].split('=')[1]
            mode = info[4].split('=')[1]
            antennaOrBand = info[5].split('=')[1]
            allow_none = int(info[6].split('=')[1])
            group = AG_GroupListElementStruct(groupNumber, in_use, name, mode, antennaOrBand, allow_none)
            groups.append(group)
        return groups
    
    def get_antennas_to_show(self):
        try:
            self.visualRepresentationAntennaGenius.antennasToShow.clear()

            all_antenna_list = self.visualRepresentationAntennaGenius.antennaList

            if not all_antenna_list:
                return

            port_get_struct1 = self.visualRepresentationAntennaGenius.portGetStruct1
            port_get_struct2 = self.visualRepresentationAntennaGenius.portGetStruct2

            band1 = port_get_struct1.band
            band2 = port_get_struct2.band

            for antenna_list_element in all_antenna_list:
                port_a_result_tx = (int(antenna_list_element.tx, 16) >> band1) & 1 != 0
                port_a_result_rx = (int(antenna_list_element.rx, 16) >> band1) & 1 != 0
                port_b_result_tx = (int(antenna_list_element.tx, 16) >> band2) & 1 != 0
                port_b_result_rx = (int(antenna_list_element.rx, 16) >> band2) & 1 != 0

                port_a_label = ("", "TXnotSet")
                antenna_name_label = (antenna_list_element.name, "antennaNotSelected")
                port_b_label = ("", "TXnotSet")
                selected_antenna_is_transmitting = (antenna_list_element.name, "")

                if port_a_result_tx or port_a_result_rx:
                    if antenna_list_element.antenna_number == port_get_struct1.rxant:
                        antenna_name_label = (antenna_list_element.name, "antennaASelected")

                    if port_a_result_tx:
                        port_a_label = ("A", "TXset")
                        if antenna_name_label[1] == "antennaASelected" and port_a_label[1] == "TXset":
                            selected_antenna_is_transmitting = (antenna_list_element.name, "TXsetAndAntennaSelectedA")
                    else:
                        port_a_label = ("A", "TXnotSet")

                if port_b_result_tx or port_b_result_rx:
                    if antenna_list_element.antenna_number == port_get_struct2.rxant:
                        antenna_name_label = (antenna_list_element.name, "antennaBSelected")

                    if port_b_result_tx:
                        port_b_label = ("B", "TXset")
                        if antenna_name_label[1] == "antennaBSelected" and port_b_label[1] == "TXset":
                            selected_antenna_is_transmitting = (antenna_list_element.name, "TXsetAndAntennaSelectedB")
                    else:
                        port_b_label = ("B", "TXnotSet")

                if port_a_label[0] or port_b_label[0]:
                    label_text_styles = [port_a_label, antenna_name_label, port_b_label, selected_antenna_is_transmitting]
                    self.visualRepresentationAntennaGenius.antennasToShow.append(label_text_styles)

        except IndexError as e:
            print(f"Index out of range while processing antenna list: {e}")
            return
        except Exception as e:
            print(f"Error occurred while processing antennas: {e}")
            return

    def get_outputs_to_show(self):
        try:
            self.visualRepresentationAntennaGenius.outputsToShow.clear()

            group_list_element_struct = self.visualRepresentationAntennaGenius.groupList
            if not group_list_element_struct:
                return

            output_list_element_struct = self.visualRepresentationAntennaGenius.outputList
            port_get_struct1 = self.visualRepresentationAntennaGenius.portGetStruct1
            port_get_struct2 = self.visualRepresentationAntennaGenius.portGetStruct2

            band1 = port_get_struct1.band
            band2 = port_get_struct2.band
            selected_antenna1 = port_get_struct1.rxant
            selected_antenna2 = port_get_struct2.rxant

            for group_list_element in group_list_element_struct:
                if group_list_element.mode == "BAND":
                    result_port1 = (int(group_list_element.antennaOrBand, 16) >> band1) & 1 != 0
                    result_port2 = (int(group_list_element.antennaOrBand, 16) >> band2) & 1 != 0

                    if result_port1 or result_port2:
                        for output_list_element in output_list_element_struct:
                            if output_list_element.group == group_list_element.groupNumber:
                                if (int(self.visualRepresentationAntennaGenius.subRelayStruct.rx, 16) >> (output_list_element.outputNumber -1)) & 1 != 0:
                                    self.visualRepresentationAntennaGenius.outputsToShow.append(
                                        [str(output_list_element.group),
                                        output_list_element.name,
                                        str(output_list_element.outputNumber), "green"])
                                else:
                                    self.visualRepresentationAntennaGenius.outputsToShow.append(
                                        [str(output_list_element.group),
                                        output_list_element.name,
                                        str(output_list_element.outputNumber), "default"])
                elif group_list_element.mode == "ANT":
                    if group_list_element.antennaOrBand in [str(selected_antenna1), str(selected_antenna2)]:
                        for output_list_element in output_list_element_struct:
                            if output_list_element.group == group_list_element.groupNumber:
                                if (int(self.visualRepresentationAntennaGenius.subRelayStruct.rx, 16) >> (output_list_element.outputNumber - 1)) & 1 != 0:
                                    self.visualRepresentationAntennaGenius.outputsToShow.append(
                                        [str(output_list_element.group),
                                        output_list_element.name, "", "green"])
                                else:
                                    self.visualRepresentationAntennaGenius.outputsToShow.append(
                                        [str(output_list_element.group),
                                        output_list_element.name, "", "default"])

        except IndexError as e:
            print(f"Index out of range while processing output list: {e}")
            return
        except Exception as e:
            print(f"Error occurred while processing outputs: {e}")
            return

        
    def get_bands_to_show(self):
        try:
            bands_to_show = ["", ""]  # Array of two strings
            band_list = self.visualRepresentationAntennaGenius.bandList
            bands_to_show[0] = band_list[self.visualRepresentationAntennaGenius.portGetStruct1.band].name
            bands_to_show[1] = band_list[self.visualRepresentationAntennaGenius.portGetStruct2.band].name
            self.visualRepresentationAntennaGenius.bandsToShow = bands_to_show

        except Exception as e:
            print(f"Error occurred while getting bands to show: {e}")
            return ["", ""]

    def sub_relay(self):
        self.client.send_command("sub relay")

    def sub_port_all(self):
        self.client.send_command("sub port all")

    def sub_output(self):
        self.client.send_command("sub output")

    def subscribe(self):
        self.sub_relay()
        self.sub_port_all()
        self.sub_output()

    def process_sub_relay(self, response):
        # Split the response string by whitespace
        parts = response.split()

        # Extract values of tx, rx, and state
        tx_value = parts[1].split('=')[1]
        rx_value = parts[2].split('=')[1]
        state_value = parts[3].split('=')[1]

        # Create an instance of AG_SubRelayStruct with extracted values
        sub_relay_struct = AG_SubRelayStruct(tx_value, rx_value, state_value)
        return sub_relay_struct
    
    def process_sub_port(self, response):
        if response == "":
            return AG_PortGetStruct(None, None, None, None, None, None, None, None)
        info = response.split()
        port_number = int(info[1])
        port_auto = int(info[2].split('=')[1])
        source = info[3].split('=')[1]
        band = int(info[4].split('=')[1])
        rxant = int(info[5].split('=')[1])
        txant = int(info[6].split('=')[1])
        tx = int(info[7].split('=')[1])
        inhibit = int(info[8].split('=')[1])
        
        return AG_PortGetStruct(port_number, port_auto, source, band, rxant, txant, tx, inhibit)
        
    def stop(self):
        if self.client:
            self.client.disconnect()

    
    @pyqtSlot(str)
    def onStatusResponseReceived(self, response):
        if "relay" in response:
            start_time = time.time()
            self.visualRepresentationAntennaGenius.subRelayStruct = self.process_sub_relay(response)
            self.get_outputs_to_show()
            self.updateOutputsToShowSignal.emit()
            print("Time to process sub_relay:", time.time() - start_time)

        if "port" in response:
            portGetStruct = self.process_sub_port(response)
            if portGetStruct.port_number == 1:
                self.visualRepresentationAntennaGenius.portGetStruct1 = portGetStruct
            elif portGetStruct.port_number == 2:
                self.visualRepresentationAntennaGenius.portGetStruct2 = portGetStruct
            self.get_outputs_to_show()
            self.get_antennas_to_show()
            self.get_bands_to_show()
            self.updateAntennasToShowSignal.emit()
            self.updateBandsToShowSignal.emit()
        if "output reload" in response:
            self.get_outputs_to_show()
            self.get_group_list()
            self.updateOutputsToShowSignal.emit()
            self.updateAntennasToShowSignal.emit()
            self.updateBandsToShowSignal.emit()