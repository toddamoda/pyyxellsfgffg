
class Environment:

    def __init__(self,
                 temperature: float = None,
                 total_ionising_dose: float = None,
                 total_non_ionising_dose: float = None) -> None:

        self.temperature = temperature                              # unit: K
        self.total_ionising_dose = total_ionising_dose              # unit: ?  (Gray or MeV/g) todo
        self.total_non_ionising_dose = total_non_ionising_dose      # unit: ?  (Gray or MeV/g) todo

    def __getstate__(self):
        return {'temperature': self.temperature,
                'total_ionising_dose': self.total_ionising_dose,
                'total_non_ionising_dose': self.total_non_ionising_dose}

    # TODO: create unittests for this method
    def __eq__(self, obj):
        assert isinstance(obj, Environment)
        return self.__getstate__() == obj.__getstate__()
