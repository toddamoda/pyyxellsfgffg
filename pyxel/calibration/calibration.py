"""TBW."""


class Calibration:
    """TBW.

    :return:
    """

    def __init__(self,
                 calibration_mode: str,
                 arguments: dict,
                 ) -> None:
        """TBW."""
        self.calibration_mode = calibration_mode
        self.args = arguments

        self.args['target_fit_range'] = slice(self.args['target_fit_range'][0], self.args['target_fit_range'][1])
        self.args['output_fit_range'] = slice(self.args['output_fit_range'][0], self.args['output_fit_range'][1])
