#  Copyright (c) European Space Agency, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Tools for jupyter notebook visualization."""

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Union

import numpy as np

from pyxel.data_structure import Persistence, SimplePersistence

if TYPE_CHECKING:
    import matplotlib.pyplot as plt
    import panel as pn
    import xarray as xr
    from hvplot.xarray import XArrayInteractive
    from panel.widgets import Widget

    from pyxel import Configuration
    from pyxel.detectors import Detector
    from pyxel.pipelines import DetectionPipeline, ModelFunction, Processor

# ----------------------------------------------------------------------------------------------
# Those two methods are used to display the contents of the configuration once loaded in pyxel


def display_config(configuration: "Configuration", only: str = "all") -> None:
    """Display configuration.

    Parameters
    ----------
    cfg: Configuration
    only: str
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    cfg: dict = configuration.__dict__
    for key in cfg:
        if cfg[key] is None:
            pass
        elif (only not in cfg) & (only != "all"):
            error = "Config file only contains following keys: " + str(list(cfg))
            display(Markdown(f"<font color=red> {error} </font>"))
            break
        elif (only == key) & (only != "all"):
            display(Markdown(f"## <font color=blue> {key} </font>"))
            display(Markdown("\t" + str(cfg[key])))
            if isinstance(cfg[key].__dict__, dict):
                display_dict(cfg[key].__dict__)
        elif only == "all":
            display(Markdown(f"## <font color=blue> {key} </font>"))
            display(Markdown("\t" + str(cfg[key])))
            if isinstance(cfg[key].__dict__, dict):
                display_dict(cfg[key].__dict__)


def display_dict(cfg: dict) -> None:
    """Display configuration dictionary.

    Parameters
    ----------
    cfg: dict
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    for key in cfg:
        display(Markdown(f"#### <font color=#0088FF> {key} </font>"))
        display(Markdown("\t" + str(cfg[key])))


# ----------------------------------------------------------------------------------------------
# This method will display the parameters of a specific model


def display_model(configuration: "Configuration", model_name: str) -> None:
    """Display model from configuration dictionary or Processor object.

    Parameters
    ----------
    pipeline_container: Processor or dict
    model_name: str
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    pipeline: DetectionPipeline = configuration.pipeline
    model: ModelFunction = pipeline.get_model(name=model_name)
    display(Markdown(f"## <font color=blue> {model_name} </font>"))
    display(Markdown(f"Model {model_name} enabled? {model.enabled}"))
    display_dict(dict(model.arguments))


def change_modelparam(
    processor: "Processor", model_name: str, argument: str, changed_value: Any
) -> None:
    """Change model parameter.

    Parameters
    ----------
    processor: Processor
    model_name: str
    argument:str
    changed_value
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    display(Markdown(f"## <font color=blue> {model_name} </font>"))
    model: ModelFunction = processor.pipeline.get_model(name=model_name)
    model.arguments[argument] = changed_value
    display(Markdown(f"Changed {argument} to {changed_value}."))


def set_modelstate(processor: "Processor", model_name: str, state: bool = True) -> None:
    """Change model state (true/false).

    Parameters
    ----------
    processor: Processor
    model_name: str
    state: bool
    """
    # Late import to speedup start-up time
    from IPython.display import Markdown, display

    display(Markdown(f"## <font color=blue> {model_name} </font>"))
    model: ModelFunction = processor.pipeline.get_model(name=model_name)
    model.enabled = state
    display(Markdown(f"Model {model_name} enabled? {model.enabled}"))


# ----------------------------------------------------------------------------------------------
# These method are used to display the detector object (all of the array Photon, pixel, signal and image)


