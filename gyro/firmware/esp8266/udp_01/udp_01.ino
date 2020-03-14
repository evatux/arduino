/*
  UDPSendReceive.pde:
  This sketch receives UDP message strings, prints them to the serial port
  and sends an "acknowledge" string back to the sender

  A Processing sketch is included at the end of file that can be used to send
  and received messages for testing with a computer.

  created 21 Aug 2010
  by Michael Margolis

  This code is in the public domain.

  adapted from Ethernet library examples
*/


#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#include "pass.inc"

const unsigned int TICKS_THRESHOLD = 800;
const unsigned int localPort = 8888;

IPAddress remoteAddr(1, 1, 1, 1);
unsigned int remotePort = 0;

unsigned int ticks;

WiFiUDP Udp;

void setup() {
  Serial.begin(9600);
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

  Serial.printf("Now listening at IP %s, UDP port %d\n", WiFi.localIP().toString().c_str(), localPort);
}

void loop() {
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
      Serial.printf("UDP packet contents: %s\n", incomingPacket);
    }

    remoteAddr = Udp.remoteIP();
    remotePort = Udp.remotePort();
    ticks = 0;
  }

  Udp.beginPacket(remoteAddr, remotePort);
  Udp.printf("hi %u\n", ticks);
  int x = Udp.endPacket();
  Serial.printf("Packet sent status: %d (remote port:%d)\n", x, remotePort);

  delay(10);
  if (ticks < TICKS_THRESHOLD) ticks += 10;
}

/*
  test (shell/netcat):
  --------------------
	  nc -u 192.168.esp.address 8888
*/
