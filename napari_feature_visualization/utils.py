# Util functions for plugins
from functools import lru_cache
import pandas as pd
from enum import Enum
from napari._qt.dialogs.qt_notification import NapariQtNotification
from napari._qt.qt_event_loop import _ipython_has_eventloop
import warnings

@lru_cache(maxsize=16)
def get_df(path):
    return pd.read_csv(path)


def napari_warn(message):
    warnings.warn(message)
    if _ipython_has_eventloop():
        NapariQtNotification(message, 'WARNING').show()

def napari_info(message):
    print(message)
    if _ipython_has_eventloop():
        NapariQtNotification(message, 'INFO').show()


class ColormapChoices(Enum):
    viridis='viridis'
    plasma='plasma'
    inferno='inferno'
    magma='magma'
    cividis='cividis'
    Greys='Greys'
    Purples='Purples'
    Blues='Blues'
    Greens='Greens'
    Oranges='Oranges'
    Reds='Reds'
    YlOrBr='YlOrBr'
    YlOrRd='YlOrRd'
    OrRd='OrRd'
    PuRd='PuRd'
    RdPu='RdPu'
    BuPu='BuPu'
    GnBu='GnBu'
    PuBu='PuBu'
    YlGnBu='YlGnBu'
    PuBuGn='PuBuGn'
    BuGn='BuGn'
    YlGn='YlGn'
    PiYG='PiYG'
    PRGn='PRGn'
    BrBG='BrBG'
    PuOr='PuOr'
    RdGy='RdGy'
    RdBu='RdBu'
    RdYlBu='RdYlBu'
    RdYlGn='RdYlGn'
    Spectral='Spectral'
    coolwarm='coolwarm'
    bwr='bwr'
    seismic='seismic'
    turbo='turbo'
    jet='jet'
    tab10='tab10'
    tab20='tab20'
