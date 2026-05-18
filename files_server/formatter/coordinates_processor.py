import pandas as pd

class CoordinatesBlocks:
    def __init__(self, df:pd.DataFrame, num_blocks_x, num_blocks_y):
        self._set_corners(df)
        self._set_cells(num_blocks_x, num_blocks_y)

    def roi_aspect_ratio(self):
        width = self.long_max - self.long_min
        height = self.lat_max - self.lat_min
        return height/width
    
    def _set_corners(self, df:pd.DataFrame):
        lat_max = df['latitude'].max()
        lat_min = df['latitude'].min()
        long_max = df['longitude'].max()
        long_min = df['longitude'].min()

        d_long = long_max - long_min
        assert d_long > 0 
        d_lat = lat_max - lat_min
        assert d_lat > 0 

        self.lat_min = lat_min - d_lat*0.05
        self.lat_max = lat_max + d_lat*0.05
        self.long_min = long_min - d_long*0.05
        self.long_max = long_max + d_long*0.05

        self.d_lat = self.lat_max - self.lat_min
        self.d_long = self.long_max - self.long_min
    
    def _set_cells(self,num_blocks_x, num_blocks_y):
        self.num_cells_x = num_blocks_x
        self.num_cells_y = num_blocks_y
        
        self.cell_x_sixe = self.d_long/self.num_cells_x
        self.cell_y_sixe = self.d_lat/self.num_cells_y

    def map_center(self):
        return (self.lat_max+self.lat_min)/2, (self.long_max+self.long_min)/2

    def upper_left(self):
        return self.lat_max, self.long_min

    def bottom_right(self):
        return self.lat_min, self.long_max

    def cell_xy_to_cell_bottom_left(self,cell_x,cell_y):
        cell_x, cell_y = int(cell_x), int(cell_y)
        cell_lat_min = self.lat_min + self.cell_y_sixe * cell_y
        cell_long_min = self.long_min + self.cell_x_sixe * cell_x
        return (cell_lat_min, cell_long_min)

    def cell_xy_to_cell_upper_right(self,cell_x,cell_y):
        cell_x, cell_y = int(cell_x), int(cell_y)
        cell_lat_max = self.lat_min + self.cell_y_sixe * (cell_y+1)
        cell_long_max = self.long_min + self.cell_x_sixe * (cell_x+1)
        return (cell_lat_max, cell_long_max)

    def cell_xy_to_cell_center_lat_long(self, cell_x, cell_y):
        cell_x, cell_y = int(cell_x), int(cell_y)
        cell_lat_min, cell_long_min = self.cell_xy_to_cell_bottom_left(cell_x, cell_y)
        cell_lat_max, cell_long_max = self.cell_xy_to_cell_upper_right(cell_x, cell_y)
        return (cell_lat_min + cell_lat_max) / 2, (cell_long_min + cell_long_max) / 2

    def cell_lat_long_to_cell_xy(self, cell_lat, cell_long):
        x = (cell_long - self.long_min)/self.cell_x_sixe
        y = (cell_lat - self.lat_min)/self.cell_y_sixe
        return (int(x), int(y))
    
    def transform_df(self,df:pd.DataFrame):
        df['cell_y'] = ((df['latitude'] - self.lat_min) / self.cell_y_sixe).astype(int)
        df['cell_x'] = ((df['longitude'] - self.long_min) / self.cell_x_sixe).astype(int)
        return df

    def y_column_to_lat_column(self, serie:pd.Series):
        return self.lat_min + (serie+0.5)*self.cell_y_sixe
    
    def x_column_to_long_column(self, serie:pd.Series):
        return self.long_min + (serie+0.5)*self.cell_x_sixe
