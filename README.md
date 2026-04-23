# Lado do Cliente

Requisitos:
- Python 3.12.5

```bash
pip install -r spectrum_sensor/requirements.txt
```

## Instalação RTL SDR

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

## Dificuldades encontradas

* Versão certa do pyrtlsdr pro meu HW
* HW limitado a 2.4MHz de banda