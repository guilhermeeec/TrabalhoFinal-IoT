import serial
import time
import RPi.GPIO as GPIO

def get_gps_position(config:dict)->tuple[float, float]:
    if not config["real_gps"]:
        return -22.9068, -43.1729
    
    port = config.get('port', '/dev/serial0')
    baud = config.get('baud', 9600)
    gpio_pin_out = config.get("gpio_pin_out", 18)
    bip_ms = config.get("bip_ms", 500)

    lat, lon = 0.0, 0.0

    # Configuração do GPIO do Raspberry Pi
    # Usamos BCM para nos referirmos ao número GPIO real (ex: GPIO 18) e não ao pino físico
    GPIO.setwarnings(False) 
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin_out, GPIO.OUT)

    try:
        # 1. Faz a leitura momentânea do GPS
        # Timeout de 2 segundos evita que o programa trave caso o Arduino desconecte
        with serial.Serial(port, baud, timeout=2) as ser:
            
            # Tenta ler algumas linhas até achar uma coordenada válida
            for _ in range(15): 
                if ser.in_waiting > 0:
                    linha = ser.readline().decode('utf-8').strip()
                    
                    # Ignora linhas vazias ou mensagens de espera
                    if linha and "," in linha and "Aguardando" not in linha:
                        partes = linha.split(',')
                        if len(partes) == 2:
                            lat = float(partes[0])
                            lon = float(partes[1])
                            break  # Coordenada encontrada, sai do laço de leitura
                
                time.sleep(0.1) # Pausa curta para não sobrecarregar a CPU

        # 2. Aciona o pino GPIO pelo tempo especificado (bip)
        GPIO.output(gpio_pin_out, GPIO.HIGH)
        time.sleep(bip_ms / 1000.0)  # Converte ms para segundos
        GPIO.output(gpio_pin_out, GPIO.LOW)

    except serial.SerialException as e:
        print(f"[Erro GPS] Falha na porta serial {port}: {e}")
    except ValueError:
        print(f"[Erro GPS] Falha ao converter os dados recebidos: '{linha}'")
    except Exception as e:
        print(f"[Erro GPS] Erro inesperado: {e}")
    
    # Retorna as coordenadas. Retornará (0.0, 0.0) em caso de falha de leitura.
    return lat, lon

# ==========================================
# Exemplo de uso:
# ==========================================
if __name__ == "__main__":
    configuracao = {
        "port": "/dev/serial0",
        "baud": 9600,
        "gpio_pin_out": 18, # Pino GPIO 18 (Pino físico 12)
        "bip_ms": 200       # 200 milissegundos de pulso
    }
    
    latitude, longitude = get_gps_position(configuracao)
    print(f"Posição lida - Lat: {latitude}, Lon: {longitude}")
    
    # Opcional: limpar os pinos ao encerrar totalmente o script
    # GPIO.cleanup()