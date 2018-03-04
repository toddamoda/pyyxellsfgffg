"""TBW."""


class Environment:
    """TBW."""

    def __init__(self,
                 temperature: float = None,
                 total_ionising_dose: float = None,
                 total_non_ionising_dose: float = None) -> None:
        """TBW.

        :param temperature:
        :param total_ionising_dose:
        :param total_non_ionising_dose:
        """
        self.temperature = temperature                              # unit: K
        self.total_ionising_dose = total_ionising_dose              # unit: ?  (Gray or MeV/g) todo
        self.total_non_ionising_dose = total_non_ionising_dose      # unit: ?  (Gray or MeV/g) todo

    def copy(self):
        """TBW."""
        return Environment(**self.__getstate__())

    def __getstate__(self):
        """TBW.

        :return:
        """
        return {'temperature': self.temperature,
                'total_ionising_dose': self.total_ionising_dose,
                'total_non_ionising_dose': self.total_non_ionising_dose}

    # TODO: create unittests for this method
    def __eq__(self, obj):
        """TBW.

        :param obj:
        :return:
        """
        assert isinstance(obj, Environment)
        return self.__getstate__() == obj.__getstate__()
