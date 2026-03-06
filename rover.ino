#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "new";        // Your WiFi name
const char* password = ""; // Your WiFi password

ESP8266WebServer server(80);
int GREEN_LED = 5;  // D1 (GPIO5)
int RED_LED = 4;    // D2 (GPIO4)

void setup() {
  Serial.begin(115200);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());  // Copy this IP to Streamlit code

  // HTTP endpoints for Streamlit to call
  server.on("/green", []() {
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    server.send(200, "text/plain", "🟢 GREEN LED ON");
  });

  server.on("/red", []() {
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    server.send(200, "text/plain", "🔴 RED LED ON");
  });

  server.begin();
  Serial.println("HTTP server ready!");
}

void loop() {
  server.handleClient();
}
