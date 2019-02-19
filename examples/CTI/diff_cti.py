import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np

orig = fits.getdata('input_data/cti_image/image_non_irradiated.fits')
out = fits.getdata('output/run_02_seed60336/image_01.fits')
target = fits.getdata('input_data/cti_image/image_irradiated.fits')

diff = np.abs(target - orig)
# diff[diff == 0.] = np.NAN
diff_log = np.log10(diff)

plt.figure()
plt.imshow(diff)
plt.colorbar()
plt.title('| I$_{target}$ - I$_{original}$ |')
plt.savefig('diff.png')

# plt.figure()
# plt.imshow(diff_log)
# plt.colorbar()
# plt.title(r'log$_{10}$( | I$_{pyxel}$ - I$_{original}$ | )')
# plt.savefig('diff_log.png')


diff2 = np.abs(out - target)
# diff2[diff2 == 0.] = np.NAN
# diff2 = np.clip(diff2, a_min=1000, a_max=None)
diff2_log = np.log10(diff2)

plt.figure()
plt.imshow(diff2)
plt.colorbar()
plt.title('| I$_{pyxel}$ - I$_{target}$ |')
plt.savefig('rel_diff.png')

# plt.figure()
# plt.imshow(diff2_log)
# plt.colorbar()
# plt.title(r'log$_{10}$( | I$_{pyxel}$ - I$_{previous}$ | )')
# plt.savefig('rel_diff_log.png')

plt.show()
