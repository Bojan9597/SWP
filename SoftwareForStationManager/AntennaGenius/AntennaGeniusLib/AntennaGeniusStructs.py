class AG_infoGetStruct:
    def __init__(self, version, date, btl, hw, serial, name, ports, antennas, mode, uptime):
        self.version = version
        self.date = date
        self.btl = btl
        self.hw = hw
        self.serial = serial
        self.name = name
        self.ports = ports
        self.antennas = antennas
        self.mode = mode
        self.uptime = uptime

class AG_AntennaListElementStruct:
    def __init__(self, antenna_number, name, tx, rx, inband):
        self.antenna_number = antenna_number
        self.name = name
        self.tx = tx
        self.rx = rx
        self.inband = inband

class AG_BandListElementStruct:
    def __init__(self, band_number, name, freq_start, freq_stop):
        self.band_number = band_number
        self.name = name
        self.freq_start = freq_start
        self.freq_stop = freq_stop

class AG_confGetStruct:
    def __init__(self, name, inband_port):
        self.name = name
        self.inband_port = inband_port

class AG_networkGetStruct:
    def __init__(self, dhcp, address, netmask, gateway, auth):
        self.dhcp = dhcp
        self.address = address
        self.netmask = netmask
        self.gateway = gateway
        self.auth = auth

class AG_OutputListElementStruct:
    def __init__(self, outputNumber, in_use, group, name, state, hotkey, trx):
        self.outputNumber = outputNumber
        self.in_use = in_use
        self.group = group
        self.name = name
        self.state = state
        self.hotkey = hotkey
        self.trx = trx

class AG_FlexGetStruct:
    def __init__(self, flex, serial, ant, ptt):
        self.flex = flex
        self.serial = serial
        self.ant = ant
        self.ptt = ptt

class AG_StackGetStruct:
    def __init__(self, stack_in_use, serial, ports):
        self.stack_in_use = stack_in_use
        self.serial = serial
        self.ports = ports

class AG_SubRelayStruct:
    def __init__(self, tx, rx, state):
        self.tx = tx
        self.rx = rx
        self.state = state

class AG_GroupListElementStruct:
    def __init__(self, groupNumber, in_use, name, mode, antennaOrBand, allow_none):
        self.groupNumber = groupNumber
        self.in_use = in_use
        self.name = name
        self.mode = mode
        self.antennaOrBand = antennaOrBand
        self.allow_none = allow_none

class AG_PortGetStruct:
    def __init__(self, port_number, port_auto, source, band, rxant, txant, tx, inhibit):
        self.port_number = port_number
        self.port_auto = port_auto
        self.source = source
        self.band = band
        self.rxant = rxant
        self.txant = txant
        self.tx = tx
        self.inhibit = inhibit

class AG_FlexListElementStruct:
    def __init__(self, flex_model, serial, nickname, callsign):
        self.flex_model = flex_model
        self.serial = serial
        self.nickname = nickname
        self.callsign = callsign

class AG_StackListElementStruct:
    def __init__(self, stack_serial, name, antennas, ports):
        self.stack_serial = stack_serial
        self.name = name
        self.antennas = antennas
        self.ports = ports
