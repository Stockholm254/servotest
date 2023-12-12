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


	# 1 device unit ~ 1.875 arcsec ~ 0.0005 degrees ?