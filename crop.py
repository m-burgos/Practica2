from openslide import OpenSlide, PROPERTY_NAME_MPP_X
from helpers import *
from time import time

pix = 512               #pixeles parches (cudarados)

in_path = 'WSI'         #path hacia la carpeta con los svs y los xml
out_path = 'dataset'    #path salida (dentro habrá 2 carpetas: patch & mask)
formato = '.png'        #formato para los mask&patch generados

check_dir(os.path.join(out_path, 'mask'))   #crea las carpetas donde guardaremos
check_dir(os.path.join(out_path, 'patch'))  #los patch&mask (en caso que no existan)

xml_files = filenames(in_path, 'xml')
svs_files = filenames(in_path, 'svs')
dic = get_all_vert(in_path)
patches_per_file = []
X, Y, i = [], [], 0

for svs, xml in zip(svs_files, xml_files):
    slide = OpenSlide(os.path.join(in_path, svs))
    pols =  dic[xml]
    wsi_mask = whole_mask(pols, slide.dimensions)
    svs_width, svs_height = slide.dimensions
    c = float(slide.properties.get(PROPERTY_NAME_MPP_X))
    t0 = time()
    patches_count = 0

    for y in range(0, svs_height, pix):
        for x in range(0, svs_width, pix):
            patch = slide.read_region((x, y), 0, (pix, pix)).convert('RGB')
            if not is_patch_blank(patch):
                mask = crop_mask(wsi_mask, (x,y), pix)
                xx, yy = wsi_coord(x,y,c)
                filename = f"{i:05d}_{xx}_{yy}"+formato
                mask.save(os.path.join(out_path, 'mask',filename))
                patch.save(os.path.join(out_path, 'patch',filename))
                patches_count += 1
                X.append(x), Y.append(y)
                i += 1

    patches_per_file.append(patches_count)
    print('{} cropped in {:.2f} min '.format(svs, (time()-t0)/60) )

print(f'len X: {len(X)}, len Y: {len(Y)}')
print('patches_per_file:', patches_per_file)
files = [xml[:-4] for xml in xml_files]
file_list = [fn for file, n in zip(files, patches_per_file) for fn in [file]*n]

import pandas as pd
df = pd.DataFrame({'file': file_list, 'x': X, 'y': Y})
df.to_parquet(os.path.join(out_path, 'coords.parquet'))