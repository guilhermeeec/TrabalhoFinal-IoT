#include <TinyGPS++.h>
#include <SoftwareSerial.h>

// O Uno tem apenas uma porta serial de hardware (pinos 0 e 1).
// Usaremos o SoftwareSerial para ler o GPS.
static const int RXPin = 4, TXPin = 3;
static const uint32_t GPSBaud = 9600;

TinyGPSPlus gps;
SoftwareSerial gpsSerial(RXPin, TXPin);

unsigned long ultimoEnvio = 0;
const unsigned long INTERVALO_ENVIO = 1000; // 1 segundo para maior granularidade

void setup() {
  // Inicializa a Serial de hardware (Pinos 0 = RX, 1 = TX) para enviar ao Raspberry Pi
  Serial.begin(9600); 
  
  // Inicializa a Serial de software para comunicar com o GPS
  gpsSerial.begin(GPSBaud);
}

void loop() {
  // Alimenta a biblioteca com os dados NMEA crus vindos do SoftwareSerial
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Dispara a cada 1 segundo
  if (millis() - ultimoEnvio > INTERVALO_ENVIO) {
    ultimoEnvio = millis();

    // Só envia o pacote se tiver localização válida
    if (gps.location.isValid()) {
      
      // LATITUDE E LONGITUDE separadas por vírgula
      Serial.print(gps.location.lat(), 6); 
      Serial.print(",");
      Serial.println(gps.location.lng(), 6);
      
    } else {
      Serial.println("Aguardando sinal dos satelites...");
    }
  }
}