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

#   Small script to extract a Gaia events catalog from a folder containing all the fits


from pythagor.bench.lgarcia.TARS.lib import ccd_events_catalog as ccd_events_catalog
import numpy as np


#   Creation of a catalog from folder
CR_cat_Gaia = ccd_events_catalog.from_folder_to_cat("C:\\Users\Lionel Garcia\Documents\Gaia_Data_SIF", 3.853, objlim=1)

#   plot of electrons repartition histogram of the events catalog
CR_cat_Gaia.cat_histogram('all')



end = True