import numpy as np
import pandas as pd
import os
from pykrige.ok import OrdinaryKriging
import pickle

from formatter.coordinates_processor import CoordinatesBlocks

def get_dataset(dataset_path:str, start_time:str=None, stop_time:str=None):
    df = pd.read_csv(dataset_path)
    if start_time is not None:
        df = df[df["timestamp"] >= start_time]
    if stop_time is not None:
        df = df[df["timestamp"] <= stop_time]
    print("Loaded dataset with {} rows:".format(len(df)))
    print(df.head())
    print("...")
    print("----------------------------------------------")
    return df

def get_channel_df(df:pd.DataFrame, dl_freq:int):
    # Filter using primary cell
    df_with_searched_dl_freq_in_cell_1 = df[ df['FreqDL'] == dl_freq ]

    # Get ul freq and bw
    ul_freq = df_with_searched_dl_freq_in_cell_1['FreqUL'].iloc[0]
    bw = df_with_searched_dl_freq_in_cell_1['larguraCanal'].iloc[0]

    # Remove unecessary columns 
    df1 = df_with_searched_dl_freq_in_cell_1.drop(columns=['FreqDL_cel2', 'FreqUL_cel2', 'larguraCanal_cel2', 'potencia_cel2'])

    # Filter using secundary cell
    df_with_searched_dl_freq_in_cell_2 = df[ df['FreqDL_cel2'] == dl_freq ].drop(columns=['FreqDL', 'FreqUL', 'larguraCanal', 'potencia'])
    
    # Use the same name as df1
    df2 = df_with_searched_dl_freq_in_cell_2.rename(columns={col+'_cel2':col for col in ['FreqDL', 'FreqUL', 'larguraCanal', 'potencia']})
    
    print("For DL frequency {}: {} rows in channel 1, {} rows in channel 2".format(dl_freq, len(df1), len(df2)))
    return {
        "dl":int(dl_freq),
        "ul":int(ul_freq),
        "bw":int(bw),
        "df":pd.concat([df1,df2])
    }

def compute_average_power(df:pd.DataFrame,coords:CoordinatesBlocks):
    cell_power = df.groupby(['cell_x', 'cell_y'])['potencia'].mean().reset_index(name='average_power')
    print("Computed average power:")
    print(cell_power.head())
    print("...")
    return cell_power

def krigging(df:pd.DataFrame, shape:tuple):
    OK = OrdinaryKriging(
        df['cell_x'],
        df['cell_y'],
        df['average_power'],
        variogram_model="linear",
        verbose=False,
        enable_plotting=False,
    )
    z, ss = OK.execute("grid", 
                    np.linspace(0, shape[0], shape[1]), 
                    np.linspace(0, shape[0], shape[1]))
    return z

def transform_into_matrixes(df:pd.DataFrame, shape:tuple, z:np.ndarray):

    x_power = np.zeros(shape)
    x_power[df['cell_x'], df['cell_y']] = df['average_power']
    
    x_mask = np.zeros(shape)
    x_mask[df['cell_x'], df['cell_y']] = 1

    x = np.array([x_power,x_mask])
    print("X shape: ", x.shape)

    y_ref_krigging = np.array([z])
    print("Y ref shape: ", y_ref_krigging.shape)

    y_mask = np.ones((1,shape[0],shape[1]))
    print("Y mask shape: ", y_mask.shape)

    return x, y_ref_krigging, y_mask

def write_formatted_matrixes_in_disk(x:np.ndarray, y:np.ndarray, y_mask:np.ndarray, fname:str):
    batch_x = np.array([x])
    batch_y = np.array([y])
    batch_y_mask = np.array([y_mask])
    with open(fname, 'wb') as f:
        pickle.dump((batch_x,batch_y,batch_y_mask), f)
    print(f"Wrote matrix into {fname}")
    print("----------------------------------------------")

def format_dataset_into_matrixes(dataset_name:str):
    DATASET_NAME = dataset_name # "tim_miguel_barra.csv"
    START_TIME = None
    STOP_TIME = None # Example: '2026.01.20_18.16.00'
    BLOCK_DIM = (32, 32)

    this_dir = os.path.dirname(__file__)
    dataset_path = os.path.join(this_dir,"../from_sensors",DATASET_NAME)
    
    matrix_path = os.path.join(this_dir,"../matrixes")
    os.makedirs(matrix_path, exist_ok=True)


    df = get_dataset(dataset_path, START_TIME, STOP_TIME)
    '''
    Loaded dataset with 989 rows:
        fonte operadora            timestamp   latitude  longitude geracao  FreqDL  FreqUL  larguraCanal  potencia  FreqDL_cel2  FreqUL_cel2  larguraCanal_cel2  potencia_cel2
    0  SigCap  Claro BR  2025.10.03_17.23.54 -22.886942 -43.283002     LTE  1855.0  1760.0            60     -84.0       2145.1       1955.1               60.0          -96.0
    1  SigCap  Claro BR  2025.10.03_17.24.04 -22.886859 -43.282905     LTE  1855.0  1760.0            60     -89.0       2145.1       1955.1               60.0          -92.0
    2  SigCap  Claro BR  2025.10.03_17.24.09 -22.886836 -43.283006     LTE  1855.0  1760.0            60     -90.0       2145.1       1955.1               60.0          -94.0
    3  SigCap  Claro BR  2025.10.03_17.24.19 -22.886687 -43.282952     LTE  1855.0  1760.0            60     -89.0       2145.1       1955.1               60.0          -84.0
    4  SigCap  Claro BR  2025.10.03_17.24.25 -22.886682 -43.282946     LTE  1855.0  1760.0            60     -85.0       2145.1       1955.1               60.0          -93.0
    ...
    ----------------------------------------------
    '''

    coords = CoordinatesBlocks(df, BLOCK_DIM[0], BLOCK_DIM[1])
    df = coords.transform_df(df)

    dl_freq = df["FreqDL"].value_counts().idxmax()
        
    channel = get_channel_df(df, dl_freq)

    df_one_channel = compute_average_power(channel["df"], coords)
    '''
    For DL frequency 1855.0: 122 rows in channel 1, 158 rows in channel 2
    ----------------------------------------------
    Computed average power:
        cell_x  cell_y  average_power
    0       0       7     -91.333333
    1       1       0     -84.000000
    2       1       2     -90.000000
    3       1       4     -86.666667
    4       1       5     -87.000000
    ...
    ----------------------------------------------
    '''

    z = krigging(df_one_channel, BLOCK_DIM)

    x,y,y_mask = transform_into_matrixes(df_one_channel,BLOCK_DIM,z)
    '''
    X shape:  (2, 32, 32)
    Y ref shape:  (32, 32)
    Y mask shape:  (32, 32)
    '''

    fname = os.path.join(matrix_path, f"{DATASET_NAME[:-4]}_{channel['dl']}_{channel['ul']}_{channel['bw']}.pickle" )
    write_formatted_matrixes_in_disk(x,y,y_mask,fname)
    return fname
