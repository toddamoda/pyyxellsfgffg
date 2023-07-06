# Copyright (c) 2023 Alejandro Camazon Pinilla, University of Florida, ARRAKIHS Mission Consortium
#
# acamazon@ufl.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Smooth."""

# ignore that local variables are assigned but never used for now
# ruff: noqa: F841

import logging

import numpy as np
import scipy.spatial.ckdtree as spkd
from numba import jit, njit  # , prange
from tqdm import tqdm

_spline_kernels: dict = dict()


############################################################
def sph_smooth_mp(
    xyz,
    hsml_input,
    weight,
    grid,
    x_range,
    y_range,
    kernel,
    increase_softening=True,
    max_softening=None,
    nproc=4,
):
    import time

    t0 = time.time()
    from multiprocessing import Pool

    hsml = hsml_input.copy()

    npart = xyz.shape[0]
    assert len(weight) == npart
    assert len(hsml) == npart
    assert np.all(hsml > 0)

    ngrid = grid.shape

    x0 = x_range[0]
    x1 = y_range[0]
    f0 = (x_range[1] - x_range[0]) / float(ngrid[0])
    f1 = (y_range[1] - y_range[0]) / float(ngrid[1])

    assert f0 > 0
    assert f1 > 0

    # Fudge HSML to never be less than the grid spacing
    global_min_softening = min(f0, f1) * 0.5
    global_max_softening = hsml.max()  # Just FYI, no function
    logging.debug("Min softening = %r", global_min_softening)
    if increase_softening and np.any(hsml < global_min_softening):
        number_changed = int((hsml < global_min_softening).sum())
        min_hsml = np.min(hsml)
        hsml = np.maximum(hsml, global_min_softening)
        logging.debug("Warning: increased %r softening lengths", number_changed)

    logging.debug("Max softening = ", global_max_softening)
    if max_softening is not None:
        too_large = hsml > max_softening
        logging.warning(
            "%r of %r > max softening (%r)",
            too_large.sum(),
            len(hsml),
            max_softening,
        )
        hsml[too_large] = max_softening

    chunk_size = np.ceil(npart / nproc)

    # Create segments list
    logging.debug(
        "Spawning %d jobs for %d particles [%d s]", nproc, npart, time.time() - t0
    )

    # The problem here is the distribution of hsml; processes take very different times.
    # Ideally want to divide the work equally
    logging.debug("Starting hsml sort [%14.7f s]", time.time() - t0)
    s = np.argsort(hsml)
    logging.debug("Done hsml sort [%14.7f s]", time.time() - t0)

    jobs = []
    total_particles = 0
    for i in tqdm(range(0, nproc)):
        idx = s[i::nproc]

        # A = int(i*chunk_size)
        # B = int(min((i+1)*chunk_size,npart))

        jobs.append(
            [
                xyz[idx].copy(),
                hsml[idx].copy(),
                weight[idx].copy(),
                ngrid,
                kernel,
                x_range,
                y_range,
            ]
        )

        hmax = np.log10((hsml[idx]).max())
        hmin = np.log10((hsml[idx]).min())
        logging.debug(
            "[%d] %d particles (HSML range %7.2f to %7.2f)", i, len(idx), hmax, hmin
        )
        total_particles += len(idx)
        # print('[{:d}] {:d} particles ({:d} to {:d})'.format(i,B-A,A,B))
    logging.debug("%d particles total", total_particles)

    pool = Pool(nproc)
    try:
        pmap = pool.starmap(sph_smooth_unpacker, jobs)
        result = np.sum(pmap, axis=0)
    finally:
        pool.close()

    logging.debug("Done smoothing [%14.7f s]", time.time() - t0)
    return result


############################################################
def sph_smooth_unpacker(*args):
    """Smooth."""
    xyz, hsml, weight, shape, kernel, x_range, y_range = args
    return sph_smooth_worker(xyz, hsml, weight, shape, kernel, x_range, y_range)


