import numpy as np
from matplotlib import pyplot as plt
import json
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def plot_matrix(m:np.ndarray, path=None):
    plt.figure(figsize=(5,5))
    plt.axis('off')
    plt.imshow(m, cmap='hot', vmin=0, vmax=1)
    plt.tight_layout()
    if path:
        plt.savefig(path)
    else:
        plt.show()

class Scaler():
    def __init__(self, scaler='minmax', bounds=(0, 1), min_trunc=None, max_trunc=None):
        self.scaler = scaler
        self.bounds = tuple(bounds) # Garante que seja tupla
        self.min_trunc = min_trunc
        self.max_trunc = max_trunc
        
        if self.scaler == 'minmax':
            self.sc = MinMaxScaler(feature_range=self.bounds)
        else:
            self.sc = StandardScaler()
        
    def fit(self, data):
        data = data.flatten().reshape(-1,1)
        self.sc.partial_fit(data)
        if self.min_trunc:
            if self.sc.data_min_ < self.min_trunc:
                self.sc.data_min_ = self.min_trunc
        if self.max_trunc:
            if self.sc.data_max_ > self.max_trunc:
                self.sc.data_max_ = self.max_trunc

    def transform(self, data):
        data_shape = data.shape
        data = data.flatten().reshape(-1,1)
        if self.min_trunc:
            data[data < self.min_trunc] = self.min_trunc
        if self.max_trunc:
            data[data > self.max_trunc] = self.max_trunc
        data = self.sc.transform(data)
        data = data.reshape(data_shape)        
        return data
    
    def reverse_transform(self, data):
        data_shape = data.shape
        data = data.flatten().reshape(-1,1)
        data = self.sc.inverse_transform(data)
        data = data.reshape(data_shape)
        return data

    def to_dict(self):
        """Extrai todos os atributos e parâmetros ajustados para um dicionário."""
        sc_state = {}
        for key, value in self.sc.__dict__.items():
            if isinstance(value, np.ndarray):
                sc_state[key] = value.tolist()
            elif isinstance(value, np.generic): # Lida com escalares do numpy (np.float64, etc)
                sc_state[key] = value.item()
            else:
                sc_state[key] = value

        return {
            'scaler': self.scaler,
            'bounds': self.bounds,
            'min_trunc': self.min_trunc,
            'max_trunc': self.max_trunc,
            'sc_state': sc_state
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstrói a classe a partir do dicionário de dados."""
        # Inicializa a classe base
        obj = cls(
            scaler=data.get('scaler', 'minmax'),
            bounds=data.get('bounds', (0, 1)),
            min_trunc=data.get('min_trunc'),
            max_trunc=data.get('max_trunc')
        )
        
        # Restaura os parâmetros da classe scikit-learn
        sc_state = {}
        for key, value in data['sc_state'].items():
            if isinstance(value, list):
                sc_state[key] = np.array(value)
            else:
                sc_state[key] = value
                
        obj.sc.__dict__.update(sc_state)
        return obj

    def save(self, filepath: str):
        """Salva o estado do scaler em um arquivo JSON."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, filepath: str):
        """Carrega o scaler a partir de um arquivo JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

class ScalerModel:
    def __init__(self, path: str):
        # Agora carrega diretamente do JSON (usando o método da classe)
        self.scaler = Scaler.load(path)

    def transform(self, data):
        return self.scaler.transform(data)
    
    def reverse_transform(self, data):
        return self.scaler.reverse_transform(data)

class REM:
    def __init__(self, 
                 path_to_rem_pkl:str,
                 scaler_path:str):

        t_x_points, t_channel_pows, t_y_masks = self._load_rem(path_to_rem_pkl)
        '''
        t_x_points: 1 (1 mapa apenas) x 2 (tipo de mapa -> potencia na dim 1 e mascara de medidas na dim 2) x 32 (x, de 0 a 31) x 32 (y, de 0 a 31) 
        t_channel_pows: 1x1x32x32 -> eh o alvo (y)
        t_y_masks: 1x1x32x32 -> tudo 1
        '''
        #print("X shape: ", t_x_points.shape)
        #print("y shape: ", t_channel_pows.shape)
        
        self.raw_power = t_channel_pows[0,0,:,:]
        ''' 
        raw_power: 32x32
        '''

        self.scaler = ScalerModel(scaler_path)

        t_x_points, t_channel_pows, _ = self._apply_transforms(t_x_points, t_channel_pows, t_y_masks)
        '''
        t_x_points: 1x2x32x32 -> agora, a dim [:,0,:,:] teve mascara aplicada alem da normalizacao -> potencia zero onde nao foi medido
        t_channel_pows: 1x1x32x32 -> foi normalizada
        '''

        self._prepare_maps_for_visualization(t_x_points, t_channel_pows)
        
        self.norm_power = t_channel_pows[0,0,:,:]
        '''
        norm_power: 32x32 eh o conteudo que tava em t_channel_pows
        '''

        self.prediction = None
        self.prediction = self._interpol_krigging(t_x_points)
        '''
        prediction: 32x32
        '''

    def get_raw_power_matrix(self)->np.ndarray:
        #rint(f"Got array with shape {self.raw_power.shape}")
        return self.raw_power
        
    def get_normalized_power_matrix(self)->np.ndarray:
        #print(f"Got array with shape {self.norm_power.shape}")
        return self.norm_power
        
    def get_raw_interpol_matrix(self)->np.ndarray:
        if self.prediction is None:
            print("Interpolation not set during initialization")
            return None
        inverted = self.scaler.reverse_transform(self.prediction[np.newaxis, np.newaxis, :])
        #print(f"Got array with shape {inverted.shape}")
        return inverted

    def get_normalized_interpol_matrix(self)->np.ndarray:
        if self.prediction is None:
            print("Interpolation not set during initialization")
            return None
        #print(f"Got array with shape {self.prediction.shape}")
        return self.prediction

    def visualize_input(self, png_path:str=None, just_input=True):
        if just_input:
            return plot_matrix(self.sample_map, png_path)
        fig, axs = plt.subplots(1,3, figsize=(6,5))
        axs[0].imshow(self.sample_map, cmap='hot', vmin=0, vmax=1)
        axs[0].set_title('Sampled Map')
        axs[1].imshow(self.env_mask, cmap='binary')
        axs[1].set_title('Environment Mask')
        axs[2].imshow(self.target, cmap='hot', vmin=0, vmax=1)
        axs[2].set_title('Complete Radio Map')
        [ax.set_xticks([]) for ax in axs]
        [ax.set_yticks([]) for ax in axs]
        fig.tight_layout()
        fig.savefig(png_path)
    
    def visualize_output(self, png_path:str=None):
        plt.figure(figsize=(5,5))
        plt.axis('off')
        plt.title('Model Output')
        plt.imshow(self.prediction, cmap='hot', vmin=0, vmax=1)
        plt.tight_layout()
        plt.savefig(png_path)
        plt.show()
    
    def _interpol_krigging(self, t_x_points:np.ndarray)->np.ndarray:
        from pykrige.ok import OrdinaryKriging
        power = t_x_points[0,0,:,:]
        mask = t_x_points[0,1,:,:]
        y_measure, x_measure = np.where(mask == 1)
        
        # 1. Garante que os pontos conhecidos são floats
        x_measure = x_measure.astype(float)
        y_measure = y_measure.astype(float)
        z_measured = power[y_measure.astype(int), x_measure.astype(int)].astype(float)
        
        ok = OrdinaryKriging(
            x_measure,
            y_measure,
            z_measured,
            variogram_model="linear",
            verbose=False,
            enable_plotting=False)
        
        rows, columns = power.shape
        
        # 2. Garante que o grid de interpolação também é float
        grid_x = np.arange(columns, dtype=float)
        grid_y = np.arange(rows, dtype=float)

        z_interpol, _ = ok.execute('grid', grid_x, grid_y)

        final = np.copy(power)
        no_measure = (mask == 0)
        final[no_measure] = z_interpol[no_measure]
        return final

    def _prepare_maps_for_visualization(self, t_x_points:np.ndarray, t_y_points:np.ndarray):
        self.sample_map = t_x_points[0,0,:,:]
        self.env_mask = t_x_points[0,1,:,:]
        self.target = t_y_points[0,0,:,:]
        self.target[self.env_mask==-1] = 1

    def _load_rem(self,path:str):
        t_x_points, t_channel_pows, t_y_masks = np.load(path, allow_pickle=True)
        return t_x_points, t_channel_pows, t_y_masks

    def _apply_transforms(self, t_x_points:np.ndarray, t_channel_pows:np.ndarray, t_y_masks:np.ndarray):
        t_y_points = t_channel_pows * t_y_masks
        t_x_masks = t_x_points[:,1,:,:] == 1

        t_x_points[:,0,:,:] = self.scaler.transform(t_x_points[:,0,:,:]) * t_x_masks
        t_channel_pows = self.scaler.transform(t_channel_pows)
        t_y_points = self.scaler.transform(t_y_points)

        return t_x_points, t_channel_pows, t_y_points
