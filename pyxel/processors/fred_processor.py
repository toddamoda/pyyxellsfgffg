import typing

class OPTICS_MODEL:
    pass



class ShotNoise(OPTICS_MODEL):

    def __init__(self):
        self._func = CCDNoiseGenerator().add_shot_noise

    @property
    def func(self) -> typing.Callable:
        return self._func



cfg_filename = 'settings.yaml'

obj = read_yaml_config(cfg_filename)
assert isinstance(obj, CCD_PIPELINE)

ccd_params = obj.ccd

# Create the CCD object
ccd = CCD(dict(obj.ccd))

# Start the CCD pipeline

# Apply Optics Model (if necessary)
if obj.optics:
    for cfg_optics in obj.optics.item():
        assert isinstance(cfg_optics, OPTICS_MODEL)

        params = cfg_optics.params      # type: dict
        func = cfg_optcs.func           # type: callable

        ccd.p = func(photons=self.ccd.p, **params)
        # ccd.p = cfg_optics.apply(photons=self.ccd.p, **params)


# Apply Charge Generation Model (if necessary)
params = obj.charge_generation
qe = params['qe']
eta = params['eta']

# calculate charges per pixel
ccd.compute_charge(**params)

if obj.charge_generation.extra_models:

# FIXED PATTERN NOISE
# if self.model.fix_pattern_noise:
#     self.ccd.charge = self.model.add_fix_pattern_noise(self.ccd.charge, self.model.noise_file)

