#!/bin/bash

# Verifica se o hostname foi fornecido
if [ -z "$1" ]; then
    echo "Uso: $0 <usuario@hostname> [diretorio_destino]"
    echo "Exemplo: $0 usuario@192.168.1.100 /caminho/no/servidor/"
    exit 1
fi

HOST="$1"
# Se um segundo argumento for passado, usa como destino. Se não, copia para o home (~/).
DESTINO="${2:-~/IoT/}" 

# Verifica se o arquivo .copyignore existe no diretório atual
EXCLUDE_ARG=""
if [ -f ".copyignore" ]; then
    EXCLUDE_ARG="--exclude-from=.copyignore"
else
    echo "Aviso: Arquivo '.copyignore' não encontrado. Todos os arquivos serão transferidos."
fi

echo "Iniciando cópia para $HOST:$DESTINO"
echo "O SSH solicitará sua senha abaixo:"
echo "---------------------------------------------------"

# Executa o rsync
# -a: archive mode (recursivo, preserva permissões, donos e links)
# -v: verbose (mostra os arquivos sendo copiados)
# -z: comprime os dados durante a transferência pela rede
# -P: mostra a barra de progresso para cada arquivo
rsync -avzP $EXCLUDE_ARG ./ "$HOST:$DESTINO"

echo "---------------------------------------------------"
echo "Transferência finalizada!"