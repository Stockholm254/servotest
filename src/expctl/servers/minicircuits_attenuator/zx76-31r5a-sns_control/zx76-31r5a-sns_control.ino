int CLK = 3;
int DATA = 4;
int LATCH = 5;
int incomingData = 0;
  
void setup() {
  Serial.begin(9600);
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
    digitalWrite(DATA, kth_bit(val, i));
    digitalWrite(CLK, 1);
    digitalWrite(CLK, 0);
  }
  digitalWrite(LATCH, 1);
  digitalWrite(LATCH, 0);
  digitalWrite(DATA, 0);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) 
  {
    incomingData = Serial.parseInt();
    while (Serial.available() > 0) {Serial.read();}
    set_val(incomingData);
    Serial.println(incomingData);
  }
}
