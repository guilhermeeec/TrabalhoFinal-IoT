import json

def load_params(json_path:str="config.json")->dict:
    """
    Lê o arquivo JSON e retorna um dicionário com os parâmetros,
    incluindo as variáveis calculadas (center_freq e bandwidth).
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Calcula a Frequência Central baseada no Canal escolhido
    if config['channel'].upper() == "UL":
        config['center_freq'] = config['freq_ul']
    else:
        config['center_freq'] = config['freq_dl']
        
    # Calcula a Largura de Banda de amostragem
    config['bandwidth'] = config['larg_banda'] / config['bw_reduction_ratio']
    
    return config