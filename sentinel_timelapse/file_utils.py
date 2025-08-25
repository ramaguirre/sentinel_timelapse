import os

def rename_clipped_files(rename_dic, folder='clipped_assets', prefix='ant_footprint_visual'):
    for name_in in [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.tif')]:
        new_date = rename_dic[name_in.split('_')[-1].split('.')[0]]
        name_out = os.path.join(folder, f'{prefix}_{new_date}.tif')
        os.rename(name_in, name_out)