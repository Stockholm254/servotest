from .kinesis_server import KinesisServer

if __name__ == '__main__':

	message = """
	===========================================
	==        Kinesis Waveplate Server       ==
	==                Lambda / 2             ==
	==              SN 27501301              ==
	===========================================
	"""
	server = KinesisServer("Kinesis2", 60641, message=message, serial_number="27501301")
	server.main_loop()