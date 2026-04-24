# Lado do Cliente

Requisitos:
- Python 3.12.5

```bash
pip install -r spectrum_sensor/requirements.txt
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

```
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
$ python3 spectrum_sensor/test.py
Detached kernel driver
Found Rafael Micro R820T tuner
[R82XX] PLL not locked!
Read 512 samples successfully.
[(-0.0039215686274509665+0.0117647058823529j), (-0.0039215686274509665+0.0039215686274509665j), (0.0039215686274509665-0.0039215686274509665j), (-0.0039215686274509665-0.0039215686274509665j), (-0.0039215686274509665-0.0039215686274509665j), (-0.0039215686274509665+0.0039215686274509665j), (-0.0117647058823529+0.0039215686274509665j), (0.0039215686274509665+0.0039215686274509665j), (0.0039215686274509665-0.0117647058823529j), (0.0039215686274509665+0.0039215686274509665j)]
Reattached kernel driver
```

## Transferência para o Raspberry

Liste em `.copyignore` arquivos e diretórios que não serão copiados

```bash
chmod +x transfer.sh
./transfer.sh gta@192.168.0.6 # usar endereço certo
```

## Dificuldades encontradas

* Versão certa do pyrtlsdr pro meu HW
* HW limitado a 2.4MHz de banda

## Notas

* Estou usando o Raspberry Pi 4 com etiqueta escrito `2`.
* Em casa, as características são as seguintes: raspberry `d8:3a:dd:1a:fe:5e 192.168.0.6`