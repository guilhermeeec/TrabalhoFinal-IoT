import time
import os
from params import load_params
from data import Data
from gps import get_gps_position
from sdr import Sdr
from fsm import FSM

def working_loop(fsm, config, dataset, sdr_device):
    """Loop isolado que roda apenas enquanto o estado for 'working'"""
    print(">>> Iniciando loop de captura (WORKING)...")
    
    while fsm.is_working():
        power_dbm = sdr_device.get_channel_power_dbm()
        lat, lon = get_gps_position()
        dataset.insert_into_csv(power_dbm, lat, lon)
        time.sleep(config['wait_time'])
        
    print(">>> Saindo do loop de captura. Sistema em espera.")
    # Exemplo: dataset.send_data(config['server_url']) 

def main():
    # Salva o PID do processo atual para o script de testes encontrar
    with open("main.pid", "w") as f:
        f.write(str(os.getpid()))

    config = load_params('config.json')
    dataset = Data(config['csv_dir'], config)
    dataset.create_csv_file()
    
    # Inicializa a Máquina de Estados
    fsm = FSM(
        mode=config['interrupt_mode'],
        pin_start=config.get('gpio_pin_start', 17), # Valores padrão BCM
        pin_stop=config.get('gpio_pin_stop', 27)
    )

    sdr_device = None
    try:
        sdr_device = Sdr(config)
        
        # Loop infinito principal da aplicação
        while True:
            if fsm.is_working():
                # Entra no loop de trabalho e fica lá enquanto a flag for verdadeira
                working_loop(fsm, config, dataset, sdr_device)
            else:
                # Sistema no estado 'waiting'
                # Dorme um pouco para não fritar a CPU do Raspberry com um loop vazio
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\nRotina interrompida pelo usuário.")
        
    except Exception as e:
        print(f"\nErro de execução: {e}")
        
    finally:
        # Limpeza segura do hardware
        if sdr_device is not None:
            sdr_device.close()
        
        fsm.cleanup()  # Para o modo de hardware, limpa os GPIOs
            
        # Remove o arquivo do PID ao sair
        if os.path.exists("main.pid"):
            os.remove("main.pid")

if __name__ == '__main__':
    main()