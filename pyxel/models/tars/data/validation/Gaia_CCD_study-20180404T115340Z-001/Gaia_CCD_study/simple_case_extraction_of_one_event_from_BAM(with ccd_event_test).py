#   --------------------------------------------------------------------------
#   Copyright 2016 SRE-F, ESA (European Space Agency)
#       Lionel Garcia <lionel_garcia@live.fr>
#
#   This is restricted software and is only to be used with permission
#   from the author, or from ESA.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#   THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#   --------------------------------------------------------------------------
#
# Fully documented
# Fully commented

#   Simple script to understand CRs extraction and events catalog creation
#   1st image is the original
#   Second image is the mask from L.A cosmic
#   Third image is from_image_to_cat extraction with structural_labelisation=False
#   Fourth image is from_image_to_cat extraction with structural_labelisation=True
#   Fifth image is the clean image by L.A cosmic

from pythagor.bench.lgarcia.TARS.lib import ccd_events_catalog as ccd_events_catalog
from pythagor.bench.lgarcia.TARS.lib import cosmics
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pyfits


def plot_comparison():
    """
    Small routine to plot all the extraction process
    """

    # visualisation of the extraction
    fig = plt.figure(facecolor='white', figsize=(8, 10))
    plt.style.use('ggplot')


    ax = plt.subplot(154)
    ax.set_xlabel('AC dimension (' + r'$\mu$' + ')', fontsize=10)
    ax.set_ylabel('AL dimension (' + r'$\mu$' + ')', fontsize=10)
    plt.imshow(array, cmap='Greys_r', interpolation='None', aspect='auto', vmin=np.mean(array), vmax=1600)
    plt.grid(b=False)

    for i in range(0, new_catalog.number_of_events):
        ax.add_patch(patches.Rectangle((new_catalog.events_positions_in_ccd[i][1] - 0.5, new_catalog.events_positions_in_ccd[i][0] - 0.5),
                                       new_catalog.events_dimensions[i][1], new_catalog.events_dimensions[i][0], fill=None, edgecolor='r', linewidth=1))

        ax.text(new_catalog.events_positions_in_ccd[i][1] - 1, new_catalog.events_positions_in_ccd[i][0] - 1,
                str(i), fontsize=12, color='red')


    ax0 = plt.subplot(152)
    ax0.set_xlabel('AC dimension (' + r'$\mu$' + ')', fontsize=10)
    ax0.set_ylabel('AL dimension (' + r'$\mu$' + ')', fontsize=10)
    plt.imshow(c.mask, cmap='Greys_r', interpolation='None', aspect='auto', vmin=0, vmax=1)
    plt.grid(b=False)


    ax1 = plt.subplot(153)
    ax1.set_xlabel('AC dimension (' + r'$\mu$' + ')', fontsize=10)
    ax1.set_ylabel('AL dimension (' + r'$\mu$' + ')', fontsize=10)
    plt.imshow(array, cmap='Greys_r', interpolation='None', aspect='auto', vmin=np.mean(array), vmax=1600)
    plt.grid(b=False)

    for i in range(0, new_catalog1.number_of_events):
        ax1.add_patch(patches.Rectangle((new_catalog1.events_positions_in_ccd[i][1] - 0.5, new_catalog1.events_positions_in_ccd[i][0] - 0.5),
                                       new_catalog1.events_dimensions[i][1], new_catalog1.events_dimensions[i][0],
                                       fill=None, edgecolor='r', linewidth=1))

    ax2 = plt.subplot(151)
    ax2.set_xlabel('AC dimension (' + r'$\mu$' + ')', fontsize=10)
    ax2.set_ylabel('AL dimension (' + r'$\mu$' + ')', fontsize=10)
    plt.imshow(array, cmap='Greys_r', interpolation='None', aspect='auto', vmin=np.mean(array), vmax=1600)
    plt.grid(b=False)

    ax2 = plt.subplot(155)
    ax2.set_xlabel('AC dimension (' + r'$\mu$' + ')', fontsize=10)
    ax2.set_ylabel('AL dimension (' + r'$\mu$' + ')', fontsize=10)
    plt.imshow(c.cleanarray, cmap='Greys_r', interpolation='None', aspect='auto', vmin=np.mean(array), vmax=1600)
    plt.grid(b=False)

    plt.show()


#   fits load
hdulist = pyfits.open("Your FITS file")

# image extraction
array = hdulist[0].data

# We take a little part of the image
array = array[100:700, 0:200]

# LA cosmic routine
c = cosmics.cosmicsimage(array, gain=3.853, readnoise=10.0, sigclip=5.0, sigfrac=0.3, objlim=1.0, verbose=False)

#   BAM Gaia CCD : objlim = 1.0
#   SM Gaia CCD : objlim= 7.0
#   for objlim definition see L.A. cosmic library

c.run(maxiter=4)

new_catalog = ccd_events_catalog.from_image_to_cat(array, c.mask, "CR_extraction", gain=3.853, local_mean=True, structural_labelisation=True)

new_catalog1 = ccd_events_catalog.from_image_to_cat(array, c.mask, "CR_extraction", gain=3.853, local_mean=False, structural_labelisation=False)

#   plotting
plot_comparison()

end = True
