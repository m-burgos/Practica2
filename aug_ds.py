from PIL import Image
import albumentations as A
import numpy as np
import os
from helpers import check_dir
from time import time

def generate_augmented_images(image_path, img): #img = 'patch' ó 'mask'
    image = Image.open(image_path) if img=='patch' else Image.open(image_path).convert('L')
    augs = [A.HorizontalFlip(p=1), A.VerticalFlip(p=1), A.Rotate(limit=[90, 90], p=1),
        A.Rotate(limit=[180, 180], p=1), A.Rotate(limit=[270, 270], p=1),]
    augmented_images = [aug(image=np.array(image))['image'] for aug in augs]
    return augmented_images

def do_aug_dataset(path_mask, path_patch, path_output):
    check_dir(os.path.join(path_output,'aug_masks'))
    check_dir(os.path.join(path_output,'aug_patches'))
    files = os.listdir(path_mask)
    t0 = time()
    for file in files:
        aug_masks = generate_augmented_images(os.path.join(path_mask,file), 'mask')
        aug_patchs = generate_augmented_images(os.path.join(path_patch,file), 'patch')
        for i, (aug_mask, aug_patch) in enumerate(zip(aug_masks, aug_patchs)):
            fn = f'{file[:-4]}_{i}.jpg'
            aug_mask = Image.fromarray(aug_mask)
            aug_mask.save(os.path.join(path_output,'aug_masks',fn))
            aug_patch = Image.fromarray(aug_patch)
            aug_patch.save(os.path.join(path_output,'aug_patches',fn))
            if (i+1)%200 == 0:
                print(f'{i/len(files)*100:.2f}% progressed | time elapsed: {(time()-t0):.2f} sec')
    
path_mask = '/home/user/Documentos/masking the tissue/dataset/mask'
path_patch = '/home/user/Documentos/masking the tissue/dataset/patch'
path_output = '/home/user/Documentos/masking the tissue/dataset'
do_aug_dataset(path_mask, path_patch, path_output)


#no mostró el print
#quizá es el .jpg -> guardó muy rápido...