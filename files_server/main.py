import os
from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Lê as configurações das variáveis de ambiente injetadas pelo Docker
UPLOAD_FOLDER = os.environ.get('UPLOAD_DIR_CONTAINER', '/app/uploads')
PORT = int(os.environ.get('CONTAINER_PORT', 5000))

# Garante que o diretório de destino exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Verifica se a requisição contém o campo 'file'
    if 'file' not in request.files:
        return "Nenhum arquivo enviado na requisição", 400
        
    file = request.files['file']
    
    # Verifica se o usuário enviou um arquivo sem nome
    if file.filename == '':
        return "Nome de arquivo vazio", 400
        
    if file:
        # secure_filename remove caracteres perigosos do nome do arquivo original
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(save_path)
            return f"Upload concluído com sucesso: {filename}", 200
        except Exception as e:
            return f"Erro ao salvar o arquivo: {str(e)}", 500

if __name__ == '__main__':
    # host='0.0.0.0' é obrigatório no Docker para que o app seja acessível externamente
    app.run(host='0.0.0.0', port=PORT)