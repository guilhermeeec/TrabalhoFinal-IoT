import serial
import time
# Substituímos a importação do RPi.GPIO pelo gpiozero
from gpiozero import DigitalOutputDevice

def get_gps_position(config:dict)->tuple[float, float]:
    # Verifica se deve usar o GPS real ou retornar mock
    if not config.get("real_gps", True): 
        return -22.9068, -43.1729
    
    port = config.get('port', '/dev/serial0')
    baud = config.get('baud', 9600)
    gpio_pin_out = config.get("gpio_pin_out", 18)
    bip_ms = config.get("bip_ms", 500)

    lat, lon = 0.0, 0.0

    # Configuração do GPIO com gpiozero
    # Não precisamos mais de setmode ou setup. A classe DigitalOutputDevice
    # já configura o pino BCM como saída (OUT) automaticamente.
    pino_bip = DigitalOutputDevice(gpio_pin_out)

    try:
        # 1. Faz a leitura momentânea do GPS[cite: 2]
        # Timeout de 2 segundos evita que o programa trave[cite: 2]
        with serial.Serial(port, baud, timeout=2) as ser:
            
            for _ in range(15): 
                if ser.in_waiting > 0:
                    linha = ser.readline().decode('utf-8').strip()
                    
                    if linha and "," in linha and "Aguardando" not in linha:
                        partes = linha.split(',')
                        if len(partes) == 2:
                            lat = float(partes[0])
                            lon = float(partes[1])
                            break  
                
                time.sleep(0.1) 

        # 2. Aciona o pino GPIO pelo tempo especificado (bip)[cite: 2]
        pino_bip.on()  # Substitui GPIO.output(gpio_pin_out, GPIO.HIGH)[cite: 2]
        time.sleep(bip_ms / 1000.0)  
        pino_bip.off() # Substitui GPIO.output(gpio_pin_out, GPIO.LOW)[cite: 2]

    except serial.SerialException as e:
        print(f"[Erro GPS] Falha na porta serial {port}: {e}")
    except ValueError:
        print(f"[Erro GPS] Falha ao converter os dados recebidos.")
    except Exception as e:
        print(f"[Erro GPS] Erro inesperado: {e}")
    finally:
        # [MUITO IMPORTANTE] No gpiozero, se você instanciar o pino dentro de uma 
        # função que é chamada várias vezes, precisa usar o .close() para liberá-lo.
        # Caso contrário, na segunda vez que a função rodar, dará erro de "Pin In Use".
        pino_bip.close()
    
    return lat, lon

# ==========================================
# Exemplo de uso:
# ==========================================
if __name__ == "__main__":
    configuracao = {
        "real_gps": True,       # Chave adicionada para o if inicial funcionar corretamente
        "port": "/dev/serial0",
        "baud": 9600,
        "gpio_pin_out": 18,     # Pino GPIO 18 (Pino físico 12)[cite: 2]
        "bip_ms": 200           # 200 milissegundos de pulso[cite: 2]
    }
    
    latitude, longitude = get_gps_position(configuracao)
    print(f"Posição lida - Lat: {latitude}, Lon: {longitude}")