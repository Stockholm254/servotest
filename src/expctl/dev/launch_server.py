import sys
from ..servers.ServerClass import Server

if __name__ == '__main__':
	if len(sys.argv)>1:
		port = int(sys.argv[1])
	else:
		port = 50001

	message = """===========================================
	==       Dummy Digital Output Server     ==
	==              for PCIe 6537            ==
	=========================================== 
	"""
	server = Server(f"Server {port}", port, message)
	server.main_loop()