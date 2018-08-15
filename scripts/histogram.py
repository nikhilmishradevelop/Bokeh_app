
import pandas as pd
import numpy as np
from bokeh.layouts import row, column, WidgetBox
from bokeh.io import output_file, show, curdoc
from bokeh.models.widgets import CheckboxGroup, RadioGroup,  Select, Slider, Tabs, Panel, RangeSlider
from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.palettes import Category20_16
from bokeh.plotting import figure


def histogram_tab(df):

    def make_dataset(select_cats_list, range_start=-60, range_end=120, bin_width=5):
        '''
        select_cats_list: To select categories from a specified category. Like select cats, birds from [cats, dogs and birds]
        '''
        # Dataframe to hold information
        hist_df = pd.DataFrame(columns=['proportion', 'left', 'right', 'f_interval',
                                        'name', 'color'])
        
        range_extent = range_end - range_start

        # Iterate through all the categories
        for i, cat_name in enumerate(select_cats_list):

            # Subset to the carrier
            cat_name = str(cat_name)
            selected_cat_series = df[select_by_cat.value]
            selected_cat_series = selected_cat_series.astype('str')
            #subset = df[df[select_by_cat.value] == cat_name]
            subset = df[selected_cat_series.isin([cat_name])]

            # Create a histogram with 5 minute bins
            arr_hist, edges = np.histogram(subset[select_cont.value], 
                                           bins=int(range_extent / bin_width), 
                                           range=[range_start, range_end])

            # Divide the counts by the total to get a proportion
            arr_df = pd.DataFrame({'proportion': arr_hist / np.sum(arr_hist), 'left': edges[:-1], 'right': edges[1:]})

            # Assign the carrier for labels
            arr_df['name'] = cat_name

            # Color each carrier differently
            arr_df['color'] = Category20_16[i]

            # Add to the overall dataframe
            hist_df = hist_df.append(arr_df)

        # Overall dataframe
        hist_df = hist_df.sort_values(['name', 'left'])

        return ColumnDataSource(hist_df)

    def style(p):
        # Title 
        p.title.align = 'center'
        p.title.text_font_size = '20pt'
        p.title.text_font = 'serif'

        # Axis titles
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.axis_label_text_font_style = 'bold'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.axis_label_text_font_style = 'bold'

        # Tick labels
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.major_label_text_font_size = '12pt'

        return p

    def make_plot(src):
        
        # Blank plot with correct labels
        p = figure(plot_width = 700, plot_height = 700, 
            title = 'Histogram of Arrival Delays by Airline',
            x_axis_label = 'Delay (min)', y_axis_label = 'Proportion')

        # Quad glyphs to create a histogram
        p.quad(source = src, bottom = 0, top = 'proportion', left = 'left', right = 'right',
               color = 'color', fill_alpha = 0.7, hover_fill_color = 'color', legend = 'name',
               hover_fill_alpha = 1.0, line_color = 'black')

        # Hover tool with vline mode
        hover = HoverTool(tooltips=[('Carrier', '@name'), 
                                    ('Delay', '@f_interval'),
                                    ('Proportion', '@f_proportion')],
                            mode='vline')

        p.add_tools(hover)

        # Styling
        p = style(p)

        return p

    cols_df = list(df.columns)
    by_cat_list = cols_df
    cont_cols_list = cols_df

    select_cont = Select(options=cont_cols_list, title='Select Numerical Column')
    select_by_cat = Select(options=by_cat_list, title='Select Categorical Column')

    checkbox_cats = CheckboxGroup()
    radio_plot_type = RadioGroup()

    ######################################################
    def update_cont_col(attr, old, new):
        p.title.text = 'Histogram of {}'.format(select_cont.value)
        p.xaxis.axis_label = select_cont.value
        range_select_max = df[select_cont.value].max()
        range_select_min = df[select_cont.value].min()
        range_select.start = range_select_min
        range_select.end = range_select_max
        range_select.value = (range_select_min, range_select_max)
    #########################################################
    def update(attr, old, new):
        carriers_to_plot = [checkbox_cats.labels[i] for i in checkbox_cats.active]

        new_src = make_dataset(carriers_to_plot,
                               range_start=range_select.value[0],
                               range_end=range_select.value[1],
                               bin_width=binwidth_select.value)
        
        src.data.update(new_src.data)



    #########################################################
    def modify_by_cat(attr, old, new):
        '''
        Change the checkboxes to reflect new category
        '''
        checkbox_labels = list(df[select_by_cat.value].value_counts().index)
        checkbox_labels = [str(c) for c in checkbox_labels]
        checkbox_cats.labels = checkbox_labels
    
    #########################################################
    def modify_cats(attr, old, new):
        '''
        Add or remove the cats in the checkboxes
        '''
        radio_plot_type.labels = ['Histogram', 'ECDF']
    ##########################################################
    optimal_bin_width = int(np.sqrt(len(df)))
    binwidth_select = Slider(start=optimal_bin_width-15, end=optimal_bin_width+15,
                             step=1, value=optimal_bin_width,
                             title='Bin Width (min)')
    
    range_select = RangeSlider(step=5, title='Range', start=1, end=10, value=(1, 10))

    ##########################################################
    select_cont.on_change('value', update_cont_col, update)
    checkbox_cats.on_change('active', modify_cats, update)
    select_by_cat.on_change('value', modify_by_cat, update)
    binwidth_select.on_change('value', update)
    range_select.on_change('value', update)
    #########################################################
    
    src = make_dataset(checkbox_cats.labels,
                       range_start=1,
                       range_end=10,
                       bin_width=binwidth_select.value)
    p = make_plot(src)
    p
    #####################################################

    controls = column(row(select_cont, select_by_cat), checkbox_cats, radio_plot_type, binwidth_select, range_select)
    layout = row(controls, p)
    tab = Panel(child=layout, title='Histogram')

    ##################################################

    return tab