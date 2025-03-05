import serial
import time

class ArduinoADC:
    def __init__(self, port, baud_rate=115200, timeout=1):
        self.ser = serial.Serial(port, baud_rate, timeout=timeout)
        time.sleep(2)  # Wait for Arduino to reset

    def read(self, chan):
        if not 1 <= chan <= 6:
            raise ValueError("Channel must be between 1 and 6")
        
        # Send command to Arduino
        self.ser.write(str(chan).encode())
        
        # Read response
        response = self.ser.readline().decode().strip()
        
        try:
            return float(response)
        except ValueError:
            print(f"Invalid response: {response}")
            return None

    def close(self):
        self.ser.close()

# Example usage
if __name__ == "__main__":
    adc = ArduinoADC("COM8")  # Adjust port as necessary
    
    try:
        while True:
            # for chan in range(1, 7):
            #     value = adc.read(chan)
            #     print(f"Channel {chan}: {value}")
            chan=1
            value = adc.read(chan)
            print(f"Channel {chan}: {value}")
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        adc.close()