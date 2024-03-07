from PIL import Image
import pandas as pd
import os 
import pickle
from time import time
t=time()

def reconstruct_wsi(filename, path_masked_patches, path_coords_df, full_image_size,formato):
    t0 = time()
    full_image = Image.new('RGB', full_image_size, (240,240,240))
    df = pd.read_parquet(path_coords_df)
    df = df[df.file == filename]
    files = sorted(os.listdir(path_masked_patches))
    
    for i, (_, row) in enumerate(df.iterrows()):
        patch = Image.open(os.path.join(path_masked_patches, files[i])) #leemos la mask 
        full_image.paste(patch, (row.x, row.y))         #pegamos sobre fondo 

    match formato:
        case "webp":
            full_image.save(filename+'_masked.'+formato, lossless=True)
        case "tiff":
            full_image.save(filename+'_masked.'+formato, compression="tiff_deflate")
        case "jp2":
            full_image.save(filename+'_masked.'+formato, quality_mode='dB', quality_layers=[80])
    print(  'Saved as {} in {:.2f} sec'.format(formato, time()-t0)  )


with open('dims_per_filename.pkl', 'rb') as f:
    dims_per_file = pickle.load(f)


filename = 'I-2021-4001 A3'
path_masked_patches = os.path.join('/home/user/Documentos/WSI/temp', filename)
path_coords_df = '/home/user/Documentos/WSI/dataset/coords.parquet'
full_image_size = dims_per_file[filename]
formatos = ['webp', 'tiff', 'jp2']

for formato in formatos:
    reconstruct_wsi(filename, path_masked_patches, path_coords_df, full_image_size, formato)

print(  'Processed all in {:.2f} sec'.format(time()-t)  )