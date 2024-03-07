import os
import xml.etree.ElementTree as et
from PIL import Image, ImageDraw
import numpy as np

def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

#input: size (slide.dimensions) & pols (lista donde c/elemento es la lista de ptos de 1 poligono) -> output: mask (blanco & negro)
def whole_mask(pols, size):
    img = Image.new(size=size, color=0, mode='1')
    draw = ImageDraw.Draw(img)
    for pol in pols:
        draw.polygon(pol, fill=1)
    return img

#input: objeto Image (whole_mask) & (left, top) coordinates & dim (pixel) del parche -> output: img cropped
def crop_mask(img, point, pix):
    return  img.crop( (point[0], point[1], point[0]+pix, point[1]+pix) )

#input coordenadas en pixel -> retorna coordenadas en micro metro | c = [micro m / pixel]
def wsi_coord(x,y,c):
    #return int(round(x*c,0)), int(round(y*c,0))
    return str(int(round(x*c,0))), str(int(round(y*c,0))) #puesto que lo usamos solo para poner en el filename del parche

#verifica si más del percent% del parche está sobre threshold (blanco) ó si más del 20% es negro (menor 20 en grayscale)
'''
def is_patch_blank(patch, percent = 0.9, threshold = 200):
    #import numpy as np
    gray_patch = patch.convert('L')
    np_patch = np.array(gray_patch)
    #average_pixel_value = np.mean(np_patch)
    w_per_patch = sum(sum([p>threshold for p in np_patch]))/len(np_patch)**2 #white
    g_per_patch = sum(sum([p<50 for p in np_patch]))/len(np_patch)**2 #gray/black
    return True if (w_per_patch > percent) or (g_per_patch > 0.2) else False
'''

def count_zero_rows_columns(array): #numpy_array!
    zero_row_count = np.sum(np.all(array == 0, axis=1))
    zero_column_count = np.sum(np.all(array == 0, axis=0))
    return max(zero_row_count, zero_column_count)

#percent: desde que porcentaje se considera que un parche está en blanco
#threshold:  desde que valor (grayscale) es blanco un pixel
def is_patch_blank(patch, percent=0.6, threshold=200): 
    np_patch = np.array(patch.convert('L'))
    w_per_patch = np.sum((np_patch > threshold))/len(np_patch)**2 
    return (np.std(np_patch) < 25) or (count_zero_rows_columns(np_patch) > 10) or (w_per_patch > percent)
#std cambiado a 25

#retorna lista con TODOS los .xml ó .svs en <path>
def filenames(path, extension):
    if extension == 'svs':
        return sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) if f[-3:]=='svs'])
    elif extension == 'xml':
        return sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) if f[-3:]=='xml'])
    else:
        print('extension: svs ó xml !')

#retorna una lista donde cada elemento son las poligonales registradas en fn (filename)
def get_vert(fn):
    tree = et.parse(fn)
    root = tree.getroot()
    n,v = len(root[0][1]), []
    for i in range(1,n):
        x=root[0][1][i][1]
        v.append([(int(float(c.get('X'))), int( float( c.get('Y') ) )) for c in x])
    return v

# devuelve {filename: list(poligonales en filename)} para todo filename en <path>
def get_all_vert(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) if f[-3:]=='xml']
    return {f: get_vert(os.path.join(path,f)) for f in files}

def get_xy(data): #recibe [(x1,y2)...(xn,yn)] => devuelve [x1...xn], [y1...yn]
    return [p[0] for p in data], [p[1] for p in data]