def display_detector(detector: "Detector") -> "pn.Tabs":
    """Display detector interactively.

    Parameters
    ----------
    detector: Detector

    Returns
    -------
    Tabs
    """
    # Late import to speedup start-up time
    import hvplot.xarray  # To integrate 'hvplot' with 'xarray' # noqa
    import panel as pn
    import param

    # Extract a 'dataset' from 'detector'
    ds: "xr.Dataset" = detector.to_xarray()

    # Extract names from the arrays
    array_names: list[str] = [str(name) for name in ds]
    if not array_names:
        raise ValueError("Detector object does not contain any arrays.")

    first_array_name = array_names[0]

    # Create widget 'Array'
    array_widget: Widget = pn.widgets.Select(name="Array", options=array_names)
    array_widget.value = first_array_name

    # Create widget 'Color'
    color_widget: Widget = pn.widgets.Select(
        name="Color", options=["gray", "viridis", "fire"]
    )

    # Create an interactive widget
    ds_interactive: XArrayInteractive = ds.interactive(loc="right")
    selected_data: XArrayInteractive = ds_interactive[array_widget]

    # Create widget 'Color bar'
    colorbar_widget: Widget = pn.widgets.ToggleGroup(
        name="Color bar",
        options=["linear", "log"],
        behavior="radio",
    )

    # Create interactive 2D imge 'Array'
    img: XArrayInteractive = selected_data.hvplot(
        title="Array",
        aspect="equal",
        cmap=color_widget,
        cnorm=colorbar_widget,
    )

    def update_tabs_widget(*events: param.parameterized.Event) -> None:
        for event in events:
            if event.name != "value":
                continue

            tab_widgets.insert(index=1, pane=("Array", img))
            _ = tab_widgets.pop(0)

    # See https://panel.holoviz.org/how_to/links/watchers.html
    colorbar_widget.param.watch(fn=update_tabs_widget, parameter_names="value")

    num_bins_widget: Widget = pn.widgets.DiscreteSlider(
        name="Num bins",
        options=[10, 20, 50, 100, 200],
        value=50,
    )

    def configure_range_slider(name: str) -> None:
        data_2d = ds[name]
        start, val_low, val_high, end = np.asarray(
            data_2d.quantile(q=[0.0, 0.5, 0.95, 1.0])
        )

        step = (end - start) / 1000.0

        hist_range_widget.start = start
        hist_range_widget.end = end
        hist_range_widget.step = step

        hist_range_widget.value = (val_low, val_high)

    hist_range_widget: Widget = pn.widgets.EditableRangeSlider(name="Range Slider")
    configure_range_slider(name=first_array_name)

    hist: XArrayInteractive = selected_data.hvplot.hist(
        aspect=1.0,
        bins=num_bins_widget,
        logx=False,
        logy=False,
        title="Histogram",
        bin_range=hist_range_widget,
    )

    def update_array_widget(*events: param.parameterized.Event) -> None:
        for event in events:
            if event.name != "value":
                continue

            configure_range_slider(name=event.new)

    # See https://panel.holoviz.org/how_to/links/watchers.html
    array_widget.param.watch(fn=update_array_widget, parameter_names="value")

    # hist_widget = pn.Row(pn.WidgetBox(array_name, num_bins, range_slider), hist)
    tab_widgets = pn.Tabs(
        ("Array", img),
        ("Histogram", hist),
        dynamic=True,
    )

    return tab_widgets


def display_array(
    data: np.ndarray,
    axes: tuple["plt.Axes", "plt.Axes"],
    **kwargs,
) -> None:
    """For a pair of axes, display the image on the first one, the histogram on the second.

    Parameters
    ----------
    data: ndarray
        A 2D np.array.
    axes: list
        A list of two axes in a figure.
    """
    # Late import to speedup start-up time
    import matplotlib.pyplot as plt
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    mini = np.nanpercentile(data, 1)
    maxi = np.nanpercentile(data, 99)
    im = axes[0].imshow(data, vmin=mini, vmax=maxi)
    axes[0].get_xaxis().set_visible(False)
    axes[0].get_yaxis().set_visible(False)
    divider = make_axes_locatable(axes[0])
    cax1 = divider.append_axes("left", size="5%", pad=0.05)
    axes[0].set_title(kwargs["label"])
    plt.colorbar(im, cax=cax1)
    cax1.yaxis.set_label_position("left")
    cax1.yaxis.set_ticks_position("left")
    if mini == maxi:
        bins: Union[int, Sequence] = 50
    else:
        bins = list(np.arange(start=mini, stop=maxi, step=(maxi - mini) / 50))

    axes[1].hist(data.flatten(), bins=bins, **kwargs)
    plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45)
    axes[1].legend(fontsize=12)
    axes[1].grid(True, alpha=0.5)


# def display_detector(
#     detector: "Detector", array: Union[None, Photon, Pixel, Signal, Image] = None
# ) -> None:
#     """Display detector.
#
#     Parameters
#     ----------
#     detector: Detector
#     array: str
#
#     Returns
#     -------
#     None
#     """
#     if array is not None:
#         fig, axes = plt.subplots(1, 2, figsize=(15, 6))
#         display_array(array.array, axes, label=str(array).split("<")[0])
#     else:
#         arrays = [detector.photon, detector.pixel, detector.signal, detector.image]
#
#         fig, axes = plt.subplots(len(arrays), 2, figsize=(15, 6 * len(arrays)))
#
#         for idx, data in enumerate(arrays):
#             display_array(data.array, axes[idx], label=str(data).split("<")[0])
#
#     plt.show()


