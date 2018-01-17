from pyxel.detectors.ccd import CCD


def run_pipeline(cfg):

    ccd = cfg.ccd     # type: CCD

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
    steps = [] # ['diffusion']
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
    ccd.compute_signal()
    # TODO: Convert here the charge object list into a 2d signal array

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