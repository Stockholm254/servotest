from .kinesis_server import KinesisServer

if __name__ == '__main__':

	message = """
	===========================================
	==        Kinesis Waveplate Server       ==
	==                Lambda / 4             ==
	==              SN 27501302              ==
	===========================================
	"""
	server = KinesisServer("Kinesis4", 60642, message=message, serial_number='27501302')
	server.main_loop()