# ----------------------------------------------------------------------------------------------
# These method are used to display the detector memory


def display_persist(persistence: Union[Persistence, SimplePersistence]) -> None:
    """Plot all trapped charges using the detector persistence.

    Parameters
    ----------
    persistence: Persistence or SimplePersistence
    """
    # Late import to speedup start-up time
    import matplotlib.pyplot as plt

    trapped_charges = persistence.trapped_charge_array

    fig, axes = plt.subplots(
        len(trapped_charges), 2, figsize=(10, 5 * len(trapped_charges))
    )

    if isinstance(persistence, SimplePersistence):
        labels = [
            f"Trap time constant: {persistence.trap_time_constants[i]}; trap density:"
            f" {persistence.trap_densities[i]}"
            for i in range(len(trapped_charges))
        ]

    elif isinstance(persistence, Persistence):
        labels = [
            f"Trap time constant: {persistence.trap_time_constants[i]}; "
            + f"trap proportion: {persistence.trap_proportions[i]}"
            for i in range(len(trapped_charges))
        ]
    else:
        raise TypeError(
            "Persistence or SimplePersistence expected for argument 'persistence'!"
        )

    for ax, trapmap, keyw in zip(axes, trapped_charges, labels):
        display_array(data=trapmap, axes=ax, label=keyw)


def display_scene(
    detector: "Detector", figsize: tuple[int, int] = (8, 6)
) -> "plt.Axes":
    """Display the scene contained of 'detector' and the size of the detector.

    Examples
    --------
    >>> import pyxel
    >>> pyxel.display_scene(detector)

    .. image:: _static/display_scene.jpg
    """
    import astropy.units as u
    import matplotlib.pyplot as plt

    scene: xr.Dataset = detector.scene.to_xarray()

    if not scene:
        raise ValueError("Scene not initialized in this detector")

    right_ascension_key = "right_ascension[deg]"
    declination_key = "declination[deg]"
    fov_radius_key = "fov_radius[deg]"

    if right_ascension_key not in scene.attrs:
        raise KeyError(f"Missing key {right_ascension_key!r} in the attributes.")

    if declination_key not in scene.attrs:
        raise KeyError(f"Missing key {declination_key!r} in the attributes.")

    if fov_radius_key not in scene.attrs:
        raise KeyError(f"Missing key {fov_radius_key!r} in the attributes.")

    # Extract parameters from 'scene'
    right_ascension = u.Quantity(scene.attrs[right_ascension_key], unit="deg")
    declination = u.Quantity(scene.attrs[declination_key], unit="deg")
    fov_radius_key = u.Quantity(scene.attrs[fov_radius_key], unit="deg")

    middle_point_x = right_ascension.to(u.arcsec)
    middle_point_y = declination.to(u.arcsec)

    # Extract parameters from 'detector'
    pixel_scale = u.Quantity(detector.geometry.pixel_scale, unit="arcsec/pixel")
    detector_row = u.Quantity(detector.geometry.row, unit="pixel")
    detector_col = u.Quantity(detector.geometry.col, unit="pixel")

    x_factor = detector_row * pixel_scale / 2
    y_factor = detector_col * pixel_scale / 2

    l_x = middle_point_x - x_factor
    r_x = middle_point_x + x_factor
    t_y = middle_point_y + y_factor
    b_y = middle_point_y - y_factor

    fig, ax = plt.subplots(figsize=figsize)
    scene.plot.scatter(x="x", y="y", hue="weight", marker="o", ax=ax)

    ax.set_title(
        f"Right ascension: {right_ascension:latex}, "
        f"declination: {declination:latex}, "
        f"fov: {fov_radius_key:latex}"
    )
    ax.hlines(y=t_y.value, xmin=l_x.value, xmax=r_x.value)
    ax.vlines(x=l_x.value, ymin=b_y.value, ymax=t_y.value)
    ax.hlines(y=b_y.value, xmin=l_x.value, xmax=r_x.value)
    ax.vlines(x=r_x.value, ymin=b_y.value, ymax=t_y.value)

    return ax