############################################################
@jit(nopython=True)
def sph_smooth_worker(xyz, hsml, weight, shape, kernel, x_range, y_range):
    """Smooth."""
    local_grid = np.zeros(shape, dtype=np.float64)

    x0 = x_range[0]
    x1 = y_range[0]
    f0 = (x_range[1] - x_range[0]) / float(shape[0])
    f1 = (y_range[1] - y_range[0]) / float(shape[1])

    npart_local = xyz.shape[0]

    # kfac converts from pixel coordinates to (r/h)**2
    # kernel coordinates
    ntab = kernel.shape[0]
    kfac = (ntab - 1) / 4.0  # Had ntab-1 in JCH, correct!

    # For SPH smoothing in 2D. This is correct (e.g. Price 2010).
    # It comes from int(int(r*w(r) dr)dtheta) = 2*pi*int(r*w(r)dr)
    norm_factor = 10.0 / (7.0 * np.pi)

    for ipart in range(npart_local):
        # Range of grid cells covered by this particle
        imin0 = np.floor(((xyz[ipart, 0] - 2.0 * hsml[ipart]) - x0) / f0)
        imax0 = np.floor(((xyz[ipart, 0] + 2.0 * hsml[ipart]) - x0) / f0)

        imin1 = np.floor(((xyz[ipart, 1] - 2.0 * hsml[ipart]) - x1) / f1)
        imax1 = np.floor(((xyz[ipart, 1] + 2.0 * hsml[ipart]) - x1) / f1)

        # if ipart == 0:
        #    print('Particle 0')
        #    print('X coverage:',imin0,imax0)
        #    print('Y coverage:',imin1,imax1)

        # Account for grid boundaries
        i1 = int(max(imin0, 0))
        i2 = int(min(imax0, shape[0] - 1))
        j1 = int(max(imin1, 0))
        j2 = int(min(imax1, shape[1] - 1))

        # if ipart == 0:
        #    print('X coverage (after wrap):',i1,i2)
        #    print('Y coverage (after wrap):',j1,j2)

        # Kernel parameters
        invh = 1.0 / hsml[ipart]
        lookupfac = invh * invh * kfac

        # The normalization by norm_factor/h**2
        norm = norm_factor * (invh**2)

        for ii in range(i1, i2):
            dx2 = (x0 + (ii + 0.5) * f0 - xyz[ipart, 0]) ** 2

            for jj in range(j1, j2):
                dr2 = dx2 + (x1 + (jj + 0.5) * f1 - xyz[ipart, 1]) ** 2

                # Kernel entry of interest given by (r^2/h^2)*kfac
                itab = int(dr2 * lookupfac)
                if itab < ntab:
                    w = kernel[itab] * norm
                    local_grid[ii, jj] += weight[ipart] * w

    return local_grid


