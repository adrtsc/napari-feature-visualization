from magicgui import magic_factory
from napari import Viewer
from magicgui import widgets
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from matplotlib.colors import ListedColormap
from .utils import get_df
from .classifier import Classifier

def _init_classifier(widget):
    def get_feature_choices(*args):
        try:
            df = get_df(widget.DataFrame.value)
            return list(df.columns)
        except IOError:
            return [""]

    # set feature and label_column "default choices"
    # to be a function that gets the column names of the
    # currently loaded dataframe
    widget.feature_selection._default_choices = get_feature_choices
    widget.label_column._default_choices = get_feature_choices

    @widget.DataFrame.changed.connect
    def update_df_columns(event):
        # event value will be the new path
        # get_df will give you the cached df
        # ...reset_choices() calls the "get_feature_choices" function above
        # to keep them updated with the current dataframe
        widget.feature_selection.reset_choices()
        widget.label_column.reset_choices()
        features = widget.label_column.choices
        if 'label' in features:
            widget.label_column.value = 'label'
        elif 'Label' in features:
            widget.label_column.value = 'Label'
        elif 'index' in features:
            widget.label_column.value = 'index'

#DataFrame = '/Users/joel/Dropbox/Joel/PelkmansLab/Code/napari-feature-visualization/napari_feature_visualization/test_df_3.csv',
@magic_factory(
        call_button="Initialize Classifier",
        feature_selection = {"choices": [""]},
        label_column = {"choices": [""]},
        widget_init=_init_classifier,
        )
def initialize_classifier(viewer: Viewer,
                      label_layer: "napari.layers.Labels",
                      DataFrame: Path,
                      classifier_name = 'test',
                      feature_selection='',
                      additional_features='',
                      label_column=''):
    # TODO: Major refactor: Create a class ClassifierWidget. Instead of passing all the info, have it in there. Plus, have good init function
    # TODO: Make feature selection a widget that allows multiple features to be selected, not just one
    # Something like this in QListWidget: https://stackoverflow.com/questions/4008649/qlistwidget-and-multiple-selection
    # See issue here: https://github.com/napari/magicgui/issues/229
    # TODO: Check that input features are numeric => do in classifier, deal with exception here
    training_features = [feature_selection]

    # Workaround: provide a text box to enter additional features separated by comma, parse them as well
    if additional_features:
        training_features += [x.strip() for x in additional_features.split(',')]

    site_df = get_df(DataFrame)
    site_df['path']=DataFrame
    index_columns=('path', label_column)
    site_df = site_df.set_index(list(index_columns))
    clf = Classifier(name=classifier_name, features=site_df, training_features=training_features, index_columns=index_columns)
    clf.save()

    # Create a selection & prediction layer
    # TODO: Handle state when those layers were already created. Replace them otherwise?
    # https://napari.org/guides/stable/magicgui.html#updating-an-existing-layer
    prediction_layer = viewer.add_labels(label_layer.data, name='prediction', opacity=1.0, scale=label_layer.scale)
    selection_layer = viewer.add_labels(label_layer.data, name='selection', opacity=1.0, scale=label_layer.scale)
    colordict = create_label_colormap(selection_layer, clf.train_data, 'train', DataFrame)
    create_label_colormap(prediction_layer, clf.predict_data, 'predict', DataFrame)
    viewer.layers.selection.clear()
    viewer.layers.selection.add(label_layer)

    widget = selector_widget(clf, label_layer, DataFrame, selection_layer, prediction_layer, viewer, colordict)

    # TODO: Add a warning if a classifier with this name already exists => shall it be overwritten? => Confirmation box

    # add widget to napari
    viewer.window.add_dock_widget(widget, area='right', name=classifier_name)


@magic_factory(
        call_button="Load Classifier",
        )
