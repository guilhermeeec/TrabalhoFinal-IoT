import time
import pandas as pd
import numpy as np
from rtlsdr import RtlSdr

# ==========================================
# Funções Abstraídas (Mocks)
# ==========================================

def get_gps_position():
    """
    Abstração: Retorna a posição GPS atual.
    Substitua pela sua lógica (ex: leitura serial de um módulo GPS NMEA).
    """
    # Retornando coordenadas genéricas (ex: Rio de Janeiro)
    return -22.9068, -43.1729

def create_csv_file():
    """
    Abstração: Cria o arquivo CSV e escreve o cabeçalho.
    Substitua pela sua lógica (ex: biblioteca csv ou pandas).
    """
    # Define column names
    cols = ['fonte','operadora','timestamp',
            'latitude','longitude','geracao',
            'FreqDL', 'FreqUL', 'larguraCanal',
            'potencia','FreqDL_cel2','FreqUL_cel2',
            'larguraCanal_cel2','potencia_cel2']
    df = pd.DataFrame(columns=cols)
    df.to_csv(CSV_PATH, index=False)
    return df

def insert_into_csv(timestamp, power_dbm, lat, lon):
    """
    Abstração: Insere os dados no arquivo CSV.
    Substitua pela sua lógica (ex: biblioteca csv ou pandas).
    """

    df = pd.read_csv(CSV_PATH)

    new_row = pd.DataFrame({
        'fonte': [FONTE],
        'operadora': [OERADORA],
        'timestamp': [timestamp],
        'latitude': [lat],
        'longitude': [lon],
        'geracao': [GERACAO],
        'FreqDL': [FREQ_DL/1e6],
        'FreqUL': [FREQ_UL/1e6],
        'larguraCanal': [LARG_BANDA/1e6],
        'potencia': [power_dbm],
        'FreqDL_cel2': [FREQ_DL/1e6],
        'FreqUL_cel2': [FREQ_UL/1e6],
        'larguraCanal_cel2': [LARG_BANDA/1e6],
        'potencia_cel2': [power_dbm]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

# ==========================================
# Configurações de Monitoramento
# ==========================================

CSV_PATH = 'spectrum_data.csv'  # Caminho do arquivo CSV para armazenar os dados

FONTE = "RafaelSDR"
OERADORA = "-"
GERACAO = "HSPA"
FREQ_DL = 882.8e6      # Frequência de Downlink em Hz (ex: 882.8 MHz)
FREQ_UL = 837.8e6      # Frequência de Uplink em Hz (ex: 837.8 MHz)
LARG_BANDA = 5e6      # Largura de banda em Hz (ex: 5 MHz)

CHANNEL = "UL" # Canal de interesse: "DL" ou "UL"
BW_REDUCTION_RATIO = 5 # Reduz a largura de banda para evitar sobrecarga do SDR (ex: 5 vezes menor que a largura de banda nominal)
CENTER_FREQ = FREQ_UL if CHANNEL == "UL" else FREQ_DL  # Frequência central em Hz (ex: 882.8 MHz)
BANDWIDTH = LARG_BANDA / BW_REDUCTION_RATIO      # Largura de banda / Sample Rate em Hz (ex: 5 MHz)
GAIN = 'auto'            # Ganho de RF (ou valor numérico em dB, ex: 40)
WAIT_TIME = 1.0          # Tempo T em segundos entre as iterações
NUM_SAMPLES = 1024 * 16  # Quantidade de amostras IQ lidas por iteração

# Offset de calibração (empírico). dBm = dBFS + OFFSET
# Você precisará calibrar seu SDR com um gerador de sinal para achar o valor exato.
CALIBRATION_OFFSET = -30.0 

def get_channel_power_dbm(sdr, num_samples):
    """
    Lê as amostras IQ do RTL-SDR e calcula a potência em dBm.
    """
    # Lê as amostras complexas (I + jQ)
    samples = sdr.read_samples(num_samples)
    
    # Calcula a potência média (magnitude ao quadrado das amostras complexas)
    # P = I^2 + Q^2
    mean_power = np.mean(np.abs(samples)**2)
    
    # Previne erro de log de zero
    if mean_power == 0:
        return -np.inf
        
    # Converte para decibéis relativos ao fundo de escala (dBFS)
    power_dbfs = 10 * np.log10(mean_power)
    
    # Aplica a calibração para estimar a potência absoluta no conector do receptor
    power_dbm = power_dbfs + CALIBRATION_OFFSET
    
    return power_dbm

def main():

    create_csv_file()

    # Inicializa a comunicação com o dongle
    sdr = RtlSdr()
    
    # No RTL-SDR, o filtro anti-aliasing é ajustado de acordo com a sample_rate.
    # Logo, a sample_rate define a largura de banda visualizada.
    sdr.sample_rate = BANDWIDTH 
    sdr.center_freq = CENTER_FREQ
    sdr.gain = GAIN
    
    print(f"Iniciando monitoramento de espectro...")
    print(f"Freq Central: {CENTER_FREQ/1e6:.2f} MHz | Banda: {BANDWIDTH/1e6:.2f} MHz\n")

    try:
        # Loop principal de varredura
        while True:
            # 1. Mede a potência no canal (SDR)
            power_dbm = get_channel_power_dbm(sdr, NUM_SAMPLES)
            
            # 2. Pega a localização atual (GPS)
            lat, lon = get_gps_position()
            
            # 3. Formata timestamp atual
            timestamp = time.strftime("'%Y.%m.%d_%H.%M.%S'")
            
            # 4. Grava os dados (CSV)
            insert_into_csv(timestamp, power_dbm, lat, lon)
            
            # 5. Espera tempo T
            time.sleep(WAIT_TIME)
            
    except KeyboardInterrupt:
        print("\nRotina interrompida pelo usuário.")
        
    except Exception as e:
        print(f"\nErro de execução: {e}")
        
    finally:
        # Garante que o recurso de hardware seja liberado ao final
        sdr.close()

if __name__ == '__main__':
    main()