import serial
import time
import RPi.GPIO as GPIO

def nmea_to_decimal(nmea_val: str, direction: str, is_lon: bool = False) -> float:
    """
    Converte o formato NMEA (DDMM.MMMMM para Lat, DDDMM.MMMMM para Lon) 
    para Graus Decimais (float).
    """
    if not nmea_val:
        return 0.0
    
    # A longitude tem 3 dígitos de graus iniciais, a latitude tem 2
    graus_len = 3 if is_lon else 2
    
    graus = float(nmea_val[:graus_len])
    minutos = float(nmea_val[graus_len:])
    
    decimal = graus + (minutos / 60.0)
    
    # Sul (S) e Oeste (W) são coordenadas negativas
    if direction in ['S', 'W']:
        decimal *= -1.0
        
    return round(decimal, 6)

def get_gps_position(config: dict) -> tuple[float, float]:
    """
    Lê a posição GPS bruta via NMEA (sentença $GPGGA), converte para decimal
    e aciona um pino GPIO pelo tempo configurado.
    """
    port = config.get('port', '/dev/serial0')
    baud = config.get('baud', 9600)
    gpio_pin_out = config.get("gpio_pin_out", 18)
    bip_ms = config.get("bip_ms", 500)

    lat, lon = 0.0, 0.0

    # Configuração do GPIO
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin_out, GPIO.OUT)

    try:
        with serial.Serial(port, baud, timeout=2) as ser:
            ser.reset_input_buffer()
            
            # Laço de leitura inspirado no seu script funcional
            for _ in range(30): # Tenta ler por até ~3 segundos
                if ser.in_waiting > 0:
                    linha = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if linha and linha.startswith('$GPGGA'):
                        partes = linha.split(',')
                        
                        # Garante que a linha tem os campos necessários
                        if len(partes) > 6:
                            qualidade_sinal = partes[6]
                            
                            # '0' = sem sinal, '1' ou '2' = sinal fixado
                            if qualidade_sinal != '0' and partes[2] and partes[4]:
                                # Converte as strings NMEA para float decimal
                                lat = nmea_to_decimal(partes[2], partes[3], is_lon=False)
                                lon = nmea_to_decimal(partes[4], partes[5], is_lon=True)
                                break # Achou coordenada válida, sai do laço!
                
                time.sleep(0.1)

        # Dispara o acionamento do GPIO independente se achou sinal ou não
        GPIO.output(gpio_pin_out, GPIO.HIGH)
        time.sleep(bip_ms / 1000.0)
        GPIO.output(gpio_pin_out, GPIO.LOW)

    except serial.SerialException as e:
        print(f"[Erro GPS] Erro na porta {port}: {e}")
    except Exception as e:
        print(f"[Erro GPS] Erro inesperado: {e}")
    
    return lat, lon

# ==========================================
# Exemplo de uso local para teste rápido:
# ==========================================
if __name__ == "__main__":
    configuracao = {
        "port": "/dev/serial0",
        "baud": 9600,
        "gpio_pin_out": 18,
        "bip_ms": 200 
    }
    
    latitude, longitude = get_gps_position(configuracao)
    if latitude != 0.0:
        print(f"Posição Decimal - Lat: {latitude} | Lon: {longitude}")
    else:
        print("Aguardando precisão dos satélites ou tempo limite excedido.")
