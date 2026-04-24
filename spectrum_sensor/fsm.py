import signal

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
            # O RPi.GPIO só é importado se o modo for hardware, 
            # evitando erros caso você rode o código de testes no seu PC.
            import RPi.GPIO as GPIO
            
            self.pin_start = pin_start
            self.pin_stop = pin_stop
            
            GPIO.setmode(GPIO.BCM)
            # Configura pinos como entrada e ativa os resistores pull-up internos
            GPIO.setup(self.pin_start, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.pin_stop, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Configura as interrupções para borda de descida (botão apertado = GND = Falling)
            # O bouncetime previne múltiplas leituras pelo repique do botão mecânico
            GPIO.add_event_detect(self.pin_start, GPIO.FALLING, callback=self._start_handler, bouncetime=300)
            GPIO.add_event_detect(self.pin_stop, GPIO.FALLING, callback=self._stop_handler, bouncetime=300)
            
            print(f"FSM: Modo HW_INTERRUPT. Pinos GPIO: Start({pin_start}), Stop({pin_stop}).")
            
        else:
            raise ValueError(f"Modo de interrupção '{mode}' desconhecido.")

    def _start_handler(self, *args):
        if not self._is_working:
            print("\n>>> [Sinal/Interrupção] Mudando estado para: WORKING")
            self._is_working = True

    def _stop_handler(self, *args):
        if self._is_working:
            print("\n>>> [Sinal/Interrupção] Mudando estado para: WAITING")
            self._is_working = False

    def is_working(self):
        return self._is_working

    def is_waiting(self):
        return not self._is_working
    
    def cleanup(self):
        if self.mode == "hw_interrupt":
            import RPi.GPIO as GPIO
            GPIO.cleanup()