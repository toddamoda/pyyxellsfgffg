import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np

orig = fits.getdata('Pleiades_HST.fits')
new = fits.getdata('output/run_04/image_01.fits')
prev = fits.getdata('output/run_03/image_01.fits')

diff = np.abs(new - orig)
diff[diff == 0.] = np.NAN
diff_log = np.log10(diff)

plt.figure()
plt.imshow(diff)
plt.colorbar()
plt.title('| I$_{pyxel}$ - I$_{original}$ |')
plt.savefig('diff.png')

plt.figure()
plt.imshow(diff_log)
plt.colorbar()
plt.title(r'log$_{10}$( | I$_{pyxel}$ - I$_{original}$ | )')
plt.savefig('diff_log.png')


diff2 = np.abs(new - prev)
diff2[diff2 == 0.] = np.NAN
diff2 = np.clip(diff2, a_min=100, a_max=None)
diff2_log = np.log10(diff2)

plt.figure()
plt.imshow(diff2)
plt.colorbar()
plt.title('| I$_{pyxel}$ - I$_{previous}$ |')
plt.savefig('rel_diff.png')

plt.figure()
plt.imshow(diff2_log)
plt.colorbar()
plt.title(r'log$_{10}$( | I$_{pyxel}$ - I$_{previous}$ | )')
plt.savefig('rel_diff_log.png')

plt.show()
