import numpy as np
import matplotlib.pyplot as plt
from pyxel.util.outputs import update_plot

ax_args = {
    'xlabel': 'signal (ADU)',
    'ylabel': 'noise (ADU)',
    'title': 'CCD Photon Transfer Curve',
    'axis': None,
    'grid': True,
    'xscale': 'log',
    'yscale': 'log',
    'xticks': None,
    'yticks': None,
    'xlim': [1., 2.e+6],
    'ylim': [1., 3.e+4]
}

run_dict = {
    'readout noise':        'run_01',
    'shot noise':           'run_02',
    'fixed pattern noise':  'run_03',
    'all with FWC':         'run_04'
}

x = np.load('run_01/x_parametric_01.npy')
for key, val in run_dict.items():

    y = np.load(val + '/y_parametric_01.npy')
    if key == 'all with FWC':
        plt.plot(x, y, label=key, marker='.', linestyle='', markersize=6)
    else:
        plt.plot(x, y, label=key, marker='.', linestyle='', markersize=4)
    update_plot(ax_args)
    plt.draw()

plt.legend()
plt.savefig('ptc')
plt.show()