############################################################
@jit(nopython=True, parallel=True)
def sph_smooth(
    xyz, hsml, weight, grid, x_range, y_range, kernel, increase_softening=True
):
    """Smooth.

    Returns: density per unit area of input pixels.
    """
    npart = xyz.shape[0]
    assert len(weight) == npart
    assert len(hsml) == npart

    assert np.all(hsml > 0)

    ngrid = grid.shape

    x0 = x_range[0]
    x1 = y_range[0]
    f0 = (x_range[1] - x_range[0]) / float(ngrid[0])
    f1 = (y_range[1] - y_range[0]) / float(ngrid[1])

    assert f0 > 0
    assert f1 > 0

    # Fudge HSML to never be less than the grid spacing
    MIN_SOFTENING = min(f0, f1) * 0.5
    logging.info("Min softening = %r", MIN_SOFTENING)
    if increase_softening and np.any(hsml < MIN_SOFTENING):
        number_changed = int((hsml < MIN_SOFTENING).sum())
        min_hsml = np.min(hsml)
        hsml = np.maximum(hsml, MIN_SOFTENING)
        logging.warning("increased %r softening lengths", number_changed)

    # kfac converts from pixel coordinates to (r/h)**2
    # kernel coordinates
    ntab = kernel.shape[0]
    kfac = (ntab - 1) / 4.0  # Had ntab-1 in JCH, correct!

    # For SPH smoothing in 2D. This is correct (e.g. Price 2010).
    # It comes from int(int(r*w(r) dr)dtheta) = 2*pi*int(r*w(r)dr)
    norm_factor = 10.0 / (7.0 * np.pi)

    local_grid = np.zeros(grid.shape, dtype=np.float64)

    logging.info("Npart = %r", npart)
    logging.info("Starting smoothing loop...")
    for ipart in tqdm(range(npart)):
        # Range of grid cells covered by this particle
        imin0 = np.floor(((xyz[ipart, 0] - 2.0 * hsml[ipart]) - x0) / f0)
        imax0 = np.floor(((xyz[ipart, 0] + 2.0 * hsml[ipart]) - x0) / f0)

        imin1 = np.floor(((xyz[ipart, 1] - 2.0 * hsml[ipart]) - x1) / f1)
        imax1 = np.floor(((xyz[ipart, 1] + 2.0 * hsml[ipart]) - x1) / f1)

        # if ipart == 0:
        #    print('Particle 0')
        #    print('X coverage:',imin0,imax0)
        #    print('Y coverage:',imin1,imax1)

        # Account for grid boundaries
        i1 = int(max(imin0, 0))
        i2 = int(min(imax0, ngrid[0] - 1))
        j1 = int(max(imin1, 0))
        j2 = int(min(imax1, ngrid[1] - 1))

        # if ipart == 0:
        #    print('X coverage (after wrap):',i1,i2)
        #    print('Y coverage (after wrap):',j1,j2)

        # Kernel parameters
        invh = 1.0 / hsml[ipart]
        lookupfac = invh * invh * kfac

        # The normalization by norm_factor/h**2
        norm = norm_factor * (invh**2)

        # if ipart == 0:
        #    print('invh:',invh)
        #    print('norm:',norm)
        #    print('lookupfac:',lookupfac)

        w = 0.0
        debug_total_weight = 0
        debug_total_weight_outside = 0
        for ii in tqdm(range(i1, i2)):
            dx2 = (x0 + (ii + 0.5) * f0 - xyz[ipart, 0]) ** 2

            for jj in range(j1, j2):
                dr2 = dx2 + (x1 + (jj + 0.5) * f1 - xyz[ipart, 1]) ** 2

                # Kernel entry of interest given by (r^2/h^2)*kfac
                itab = int(dr2 * lookupfac)
                if itab < ntab:
                    w = kernel[itab] * norm
                    local_grid[ii, jj] += weight[ipart] * w
    logging.info("Done smoothing!")

    # Don't forget, grid contains densities, not masses
    return local_grid


############################################################
@njit(parallel=True)
def xsph_smooth(
    xyz, hsml, weight, grid, x_range, y_range, kernel, increase_softening=True
):
    """Smooth.

    Returns: density per unit area of input pixels.
    """
    npart = xyz.shape[0]
    assert len(weight) == npart
    assert len(hsml) == npart

    assert np.all(hsml > 0)

    ngrid = grid.shape

    x0 = x_range[0]
    x1 = y_range[0]
    f0 = (x_range[1] - x_range[0]) / float(ngrid[0])
    f1 = (y_range[1] - y_range[0]) / float(ngrid[1])

    assert f0 > 0
    assert f1 > 0

    # Fudge HSML to never be less than the grid spacing
    MIN_SOFTENING = min(f0, f1) * 0.5
    logging.info("MIN_SOFTENING: %r", MIN_SOFTENING)
    if increase_softening and np.any(hsml < MIN_SOFTENING):
        number_changed = int((hsml < MIN_SOFTENING).sum())
        min_hsml = np.min(hsml)
        hsml = np.maximum(hsml, MIN_SOFTENING)
        logging.warning("increased %r softening lengths", number_changed)

    # kfac converts from pixel coordinates to (r/h)**2
    # kernel coordinates
    ntab = kernel.shape[0]
    kfac = (ntab - 1) / 4.0  # Had ntab-1 in JCH, correct!

    # For SPH smoothing in 2D. This is correct (e.g. Price 2010).
    # It comes from int(int(r*w(r) dr)dtheta) = 2*pi*int(r*w(r)dr)
    norm_factor = 10.0 / (7.0 * np.pi)

    local_grid = np.zeros(grid.shape, dtype=np.float64)

    logging.info("Npart = %r", npart)
    logging.info("Starting loop...")

    # for ipart in prange(npart):

    i1 = 0
    i2 = 10
    j1 = 30
    j2 = 40
    for ii in range(i1, i2):
        for jj in range(j1, j2):
            local_grid[ii, jj] += 1.0

    return local_grid


