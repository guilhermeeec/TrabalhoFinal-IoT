import time
import pandas as pd
import os
import threading
import requests

class Data:
    def __init__(self, csv_dir, config):
        """
        Inicializa a gestão de dados.
        :param csv_dir: Caminho para o diretório onde os arquivos serão salvos.
        :param config: Dicionário de configurações.
        """
        self.csv_dir = csv_dir
        self.config = config
        
        # 1. Garante que o diretório exista
        if not os.path.exists(self.csv_dir):
            os.makedirs(self.csv_dir)
            
        # 2. Cria um nome de arquivo exclusivo baseado no timestamp de criação
        self.filename = f"scan_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        self.full_path = os.path.join(self.csv_dir, self.filename)

    def create_csv_file(self):
        """Cria o arquivo CSV inicial com o cabeçalho no diretório especificado."""
        cols = ['fonte', 'operadora', 'timestamp',
                'latitude', 'longitude', 'geracao',
                'FreqDL', 'FreqUL', 'larguraCanal',
                'potencia', 'FreqDL_cel2', 'FreqUL_cel2',
                'larguraCanal_cel2', 'potencia_cel2']
        df = pd.DataFrame(columns=cols)
        df.to_csv(self.full_path, index=False)
        print(f"Arquivo de dados criado: {self.full_path}")
        return df

    def insert_into_csv(self, power_dbm, lat, lon):
        """Insere os dados coletados no arquivo CSV exclusivo."""
        timestamp = time.strftime("'%Y.%m.%d_%H.%M.%S'")
        
        # Carrega o arquivo atual
        df = pd.read_csv(self.full_path)

        new_row = pd.DataFrame({
            'fonte': [self.config['fonte']],
            'operadora': [self.config['operadora']],
            'timestamp': [timestamp],
            'latitude': [lat],
            'longitude': [lon],
            'geracao': [self.config['geracao']],
            'FreqDL': [self.config['freq_dl'] / 1e6],
            'FreqUL': [self.config['freq_ul'] / 1e6],
            'larguraCanal': [self.config['larg_banda'] / 1e6],
            'potencia': [power_dbm],
            'FreqDL_cel2': [self.config['freq_dl'] / 1e6],
            'FreqUL_cel2': [self.config['freq_ul'] / 1e6],
            'larguraCanal_cel2': [self.config['larg_banda'] / 1e6],
            'potencia_cel2': [power_dbm]
        })
        
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.full_path, index=False)

    def send_data(self, url):
        """
        Inicia uma thread separada para tentar enviar o arquivo CSV para um servidor.
        """
        upload_thread = threading.Thread(target=self._upload_worker, args=(url,))
        upload_thread.start()
        print(f"Tarefa de upload para {self.filename} iniciada em background.")

    def _upload_worker(self, url):
        """
        Lógica de upload com retry e backoff exponencial (1, 2, 4, 8 segundos).
        """
        max_retries = 4
        backoff_times = [1, 2, 4, 8]
        
        for i in range(max_retries):
            try:
                # Abre o arquivo em modo binário para upload
                with open(self.full_path, 'rb') as f:
                    files = {'file': (self.filename, f)}
                    response = requests.post(url, files=files, timeout=10)
                
                if response.status_code == 200:
                    print(f"Sucesso: Arquivo {self.filename} enviado com êxito.")
                    return # Sai da função se o upload der certo
                else:
                    print(f"Erro no servidor ({response.status_code}): Tentativa {i+1}/{max_retries}")
            
            except Exception as e:
                print(f"Erro de conexão na tentativa {i+1}: {e}")
            
            # Se não for a última tentativa, espera antes de tentar de novo
            if i < max_retries - 1:
                wait_time = backoff_times[i]
                print(f"Aguardando {wait_time}s para nova tentativa...")
                time.sleep(wait_time)
        
        print(f"Falha definitiva: Não foi possível enviar {self.filename} após {max_retries} tentativas.")