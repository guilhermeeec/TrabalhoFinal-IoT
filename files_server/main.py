import os
from flask import Flask, request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Lê as configurações das variáveis de ambiente injetadas pelo Docker
UPLOAD_FOLDER = os.environ.get('UPLOAD_DIR_CONTAINER', '/app/uploads')
DOWNLOAD_FOLDER = os.environ.get('DOWNLOAD_DIR_CONTAINER', '/app/downloads')
PORT = int(os.environ.get('CONTAINER_PORT', 5000))

# Garante que os diretórios de destino existam
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Template HTML simples injetado direto no código
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galeria do Espectro</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; text-align: center; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #fff; margin-bottom: 30px; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .card h3 { color: #333; margin-top: 0; }
        .card img { max-width: 100%; height: auto; border-radius: 5px; margin-bottom: 15px; border: 1px solid #ddd; }
        .botoes { display: flex; justify-content: center; gap: 15px; }
        .btn { padding: 10px 20px; text-decoration: none; color: #fff; border-radius: 5px; font-weight: bold; }
        .btn-img { background-color: #007bff; }
        .btn-img:hover { background-color: #0056b3; }
        .btn-csv { background-color: #28a745; }
        .btn-csv:hover { background-color: #1e7e34; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Monitoramento de Espectro - Arquivos</h2>
        
        {% if items %}
            {% for item in items %}
            <div class="card">
                <h3>{{ item.name }}</h3>
                <img src="/files/image/{{ item.image_file }}" alt="{{ item.name }}">
                <div class="botoes">
                    <a href="/files/image/{{ item.image_file }}" download class="btn btn-img">⬇ Download Imagem</a>
                    <a href="/files/csv/{{ item.csv_file }}" download class="btn btn-csv">⬇ Download CSV Bruto</a>
                </div>
            </div>
            {% endfor %}
        {% else %}
            <p>Nenhuma imagem encontrada no diretório.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    items = []
    if os.path.exists(DOWNLOAD_FOLDER):
        # Lista todos os arquivos que sejam imagens (.jpg, .png, etc)
        files = [f for f in os.listdir(DOWNLOAD_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        # Ordena para as mais recentes aparecerem no topo (ordem alfabética reversa funciona para o seu formato de data)
        files.sort(reverse=True)
        
        for image_file in files:
            # Extrai o nome sem a extensão (ex: scan_20260518_211646)
            name_without_ext = os.path.splitext(image_file)[0]
            # Associa com o arquivo CSV correspondente
            csv_file = f"{name_without_ext}.csv"
            
            items.append({
                'name': name_without_ext,
                'image_file': image_file,
                'csv_file': csv_file
            })
            
    return render_template_string(HTML_TEMPLATE, items=items)

# Rota para baixar/servir as imagens da pasta /app/downloads
@app.route('/files/image/<filename>')
def serve_image(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

# Rota para baixar/servir os CSVs da pasta /app/uploads
@app.route('/files/csv/<filename>')
def serve_csv(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado na requisição", 400
        
    file = request.files['file']
    
    if file.filename == '':
        return "Nome de arquivo vazio", 400
        
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(save_path)
            return f"Upload concluído com sucesso: {filename}", 200
        except Exception as e:
            return f"Erro ao salvar o arquivo: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)