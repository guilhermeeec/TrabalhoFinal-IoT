import numpy as np
from rtlsdr import RtlSdr

class Sdr:
    def __init__(self, config:dict):
        """Inicializa e configura o RTL-SDR com base no dicionário."""
        self.num_samples = config['num_samples']
        self.calibration_offset = config['calibration_offset']
        
        self.sdr = RtlSdr()
        self.sdr.sample_rate = config['bandwidth']
        self.sdr.center_freq = config['center_freq']
        self.sdr.gain = config['gain']
        
        print("SDR Inicializado com sucesso.")
        print(f"Freq Central: {self.sdr.center_freq/1e6:.2f} MHz | Banda: {self.sdr.sample_rate/1e6:.2f} MHz\n")

    def get_channel_power_dbm(self)->float:
        """Lê as amostras IQ e calcula a potência em dBm."""
        samples = self.sdr.read_samples(self.num_samples)
        
        # Calcula a potência média (I^2 + Q^2)
        mean_power = np.mean(np.abs(samples)**2)
        
        if mean_power == 0:
            return -np.inf
            
        # dBFS + Offset de Calibração
        power_dbfs = 10 * np.log10(mean_power)
        power_dbm = power_dbfs + self.calibration_offset
        
        return power_dbm

    def close(self):
        """Garante que o recurso de hardware seja liberado."""
        self.sdr.close()
        print("SDR finalizado e desconectado.")