def load_classifier(viewer: Viewer,
                    label_layer: "napari.layers.Labels",
                    classifier_path: Path,
                    DataFrame: Path):
    # TODO: Refactor: Could this be integrated with the initialize widget, with optional inputs? Could be tricky
    # TODO: Make classifier path optional? If no path is added (empty path object?, None?), don't add data to the classifier, take the existing data?
    #       BUT: Needed for site identification atm => not possible to leave out
    # TODO: Add option to add new features to the classifier that were not added at initialization => unsure where to do this. Should it also be possible when initializing a classifier?
    # TODO: Add ability to see currently selected features
    # TODO: Ensure classifier path ends in .clf and DataFrame path ends in .csv
    # TODO: Can I take a guess for the dataframe path & name based on the filename of the site? Can I get the filename of the current site somehow? => probably not?
    classifier_name = classifier_path.stem

    with open(classifier_path, 'rb') as f:
        clf = pickle.loads(f.read())

    training_features = clf.training_features
    site_df = get_df(DataFrame)
    site_df['path']=DataFrame
    index_columns=clf.index_columns
    # Catches if new data frame doesn't contain the index columns
    assert(all([index_column in site_df.columns for index_column in index_columns]))
    # TODO: Notify the user why the classifier is not loaded
    site_df = site_df.set_index(list(index_columns))

    clf.add_data(site_df, training_features=training_features, index_columns=index_columns)
    clf.save()

    # Create a selection & prediction layer
    # TODO: Handle state when those layers were already created. Replace them otherwise?
    # https://napari.org/guides/stable/magicgui.html#updating-an-existing-layer
    prediction_layer = viewer.add_labels(label_layer.data, name='prediction', opacity=1.0, scale=label_layer.scale)
    selection_layer = viewer.add_labels(label_layer.data, name='selection', opacity=1.0, scale=label_layer.scale)
    colordict = create_label_colormap(selection_layer, clf.train_data, 'train', DataFrame)
    create_label_colormap(prediction_layer, clf.predict_data, 'predict', DataFrame)
    viewer.layers.selection.clear()
    viewer.layers.selection.add(label_layer)

    widget = selector_widget(clf, label_layer, DataFrame, selection_layer, prediction_layer, viewer, colordict)

    # add widget to napari
    viewer.window.add_dock_widget(widget, area='right', name=classifier_name)


def selector_widget(clf, label_layer, DataFrame, selection_layer, prediction_layer, viewer, colordict):
    # TODO: Define a minimum number of selections. Below that, show a warning (training-test split can be very weird otherwise, e.g all 1 class)
    # TODO: Generalize this. Instead of 0, 1, 2: Arbitrary class numbers. Ability to add classes & name them?
    choices = ['Deselect', 'Class 1', 'Class 2', 'Class 3', 'Class 4']
    selector = widgets.RadioButtons(choices=choices, label='Selection Class:')
    save_button = widgets.PushButton(value=True, text='Save Classifier')
    run_button = widgets.PushButton(value=True, text='Run Classifier')
    container = widgets.Container(widgets=[selector, save_button, run_button])
    # TODO: Add text field & button to save classifier output to disk

    @label_layer.mouse_drag_callbacks.append
    def toggle_label(label_layer, event):
        selection_layer.visible=True
        # Need to scale position that event.position returns by the label_layer scale.
        # If scale is (1, 1, 1), nothing changes
        # If scale is anything else, this makes the click still match the correct label
        scaled_position = tuple(pos / scale for pos, scale in zip(event.position, label_layer.scale))
        label = label_layer.get_value(scaled_position)
        #label = label_layer.get_value(event.position)
        # Check if background or foreground was clicked. If background was clicked, do nothing (background can't be assigned a class)
        if label == 0:
            pass
        else:
            # Check if the label exists in the current dataframe. Otherwise, do nothing
            if (DataFrame, label) in clf.train_data.index:
                # Assign name of class
                #clf.train_data.loc[(DataFrame, label)] = selector.value
                # Assign a numeric value to make it easier (colormap currently only supports this mode)
                clf.train_data.loc[(DataFrame, label)] = choices.index(selector.value)
                update_label_colormap(selection_layer, label, choices.index(selector.value), colordict)
            else:
                # TODO: Give feedback to the user that there is no data for a specific label object in the dataframe provided?
                pass

    @selector.changed.connect
    def change_choice(choice):
        selection_layer.visible=True
        #prediction_layer.visible=False
        viewer.layers.selection.clear()
        viewer.layers.selection.add(label_layer)

    @save_button.changed.connect
    def save_classifier(event):
        print('Saving classifier')
        clf.save()

    @run_button.changed.connect
    def run_classifier(event):
        print('Running classifier')
        clf.train()
        create_label_colormap(prediction_layer, clf.predict_data, 'predict', DataFrame)
        clf.save()
        selection_layer.visible=False
        prediction_layer.visible=True
        # TODO: Report classifier performance to the user?

    return container


def update_label_colormap(label_layer, label, new_class, colordict):
    # TODO: Profile this function => can I speed it up?
    # One idea for speed-up: Change to 2 functions. 1 for initial calculation, returns colordict.
    # New one for just updating a single label
    nb_classes = 4
    cmap = ListedColormap([(0.0, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (1.0, 0.0, 1.0, 1.0)])

    colordict[label] = cmap(new_class/nb_classes)
    label_layer.color = colordict


def create_label_colormap(label_layer, df, feature, DataFrame):
    # TODO: Profile this function => can I speed it up?
    nb_classes = 4
    cmap = ListedColormap([(0.0, 0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (1.0, 0.0, 1.0, 1.0)])
    color_dict = {}
    site_df = df[df.index.isin([DataFrame], level=0)]
    site_df.index = site_df.index.droplevel()
    colors = cmap(site_df[feature]/nb_classes)
    colordict = dict(zip(site_df.index, colors))
    label_layer.color = colordict
    return colordict
