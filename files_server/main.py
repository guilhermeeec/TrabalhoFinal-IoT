import os
import threading
from flask import Flask, request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename

# Importa a sua função do novo diretório
from formatter.generate_matrixes import format_dataset_into_matrixes

app = Flask(__name__)

UPLOAD_FOLDER = os.environ.get('UPLOAD_DIR_CONTAINER', '/app/uploads')
DOWNLOAD_FOLDER = os.environ.get('DOWNLOAD_DIR_CONTAINER', '/app/downloads')
PORT = int(os.environ.get('CONTAINER_PORT', 5000))

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

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
        .no-map { background: #eee; padding: 50px; border-radius: 5px; margin-bottom: 15px; color: #777; font-style: italic; border: 1px dashed #ccc; }
        .botoes { display: flex; justify-content: center; gap: 15px; }
        .btn { padding: 10px 20px; text-decoration: none; color: #fff; border-radius: 5px; font-weight: bold; cursor: pointer; }
        .btn-img { background-color: #007bff; }
        .btn-img:hover { background-color: #0056b3; }
        .btn-gerar { background-color: #ff9800; }
        .btn-gerar:hover { background-color: #e68a00; }
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
                
                {% if item.has_image %}
                    <img src="/files/image/{{ item.image_file }}" alt="{{ item.name }}">
                    <div class="botoes">
                        <a href="/files/image/{{ item.image_file }}" download class="btn btn-img">⬇ Download Imagem</a>
                        <a href="/files/csv/{{ item.csv_file }}" download class="btn btn-csv">⬇ Download CSV Bruto</a>
                    </div>
                {% else %}
                    <div class="no-map">Mapa não gerado</div>
                    <div class="botoes">
                        <a href="/generate/{{ item.name }}" class="btn btn-gerar">⚙ Gerar mapa</a>
                        <a href="/files/csv/{{ item.csv_file }}" download class="btn btn-csv">⬇ Download CSV Bruto</a>
                    </div>
                {% endif %}
            </div>
            {% endfor %}
        {% else %}
            <p>Nenhum dado bruto encontrado no diretório.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    items = []
    if os.path.exists(UPLOAD_FOLDER):
        # Varre pela fonte da verdade: os arquivos CSV gerados pelo SDR
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.csv')]
        files.sort(reverse=True)
        
        for csv_file in files:
            name_without_ext = os.path.splitext(csv_file)[0]
            
            # Verifica se existe uma imagem gerada com o mesmo nome
            # Aceitando .jpg ou .png
            image_file = None
            has_image = False
            
            if os.path.exists(os.path.join(DOWNLOAD_FOLDER, f"{name_without_ext}.jpg")):
                image_file = f"{name_without_ext}.jpg"
                has_image = True
            elif os.path.exists(os.path.join(DOWNLOAD_FOLDER, f"{name_without_ext}.png")):
                image_file = f"{name_without_ext}.png"
                has_image = True
                
            items.append({
                'name': name_without_ext,
                'csv_file': csv_file,
                'has_image': has_image,
                'image_file': image_file
            })
            
    return render_template_string(HTML_TEMPLATE, items=items)

@app.route('/generate/<dataset_name>', methods=['GET'])
def generate_map(dataset_name):
    # Cria uma thread para processar o mapa sem travar o servidor Flask
    thread = threading.Thread(target=format_dataset_into_matrixes, args=(f"{dataset_name}.csv",))
    thread.start()
    
    # Retorna uma resposta imediata para o usuário
    return """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gerando Mapa</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 100px; background-color: #f4f4f9; color: #333;}
            .btn { display: inline-block; margin-top: 20px; padding: 10px 20px; text-decoration: none; background-color: #007bff; color: white; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h2>Mapa sendo gerado. Volte mais tarde.</h2>
        <a href="/" class="btn">Voltar para a galeria</a>
    </body>
    </html>
    """

@app.route('/files/image/<filename>')
def serve_image(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

@app.route('/files/csv/<filename>')
def serve_csv(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "Nenhum arquivo enviado", 400
        
    file = request.files['file']
    if file.filename == '':
        return "Nome vazio", 400
        
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(save_path)
            return f"Upload concluído: {filename}", 200
        except Exception as e:
            return f"Erro ao salvar: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)