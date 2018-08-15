import pandas as pd
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from scripts.histogram import histogram_tab
import json

with open('config.json') as fp:
    config = json.load(fp)
    file_name = config['file_path']

df = pd.read_csv(file_name)

tab1 = histogram_tab(df)
tabs = Tabs(tabs=[tab1])
curdoc().add_root(tabs)
