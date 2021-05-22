"""
This module is an example of a barebones QWidget plugin for napari

It implements the ``napari_experimental_provide_dock_widget`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
from napari import Viewer
from magicgui import magic_factory
from napari.layers import Image
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from .utils import get_df, ColormapChoices


def _init(widget):
    
    @widget.DataFrame.changed.connect
    def update_df_columns(event):
        
        widget.df.value = get_df(widget.DataFrame.value)
        widget.feature.choices = list(widget.df.value.columns)
        widget.label_column.choices = list(widget.df.value.columns)
        widget.time_column.choices = list(widget.df.value.columns)
        features = widget.feature.choices
        
        if 'label' in features:
            widget.label_column.value = 'label'
        elif 'Label' in features:
            widget.label_column.value = 'Label'
        elif 'index' in features:
            widget.label_column.value = 'index'

        if 'time' in features:
            widget.time_column.value = 'time'
        elif 'Time' in features:
            widget.time_column.value = 'Time'
        elif 'timepoint' in features:
            widget.time_column.value = 'timepoint'
        elif 'Timepoint' in features:
            widget.time_column.value = 'Timepoint'
            

    @widget.feature.changed.connect
    def update_rescaling(event):
        df = get_df(widget.DataFrame.value)
        try:
            quantiles=(0.01, 0.99)
            widget.lower_contrast_limit.value = df[event.value].quantile(quantiles[0])
            widget.upper_contrast_limit.value = df[event.value].quantile(quantiles[1])
        except KeyError:
            # Don't update the limits if a feature name is entered that isn't in the dataframe
            pass
    
    
    @widget.call_button.changed.connect
    def apply_changes(event):
        
        full_df = widget.df.value
        
        if widget.timeseries.value:
            site_df = full_df.loc[
                full_df[widget.time_column.value] == widget.viewer.value.dims.current_step[0]]
        else:
            site_df = full_df
        
        site_df.loc[:, 'label'] = site_df[
            str(widget.label_column.value)].astype(int)
        # Check that there is one unique label for every entry in the dataframe
        # => It's a site dataframe, not one containing many different sites
        # TODO: How to feedback this issue to the user?
        assert len(site_df['label'].unique()) == len(site_df), 'A feature dataframe with non-unique labels was provided. The visualize_feature_on_label_layer function is not designed for this.'
        # Rescale feature between 0 & 1 to make a colormap
        site_df['feature_scaled'] = (
            (site_df[widget.feature.value] - widget.lower_contrast_limit.value) /
            (widget.upper_contrast_limit.value - widget.lower_contrast_limit.value)
        )
        # Cap the measurement between 0 & 1
        site_df.loc[site_df['feature_scaled'] < 0, 'feature_scaled'] = 0
        site_df.loc[site_df['feature_scaled'] > 1, 'feature_scaled'] = 1
    
        colors = plt.cm.get_cmap(widget.Colormap.value.value)(site_df['feature_scaled'])
    
        # Create an array where the index is the label value and the value is
        # the feature value
        properties_array = np.zeros(site_df['label'].max() + 1)
        properties_array[site_df['label']] = site_df[widget.feature.value]
        label_properties = {widget.feature.value: np.round(properties_array, decimals=2)}
    
        colormap = dict(zip(site_df['label'], colors))
        widget.label_layer.value.color = colormap
        try:
            widget.label_layer.value.properties = label_properties
        except UnboundLocalError:
            # If a napari version before 0.4.8 is used, this can't be displayed yet
            # This this thread on the bug: https://github.com/napari/napari/issues/2477
            print("Can't set label properties in napari versions < 0.4.8")
            
            
    @widget.timeseries.changed.connect
    def update_timeseries(event):
        if widget.timeseries.value:
            widget.time_column.visible = True
            widget.viewer.value.dims.events.disconnect
            widget.viewer.value.dims.events.connect(apply_changes)
        else:
            widget.time_column.visible = False
            widget.viewer.value.dims.events.disconnect
    

'''
def _init(widget):
    @widget.DataFrame.changed.connect
    def update_df_columns(event):
        # Implemented following inputs from Talley Lambert:
        # https://forum.image.sc/t/visualizing-feature-measurements-in-napari-using-colormaps-as-luts/51567/16
        # event value will be the new path
        # get_df will give you the cached df
        df = get_df(event.value)
        features = list(df.columns)
        widget.feature.choices = features
        widget.label_column.choices = features
        if 'label' in features:
            widget.label_column.value = 'label'
        elif 'Label' in features:
            widget.label_column.value = 'Label'
        elif 'index' in features:
            widget.label_column.value = 'index'


    @widget.feature.changed.connect
    def update_rescaling(event):
        df = get_df(widget.DataFrame.value)
        try:
            quantiles=(0.01, 0.99)
            widget.lower_contrast_limit.value = df[event.value].quantile(quantiles[0])
            widget.upper_contrast_limit.value = df[event.value].quantile(quantiles[1])
        except KeyError:
            # Don't update the limits if a feature name is entered that isn't in the dataframe
            pass
'''


# TODO: Set better limits for contrast_limits
@magic_factory(
        call_button="Apply Feature Colormap",
        layout='vertical',
        DataFrame={'mode': 'r'},
        lower_contrast_limit={"min": -100000000, "max": 100000000},
        upper_contrast_limit={"min": -100000000, "max": 100000000},
        feature = {"choices": [""]},
        label_column = {"choices": [""]},
        time_column = {"choices": [""], 'visible': False},
        widget_init=_init,
        )
def feature_vis(label_layer: "napari.layers.Labels",
                viewer: Viewer,
                DataFrame: pathlib.Path,
                feature = '',
                label_column = '',
                timeseries = False,
                time_column = '',
                Colormap=ColormapChoices.viridis,
                lower_contrast_limit: float = 100,
                upper_contrast_limit: float = 900,
                df=Image):
    
    pass
