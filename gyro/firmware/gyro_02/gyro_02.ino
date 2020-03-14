#include <Wire.h>

#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define DEBUG 0
#if DEBUG
#define SERIAL_PRINTF(...) Serial.printf(__VA_ARGS__)
#else
#define SERIAL_PRINTF(...)
#endif

// ========================================
// WiFi settings

#include "pass.inc"

const unsigned int TICKS_THRESHOLD = 800;
const unsigned int localPort = 8888;

IPAddress remoteAddr(1, 1, 1, 1);
unsigned int remotePort = 0;

unsigned int ticks;

WiFiUDP Udp;

// ========================================
// Sensor settings

const uint8_t MPU = 0x68;

// ========================================
// Setup

void setup_sensor(){
    // nodeMCU: SDA/SCL pins: D2/D1
    // nano: SDA/SCL pins: A4/A5
#ifdef ARDUINO_ARCH_ESP8266
    Wire.begin(4, 5);
#else
    Wire.begin();
#endif
    Wire.beginTransmission(MPU);
    Wire.write(0x6B);
    Wire.write(0);
    Wire.endTransmission(true);
}

void setup_wifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(STASSID, STAPSK);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(500);
  }
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());
  Serial.printf("UDP server on port %d\n", localPort);
  Udp.begin(localPort);

  Serial.printf("Now listening at IP %s, UDP port %d\n",
      WiFi.localIP().toString().c_str(), localPort);
}

void setup() {
  Serial.begin(9600);
  setup_sensor();
  setup_wifi();
}

// ========================================
// Loop

void loop_sensor(int &AcX, int &AcY, int &AcZ) {
    Wire.beginTransmission(MPU);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, (size_t)14, true);

    //read accel data
    AcX = (int16_t)(Wire.read()<<8|Wire.read());
    AcY = (int16_t)(Wire.read()<<8|Wire.read());
    AcZ = (int16_t)(Wire.read()<<8|Wire.read());
}

void loop_wifi(int AcX, int AcY, int AcZ) {
  if (remotePort == 0 || ticks >= TICKS_THRESHOLD) {
    const bool try_another_connection = remotePort != 0;

    // check if no new connections available
    if (!Udp.parsePacket()) {
      if (try_another_connection)
        ticks = 0;
      return;
    }

    char incomingPacket[255];
    int len = Udp.read(incomingPacket, sizeof(incomingPacket) - 1);
    if (len > 0) {
      incomingPacket[len] = 0;
      SERIAL_PRINTF("@@@ UDP packet contents: %s\n", incomingPacket);
    }

    remoteAddr = Udp.remoteIP();
    remotePort = Udp.remotePort();
    ticks = 0;
  }

  Udp.beginPacket(remoteAddr, remotePort);
  Udp.printf("%d %d %d\n", AcX, AcY, AcZ);
  SERIAL_PRINTF("%d %d %d\n", AcX, AcY, AcZ);
  Udp.endPacket();

  const int delay_time = 10;
  delay(delay_time);
  if (ticks < TICKS_THRESHOLD) ticks += delay_time;
}

void loop() {
  int AcX{}, AcY{}, AcZ{};
  loop_sensor(AcX, AcY, AcZ);
  loop_wifi(AcX, AcY, AcZ);
}
