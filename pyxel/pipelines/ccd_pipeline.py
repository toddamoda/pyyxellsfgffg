from pyxel.detectors.ccd import CCDDetector


def run_pipeline(cfg):

    ccd = CCDDetector.from_ccd(cfg.ccd)     # type: CCDDetector

    # OPTICS
    # Stage 1: Apply the Optics model(s). only '.photons' is modified
    ccd.compute_photons()
    steps = ['shot_noise', 'ray_tracing', 'diffraction']
    for step in steps:
        func = cfg.optics.models.get(step)
        if func:
            ccd = func(ccd)

    # CHARGE GENERATION
    # calculate charges per pixel
    ccd.compute_charge()
    steps = ['fixed_pattern_noise', 'tars', 'xray', 'snowballs', 'darkcurrent', 'hotpixel']
    for step in steps:
        func = cfg.charge_generation.models.get(step)
        if func:
            ccd = func(ccd)

    # CHARGE COLLECTION
    steps = []
    for step in steps:
        func = cfg.charge_collection.models.get(step)
        if func:
            ccd = func(ccd)
    # limiting charges per pixel due to Full Well Capacity
    ccd.charge_excess()

    # CHARGE TRANSFER
    steps = []
    for step in steps:
        func = cfg.charge_transfer.models.get(step)
        if func:
            ccd = func(ccd)

    # CHARGE READOUT
    # Signal with shot and fix pattern noise
    ccd.compute_ccd_signal()
    steps = ['output_node_noise']
    for step in steps:
        func = cfg.charge_readout.models.get(step)
        if func:
            ccd = func(ccd)

    # READOUT ELECTRONICS
    ccd.compute_readout_signal()
    steps = []
    for step in steps:
        func = cfg.readout_electronics.models.get(step)
        if func:
            ccd = func(ccd)

    return ccd