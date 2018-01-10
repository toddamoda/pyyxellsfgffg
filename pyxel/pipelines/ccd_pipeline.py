from pyxel.detectors.ccd import CCDDetector


def run_pipeline(cfg):
    ccd = CCDDetector.from_ccd(cfg.ccd)     # type: CCDDetector

    # Stage 1: Apply the Optics model(s). only '.photons' is modified
    ccd.compute_photons()
    steps = ['shot_noise', 'ray_tracing', 'diffraction']
    for step in steps:
        func = cfg.optics.models.get(step)
        if func:
            ccd = func(ccd)

    # calculate charges per pixel
    ccd.compute_charge()
    steps = ['fixed_pattern_noise', 'tars', 'xray', 'snowballs', 'darkcurrent', 'hotpixel']
    for step in steps:
        func = cfg.charge_generation.models.get(step)
        if func:
            ccd = func(ccd)

    # limiting charges per pixel due to Full Well Capacity
    ccd.charge_excess()  # TODO: does this come after charge_collection
    steps = []
    for step in steps:
        func = cfg.charge_collection.models.get(step)
        if func:
            ccd = func(ccd)

    steps = []
    for step in steps:
        func = cfg.charge_transfer.models.get(step)
        if func:
            ccd = func(ccd)

    # Signal with shot and fix pattern noise
    ccd.compute_signal()
    steps = ['readout_noise']
    for step in steps:
        func = cfg.charge_readout.models.get(step)
        if func:
            ccd = func(ccd)

    return ccd