############################################################
def tabulate_spline_kernel(ntab=1000):
    r"""Tabulate the smoothing kernel as a function of (r/h)**2.

    The kernel is a cubic spline, nonzero from 0 to 2h.
    To normalize correctly per particle,
    W(r,h) = (sigma/(\pi h^2))*w(r,h) where
        w(r,h) is the table returned by this function
        sigma is a dimension-dependent factor (10/7pi for 2d)
    """
    global _spline_kernels

    if ntab in _spline_kernels:
        return _spline_kernels[ntab]

    # Pixel coordinates are 0 to N-1
    x = np.arange(0, ntab)

    # Kernel coodinates s=(r/h)**2 from 0 to 4
    rh2 = 4.0 * x / (ntab - 1)  # APC: ntab-1 so ends at 1
    rh = np.sqrt(rh2)

    # The above is equivalent to:
    # rh = np.sqrt(np.linspace(0,4,len(x)))

    w = np.zeros(rh2.shape[0], dtype=np.float64)

    # First part: 0 <= r <= h (two expressions are the same)
    sel = rh <= 1.0
    # w[sel] = 1.0-(1.5*(rh[sel]**2))+0.75*(rh[sel]**3)
    w[sel] = 0.25 * ((2.0 - rh[sel]) ** 3) - (1 - rh[sel]) ** 3
    logging.info("new kernel")

    # Second part: h<r<=2h
    sel = np.logical_and(rh > 1, rh <= 2.0)
    w[sel] = 0.25 * ((2.0 - rh[sel]) ** 3)

    # Cache
    _spline_kernels[ntab] = w

    return w


############################################################
def get_smoothing_lengths(xyz, ngb=32, hmin=0.0, hmax=1.0e20, leafsize=20, n_jobs=1):
    """Compute smoothing lengths for a set of particles xyz.

    Does not include any handling of wrapping around periodic boundaries!
    """
    import time

    logging.debug("Building tree...")
    t0 = time.time()
    tree = spkd.cKDTree(xyz, leafsize)
    logging.debug("%14.7f s", time.time() - t0)

    # Get neighbours and distances for all particles
    # Note approximate nearest neighbours
    logging.debug("Searching tree...")
    t0 = time.time()
    r_nearest, ngb_index = tree.query(xyz, ngb + 1, eps=0.1, workers=n_jobs)
    logging.debug("%14.7f s", time.time() - t0)

    logging.debug("R min %r max %r", r_nearest.min(), r_nearest.max())

    del ngb_index

    # Calculate the smoothing lengths as half the root mean square
    # separation of the particles.
    t0 = time.time()
    hsml = 0.5 * np.sqrt(np.sum(r_nearest**2, dtype=np.float64, axis=1))
    logging.debug("%14.7f s", time.time() - t0)

    del r_nearest

    f_lt_min = (hsml < hmin).sum() / float(len(hsml))
    f_gt_max = (hsml > hmax).sum() / float(len(hsml))
    logging.debug("%5.1f%% < min", f_lt_min)
    logging.debug("%5.1f%% > max", f_gt_max)

    logging.debug("HSML min %10.3e (%10.3e)", hsml.min(), hmin)
    logging.debug("HSML med %10.3e", np.nanmedian(hsml))
    logging.debug("HSML max %10.3e (%10.3e)", hsml.max(), hmax)

    # Threshold the values
    np.maximum(hsml, hmin, hsml)
    np.minimum(hsml, hmax, hsml)

    return hsml


