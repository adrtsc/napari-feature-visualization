# -*- coding: utf-8 -*-
"""
Created on Thu May 13 06:13:09 2021

@author: Adria
"""
%gui qt5
import numpy as np
import pandas as pd
import napari
import napari_feature_visualization


shape = (3, 50, 50)
label_image = np.zeros(shape).astype('uint16')
label_image[0, 5:10, 5:10] = 1
label_image[0, 15:20, 5:10] = 2
label_image[0, 25:30, 5:10] = 3
label_image[0, 5:10, 15:20] = 4
label_image[0, 15:20, 15:20] = 5
label_image[0, 25:30, 15:20] = 6

label_image[1, 5:10, 5:10] = 1
label_image[1, 15:20, 5:10] = 2
label_image[1, 25:30, 5:10] = 3
label_image[1, 5:10, 15:20] = 4
label_image[1, 15:20, 15:20] = 5
label_image[1, 25:30, 15:20] = 6

label_image[2, 5:10, 5:10] = 1
label_image[2, 15:20, 5:10] = 2
label_image[2, 25:30, 5:10] = 3
label_image[2, 5:10, 15:20] = 4
label_image[2, 15:20, 15:20] = 5
label_image[2, 25:30, 15:20] = 6


# Dummy df for this test
d = {'label': [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6],
     'feature1': [100, 200, 300, 500, 900, 1001,
                  500, 800, 1300, 1500, 1900, 2001,
                  50, 20, 990, 20, 240, 100],
     'feature2': [2200, 2100, 2000, 1500, 1300, 1001,
                  200, 100, 500, 30, 1300, 5001,
                  20, 2440, 20, 20, 20, 100], 
     'timepoint': [0, 0, 0, 0, 0, 0,
                   1, 1, 1, 1, 1, 1,
                   2, 2, 2, 2, 2, 2]}

df = pd.DataFrame(data=d)
df.to_csv('test_df.csv', index=False)

viewer = napari.Viewer()
viewer.add_labels(label_image, name='labels')


