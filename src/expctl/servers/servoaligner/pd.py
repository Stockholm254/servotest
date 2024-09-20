from smbus2 import SMBus,i2c_msg
import MCP342x
i2cbus = SMBus(1)
MCP3424_fiber=MCP342x.MCP342x(i2cbus, 0x68, device='MCP3424', channel=0, gain=1, resolution=16, continuous_mode=False, scale_factor=1.0, offset=0.0)
MCP3424_pinhole=MCP342x.MCP342x(i2cbus, 0x68, device='MCP3424', channel=1, gain=1, resolution=16, continuous_mode=False, scale_factor=1.0, offset=0.0)
MCP3424_ref=MCP342x.MCP342x(i2cbus, 0x68, device='MCP3424', channel=2, gain=4, resolution=16, continuous_mode=False, scale_factor=1.0, offset=0.0)
print(MCP3424_fiber.convert_and_read())

