from . import Processor


class CCDTransferFunction(Processor):

    def __init__(self, ccd, model):
        super(CCDTransferFunction, self).__init__()
        self.model = model
        self.ccd = ccd

    def __call__(self):
        # SHOT NOISE
        if self.model.shot_noise:
            self.ccd.p = self.model.add_shot_noise(self.ccd.p)

        # calculate charges per pixel
        self.ccd.compute_charge()

        # FIXED PATTERN NOISE
        if self.model.fix_pattern_noise:
            self.ccd.charge = self.model.add_fix_pattern_noise(self.ccd.charge, self.model.noise_file)

        # limiting charges per pixel due to Full Well Capacity
        self.ccd.charge_excess()

        # Signal with shot and fix pattern noise
        self.ccd.compute_signal()

        # READOUT NOISE
        if self.model.readout_noise:
            self.model.readout_sigma = 10.0
            self.ccd.signal = self.model.add_readout_noise(self.ccd.signal)

        return self.ccd.signal


    def test(self):
        ph_n = self.ccd.p  # 2d array
        if self.model.shot_noise:
            ph_n = self.model.add_shot_noise(ph_n)

        charge = ph_n * self.ccd.qe * self.ccd.eta



        # # SHOT NOISE
        # if self.model.shot_noise:
        #     self.ccd.p = self.model.add_shot_noise(self.ccd.p)

        # calculate charges per pixel
        self.ccd.compute_charge()

        # FIXED PATTERN NOISE
        if self.model.fix_pattern_noise:
            self.ccd.charge = self.model.add_fix_pattern_noise(self.ccd.charge, self.model.noise_file)

        # limiting charges per pixel due to Full Well Capacity
        self.ccd.charge_excess()

        # Signal with shot and fix pattern noise
        self.ccd.compute_signal()

        # READOUT NOISE
        if self.model.readout_noise:
            self.model.readout_sigma = 10.0
            self.ccd.signal = self.model.add_readout_noise(self.ccd.signal)

        return self.ccd.signal