############################################################
def smooth_to_grid(xyz, hsml, weight, grid, **kwargs):
    """Smooth grid.

    Don't forget, grid contains densities, not masses.
    """
    ntab = kwargs.get("ntab", 1000)
    update_grid = kwargs.get("update_grid", False)
    x_range = kwargs.get("x_range", None)
    y_range = kwargs.get("y_range", None)
    nproc = kwargs.get("nproc", 4)
    max_softening = kwargs.get("max_softening", None)

    kfac = (ntab - 1) / 4.0  # Had ntab-1 in JCH, correct!
    ktab = tabulate_spline_kernel(ntab)

    if x_range is None:
        x_range = xyz[:, 0].min(), xyz[:, 0].max()

    if y_range is None:
        y_range = xyz[:, 1].min(), xyz[:, 1].max()

    if nproc == 1:
        lgrid = sph_smooth(
            xyz,
            hsml,
            weight,
            grid,
            x_range=np.array(x_range, dtype=np.float32),
            y_range=np.array(y_range, dtype=np.float32),
            kernel=ktab,
        )
    else:
        lgrid = sph_smooth_mp(
            xyz,
            hsml,
            weight,
            grid,
            x_range=np.array(x_range, dtype=np.float32),
            y_range=np.array(y_range, dtype=np.float32),
            kernel=ktab,
            nproc=nproc,
            max_softening=max_softening,
        )

    # Don't forget, grid contains densities, not masses
    return lgrid


############################################################
def make_demo_xyz(n):
    """Make a particle distribution consiting of two concentric rings."""
    n1 = int(n / 2)
    n2 = n - n1

    r1 = 25.0 + np.random.random(n1) * 2.0
    r2 = 50.0 + np.random.random(n2) * 2.0

    theta1 = np.random.random(n1) * np.pi * 2.0
    theta2 = np.random.random(n2) * np.pi * 2.0

    x1 = r1 * np.sin(theta1)
    x2 = r2 * np.sin(theta2)

    y1 = r1 * np.cos(theta1)
    y2 = r2 * np.cos(theta2)

    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    z = np.random.random(n1 + n2) * 50.0

    return np.vstack([x, y, z]).T


############################################################
# EXAMPLES
############################################################


############################################################
def example_usage(xyz: np.ndarray, mass: np.ndarray, gridx, gridy, hsml=None, **kwargs):
    """Smooth the density field represented by a set of particles onto a regular grid in projection.

    If smoothing lengths are not given, they are calculated
    from the particles themselves.

    Parameters
    ----------
    xyz   : an (N,3) array of coordinates for N points.
    mass  : an (N,) array of weights associated with each point.
    gridx : edges of bins in first dimension
    gridy : edges of bins in second dimension.
    hsml
    All units are those of xyz and mass.
    To plot the returned array with the expected orientation:
    imshow(mygrid.T,interpolation='nearest',extent=(gridx[0],gridx[-1],gridy[0],gridy[-1]),origin='lower')

    Optional keyword arguments:
    proj     : [0,1,2] which axis of xyz to project along
    grid_dim : a tuple (nx,ny) giving the number of points in the output grid (default 100x100).
    """
    proj = kwargs.get("proj", 0)
    hsml_min = kwargs.get("hsml_min", 0.1)
    hsml_max = kwargs.get("hsml_max", 1e9)
    smoothing_neighbours = kwargs.get("smoothing_neighbours", 32)

    # Projection
    proj_dict = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
    px, py = proj_dict[proj]

    # Compute hsml in the units of xyz
    npart = xyz.shape[0]
    logging.info("Computing HSML, %d particles", npart)

    # Minimum and maximum smoothing lengths are chosen by the user.
    if hsml is None:
        logging.info("Calculating smoothing lengths...")
        logging.info(
            "User specified softening range (physical Mpc) %e %e", hsml_min, hsml_max
        )
        hsml = get_smoothing_lengths(
            xyz, ngb=smoothing_neighbours, hmin=hsml_min, hmax=hsml_max
        )

    logging.info("HSML range %r, %r", np.min(hsml), np.max(hsml))

    # Create an array representing the output grid
    nbins_x = len(gridx)
    nbins_y = len(gridy)
    grid = np.zeros((nbins_x, nbins_y), dtype=np.float64)

    logging.info("Smoothing to grid..")
    h2d = smooth_to_grid(
        (xyz[:][:, [px, py]]),
        hsml,
        mass,
        grid,
        ntab=1000,
        dim=2,
        extent=((gridx[0], gridx[-1]), (gridy[0], gridy[-1])),
    )

    # Don't forget, returned grid contains densities, not masses
    return h2d
