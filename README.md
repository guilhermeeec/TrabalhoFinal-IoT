# Lado do Cliente

Requisitos:
- Python 3.12.5

```bash
pip install -r spectrum_sensor/requirements.txt
```

## Descobrindo o IP do Raspberry

```bash
arp -a | grep d8:3a:dd:1a:fe:5e
```

## Instalação RTL SDR do SMT - Alternativa 1, testada no PC

```bash
sudo apt install libusb-1.0-0-dev git cmake pkg-config rtl-sdr
echo 'blacklist dvb_usb_rtl28xxu' | sudo tee --append /etc/modprobe.d/blacklist-dvb.conf
sudo rtl-sdr.rules /etc/udev/rules.d/ # baixar o rtl-sdr.rules do Google
rtl_test 
```

Com o SDR RTL antigo (do SMT):

```bash
pip install pyrtlsdr==0.2.91
```

## Instalação RTL SDR do SMT - Alternativa 2, testada no Raspberry

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install rtl-sdr librtlsdr-dev -y
```

Adicione as seguintes linhas ao arquivo `/etc/modprobe.d/blacklist-rtl.conf`:

```conf
blacklist dvb_usb_rtl28xxu
blacklist rtl2832
blacklist rtl2830
```

Reinicie o dispositivo: `sudo reboot`

Teste: `rtl_test`


```bash
pip install "setuptools<82"
pip install pyrtlsdr==0.2.91
```

## Testando em Python

```bash
$ python3 spectrum_sensor/test_sdr.py
Detached kernel driver
Found Rafael Micro R820T tuner
[R82XX] PLL not locked!
Read 512 samples successfully.
[(-0.0039215686274509665+0.0117647058823529j), (-0.0039215686274509665+0.0039215686274509665j), (0.0039215686274509665-0.0039215686274509665j), (-0.0039215686274509665-0.0039215686274509665j), (-0.0039215686274509665-0.0039215686274509665j), (-0.0039215686274509665+0.0039215686274509665j), (-0.0117647058823529+0.0039215686274509665j), (0.0039215686274509665+0.0039215686274509665j), (0.0039215686274509665-0.0117647058823529j), (0.0039215686274509665+0.0039215686274509665j)]
Reattached kernel driver
```

## Instalação do Arduino CLI

```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=~ sh
sudo mv ~/arduino-cli /bin
arduino-cli core update-index
arduino-cli core install arduino:avr
```

Conecte o Ardino e pegue as configurações:

```bash
arduino-cli board list
```

Resultado guapimirim:

```bash
Port         Protocol Type              Board Name  FQBN            Core
/dev/ttyACM0 serial   Serial Port (USB) Arduino UNO arduino:avr:uno arduino:avr
/dev/ttyS0   serial   Serial Port       Unknown
```

Resultado Raspberry:

```bash
Port         Protocol Type              Board Name  FQBN            Core
/dev/ttyACM0 serial   Serial Port (USB) Arduino UNO arduino:avr:uno arduino:avr
```

## Testando o Arduino

```bash
cd arduino_gps/test
arduino-cli compile --fqbn arduino:avr:uno 
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno
cd ../..
```

## Instalação da biblioteva TinyGPS no Arduino

```bash
arduino-cli lib install "TinyGPSPlus"
```

## Testando o GPS

```bash
cd arduino_gps/gps
arduino-cli compile --fqbn arduino:avr:uno 
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno
cd ../..
```

```bash
cd spectrum_sensor
python test_gps.py
```

## Transferência para o Raspberry

Liste em `.copyignore` arquivos e diretórios que não serão copiados

```bash
chmod +x transfer.sh
./transfer.sh gta@192.168.0.6 # usar endereço certo
```

## Configurações do GPIO no Raspberry

```bash
sudo apt update
sudo apt install python3-dev gcc
sudo apt install swig python3-dev build-essential liblgpio-dev
```

```bash
python -m venv .env
source .env/bin/activate
pip install rpi-lgpio
```

## Rodando o código de coleta no PC

```bash
cd spectrum_sensor
mkdir data
python main.py
```

Em outro terminal:

```bash
cd spectrum_sensor
python sw_interrupt.py start
```

Para interromper a coleta

```bash
cd spectrum_sensor
python sw_interrupt.py stop
```

## Configuração do servidor de arquivos

Requisito: Docker

Edite as duas primeiras linhas de `files_server/.env`

```bash
cd files_server
mkdir from_sensors
mkdir maps
```

Iniciando servidor de teste

```bash
docker compose up -d
docker logs sdr_upload_server -f
```

Enviando arquivo de teste

```bash
curl -F "file=@test.csv" http://localhost:9632/upload
```

## Dificuldades encontradas

* Versão certa do pyrtlsdr pro meu HW
* HW limitado a 2.4MHz de banda
* Indisponibilidade do módulo GPS para raspberry
* Baixa qualidade dos botões
* 

## Notas

* Estou usando o Raspberry Pi 4 com etiqueta escrito `2`.
* Em casa, as características são as seguintes: raspberry `d8:3a:dd:1a:fe:5e 192.168.0.6`
* No lab, após reinstalar o sistema: raspberry: `146.164.69.232` (não é `171`, pois essa é a Ossos)
* O Raspberry está configurado para acessar meu roteador do celular. Para saber a rota de saída usada: `ip route get 8.8.8.8`
* Cópia do Raspberry para a guapimirim da Guapimirim: `scp raspiot:/home/gta/TrabalhoFinal-IoT/spectrum_sensor/data/scan_20260506_164448.csv files_server/test.csv`
* No raspberry, precisei usar `sudo apt-get -o Acquire::ForceIPv4=true install git-all` para instalar o Git