import sys
import os
import signal

def main():
    # Validações dos argumentos do terminal
    if len(sys.argv) < 2 or sys.argv[1] not in ["resume", "stop"]:
        print("Uso correto: python sw_interrupt.py [resume | stop]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        # Lê o número do processo principal
        with open("main.pid", "r") as f:
            pid = int(f.read().strip())
    except FileNotFoundError:
        print("Erro: Arquivo main.pid não encontrado. O main.py está rodando?")
        sys.exit(1)
        
    # Envia o sinal apropriado
    try:
        if command == "resume":
            print(f"Disparando interrupção de INÍCIO (SIGUSR1) para o processo {pid}...")
            os.kill(pid, signal.SIGUSR1)
        elif command == "stop":
            print(f"Disparando interrupção de PARADA (SIGUSR2) para o processo {pid}...")
            os.kill(pid, signal.SIGUSR2)
    except ProcessLookupError:
        print(f"Erro: O processo {pid} não existe mais. Reinicie o main.py.")

if __name__ == '__main__':
    main()