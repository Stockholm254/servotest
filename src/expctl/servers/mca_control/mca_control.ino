int CLK = 4;
int DATA = 13;
int LATCH = 8;
int incomingByte;
 
void setup() {
  Serial.begin(19200);
  Serial.setTimeout(0.5);
  pinMode(CLK, OUTPUT);
  pinMode(DATA, OUTPUT);
  pinMode(LATCH, OUTPUT);
}

int kth_bit(int n, int k) {
  // returns the kth bit of n
  return (n & (1 << k)) >> k;
}

void set_val(int val) {
  // sets the attenuation "val" to the device. 
  // val should be encoded as a bitstring where each bit 
  // corresponds to a data bit to be written
  for (int i = 0; i < 6; i++)
  {
    digitalWrite(DATA, kth_bit(val, 6-i)); // send MSB first
    digitalWrite(CLK, 1);
    digitalWrite(CLK, 0);
  }
  digitalWrite(LATCH, 1);
  digitalWrite(LATCH, 0);
  digitalWrite(DATA, 0);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available())
  {
    incomingByte = Serial.read();
    if (incomingByte!=-1) 
    {
      set_val(incomingByte);
      Serial.write(incomingByte);
    }
  }

}
