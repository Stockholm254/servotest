import os
import logging

# Configuration of device IP adresses for the different servers is very sensitive.
# Once you're on the same network, launching frontpanel on a machine allows aceess to the actual experiment hardware and you _can damage the machine_!!!
# Therefore this file checks if an environment variable is present on the machine and loads the appropriate config file accordingly.
# This is a safety feature, so never create the "prop" (production) env variable on any machine other than the actual experiment computer.

config = os.getenv('FRONTPANEL_CONFIG', None)

if config=='prod':
    from .prod import *
else:
    print("No machine configuration found, defaulting to development configuration.")
    from .dev import *