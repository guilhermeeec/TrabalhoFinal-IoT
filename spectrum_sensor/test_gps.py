import serial
import time

# Porta serial mapeada para os pinos RX/TX (GPIO 14/15) no Raspberry Pi
PORTA = '/dev/serial0'
BAUD_RATE = 9600

def ler_dados_gps():
    try:
        # Inicializa a conexão serial
        ser = serial.Serial(PORTA, BAUD_RATE, timeout=1)
        print(f"Lendo dados da porta {PORTA} a {BAUD_RATE} bps...")
        print("Pressione Ctrl+C para interromper.\n")

        while True:
            if ser.in_waiting > 0:
                # Lê a linha, decodifica para string e remove quebras de linha
                linha = ser.readline().decode('utf-8').strip()
                
                if linha:
                    # Captura apenas a sentença que contém os dados de localização principais
                    if linha.startswith('$GPGGA'):
                        partes = linha.split(',')
                        
                        # Verifica se o GPS já tem sinal válido (o campo 6 deve ser > 0)
                        qualidade_sinal = partes[6]
                    
                        if qualidade_sinal != '0' and partes[2] and partes[4]:
                            lat_nmea = partes[2]
                            lat_dir = partes[3] # S ou N
                            lon_nmea = partes[4]
                            lon_dir = partes[5] # W ou E
                        
                            print(f"Latitude: {lat_nmea} {lat_dir} | Longitude: {lon_nmea} {lon_dir}")
                        else:
                            print("Aguardando precisão dos satélites...")
            time.sleep(0.1) # Pausa curta para não sobrecarregar a CPU

    except serial.SerialException as e:
        print(f"Erro na comunicação serial: {e}")
        print("Verifique se a interface serial está ativada no raspi-config e as permissões de porta.")
    except KeyboardInterrupt:
        print("\nLeitura encerrada pelo usuário.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Porta serial fechada.")

if __name__ == '__main__':
    ler_dados_gps()