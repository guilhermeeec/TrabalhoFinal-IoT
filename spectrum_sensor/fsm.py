import signal
import time

class FSM:
    def __init__(self, mode, pin_start=None, pin_stop=None):
        self._is_working = False
        self.mode = mode

        if self.mode == "sw_interrupt":
            # Configura escuta de sinais do SO (Linux/POSIX)
            # SIGUSR1 = Iniciar / SIGUSR2 = Parar
            signal.signal(signal.SIGUSR1, self._start_handler)
            signal.signal(signal.SIGUSR2, self._stop_handler)
            print("FSM: Modo SW_INTERRUPT. Aguardando sinais SIGUSR1(Start) e SIGUSR2(Stop).")
            
        elif self.mode == "hw_interrupt":
            # Substitui RPi.GPIO pelo gpiozero
            from gpiozero import Button
            
            self.pin_start = pin_start
            self.pin_stop = pin_stop
            
            # O gpiozero já configura como entrada e usa pull-up interno por padrão.
            # O bounce_time no gpiozero é em segundos (0.3 = 300ms).
            self.button_start = Button(self.pin_start, pull_up=True, bounce_time=0.3)
            self.button_stop = Button(self.pin_stop, pull_up=True, bounce_time=0.3)

            # Associa os eventos (quando pressionado = FALLING) às funções de callback
            self.button_start.when_pressed = self._start_handler
            self.button_stop.when_pressed = self._stop_handler
            
            print(f"FSM: Modo HW_INTERRUPT. Pinos GPIO (gpiozero): Start({pin_start}), Stop({pin_stop}).")
            
        else:
            raise ValueError(f"Modo de interrupção '{mode}' desconhecido.")

    # O *args é mantido para compatibilidade com o módulo 'signal',
    # que envia argumentos (número do sinal e frame) ao callback.
    def _start_handler(self, *args):
        if not self._is_working:
            print("\n>>> [Sinal/Interrupção] Mudando estado para: WORKING")
            self._is_working = True

    def _stop_handler(self, *args):
        if self._is_working:
            print("\n>>> [Sinal/Interrupção] Mudando estado para: WAITING")
            self._is_working = False

    def is_working(self): # Corrigido o erro de digitação (era is_woqrking)[cite: 1]
        return self._is_working

    def is_waiting(self):
        return not self._is_working
    
    def cleanup(self):
        if self.mode == "hw_interrupt":
            # O gpiozero faz a limpeza automática ao final do script, 
            # mas podemos fechar as conexões explicitamente para garantir.[cite: 1]
            if hasattr(self, 'button_start'):
                self.button_start.close()
            if hasattr(self, 'button_stop'):
                self.button_stop.close()