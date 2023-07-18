#   Copyright (c) 2023, Florian MORIOUSEF, Vincent GOIFFON, Alexandre LE ROCH, Aubin ANTONSANTI
#  
#   This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#   is part of this Pyxel package. No part of the package, including
#   this file, may be copied, modified, propagated, or distributed except according to
#   the terms contained in the file ‘LICENCE.txt’.


"""Model to generate charge due to dark current induced by radiation"""

# The Dark Current Model description can be found in:
# A. Le Roch et al., "Radiation-Induced Leakage Current and Electric Field Enhancement in CMOS Image Sensor Sense Node Floating Diffusions," in IEEE Transactions on Nuclear Science, vol. 66, no. 3, pp. 616-624, March 2019, doi: 10.1109/TNS.2019.2892645.
# Jean-Marc Belloir, Vincent Goiffon, Cédric Virmontois, Mélanie Raine, Philippe Paillet, Olivier Duhamel, Marc Gaillardin, Romain Molina, Pierre Magnan, and Olivier Gilard, "Pixel pitch and particle energy influence on the dark current distribution of neutron irradiated CMOS image sensors," Opt. Express 24, 4299-4315 (2016)


import warnings
from typing import Optional
import numpy as np
from astropy import constants as const
import matplotlib.pyplot as plt

from pyxel.detectors import APD, Detector
from pyxel.util import set_random_seed


def Damage_Factors(
        AnnealingTime: float, EactDC: float, temperature: float, Kdark_Srour: float, gammaDark: float,
        DepletionVolume: float, Dd: float
) -> list:

    """Return Damage Factors calculation list [nuDark, muDark]
    
    muDark: mean number of interactions per pixel 
    
    Parameters
    ----------
    AnnealingTime : float
        Parameter annealing_time. Unit: s
    EactDC : float
        Activation Energy parameter. Unit: eV
    temperature :
        temperature parameter. Unit K
    Kdark_Srour :
        Kdark_Srour parameter. Unit e-/cm3/sec per MeV/g
    gammaDark : 
        gammaDark parameter. Unit 1/µm3/(TeV/g)       
    DepletionVolume : 
        DepletionVolume parameter. Unit µm3
    Dd : 
        Displacment dose parameter. Unit TeV/g

    Returns
    -------
    float
        Nudark. Unit: e-/s
    float 
        MuDark. Unit: no units
    """
    
    k = const.k_B.value
    
    q = const.e.value  
    
    # Linear fit of Srour & Lo annealing factor (TNS 2000) in the 10^4 - 5.10^6 s range
    AnnealingFactor = (-0.3965 * np.log10(AnnealingTime) + 3.5948)/1.3024 
    OperatingTemperatureCorrection = np.exp( (-EactDC*q/k/temperature) - (-EactDC*q/k/300) )
    Kdark = Kdark_Srour * AnnealingFactor * OperatingTemperatureCorrection / 1e4 ** 3 * 1e6
    nuDark = Kdark/gammaDark
    muDark = gammaDark * DepletionVolume * Dd # mean number of interactions per pixel
 
    return nuDark, muDark 


def DamageFactorsSilicon (AnnealingTime: float, temperature: float, DepletionVolume: float, Dd: float
) -> list: 
    
    """Return Damage Factors (for silicon device) calculation list [nuDark, muDark]
    
    based on: 
    Source: J. R. Srour and D. H. Lo, "Universal damage factor for radiation-induced dark current in silicon devices," in IEEE Transactions     xon Nuclear Science, vol. 47, no. 6, pp. 2451-2459, Dec. 2000, doi: 10.1109/23.903792.
    
    muDark: mean number of interactions per pixel 
    
    Parameters
    ----------
    annealingtime : float
        Parameter annealing_time. Unit: weeks
    temperature :
        Temperature parameter. Unit K       
    DepletionVolume : 
        DepletionVolume parameter. Unit µm3
    Dd : 
        Displacment dose parameter. Unit TeV/g

    Returns
    -------
    float
        Nudark. Unit: e-/s
    float 
        MuDark. Unit: no units
    """
    
    EactDC = 0.63 # eV
    Kdark_Srour = 1.9e5 # e-/cm3/sec per MeV/g
    gammaDark = 0.097179425484859/4100 # 1/µm3/(TeV/g) 
    AnnealingTime = AnnealingTime * 7 * 24 * 3600 # convert week --> sec
    
    return Damage_Factors(
            AnnealingTime = AnnealingTime, EactDC = EactDC, temperature = temperature, 
            Kdark_Srour = Kdark_Srour, gammaDark = gammaDark, DepletionVolume = DepletionVolume, 
            Dd = Dd
    ) 


def computeDarkCurrentInduced (
    NumberOfRows: float, 
    NumberOfColumns: float, 
    muDark: float,
    nuDark: float,
    IntegrationTime:float,
    ShotNoise: bool
) -> np.ndarray:
    
    """Return Dark Signal Frame 
    
    Parameters
    ----------
    NumberOfRows : float
        Parameter NumberOfRows. Unit: pixels (#)
    NumberOfColumns :
        NumberOfColumns parameter. Unit: pixels (#)     
    muDark : 
        mean number of interactions per pixel. Unit: no units
    nuDark : 
        nuDark parameter. Unit: e-/s
    IntegrationTime : 
        IntegrationTime parameter. Unit s
    ShotNoise : 
        Shotnoise: true for shotnoise

    Returns
    -------
    np.ndarray
        DarkCurrentFrame. Unit: e-
    """
    
    # Define the Dark Current Frame
    DarkCurrentFrame = np.zeros((NumberOfRows, NumberOfColumns)) # e-
    
    # Assign a number of interactions for each pixels of the frame
    InteractionsArray = np.random.poisson(muDark, size =(NumberOfRows, NumberOfColumns))
    
    for i in range(1,np.max(InteractionsArray)):
        
        temp = np.array(np.where(InteractionsArray==i)) # Index of pixels with i events
        temp = np.swapaxes(temp, 0, 1)
       
        temp_darkcurrent = np.random.exponential(scale = nuDark, size = (i,len(temp)) ) # e-/s

        if i>1:
            temp_darkcurrent = np.sum( temp_darkcurrent, axis = 0) # if one pixel has more than 1 interaction, sum darkcurrent contributions
        else: 
            temp_darkcurrent = np.reshape(temp_darkcurrent, (np.shape(temp_darkcurrent)[1]))
      
        for pixels in range(len(temp)):
            Row = temp[pixels][0]
            Column = temp[pixels][1]
            DarkCurrentFrame[Row, Column] = temp_darkcurrent[pixels] # assign dark current value to corresponding pixel, e-/s
            
    DarkSignalFrame = np.round(DarkCurrentFrame * IntegrationTime) # e-
    
    if ShotNoise: 
        DarkSignalFrame = np.random.poisson(DarkSignalFrame).astype(float)
    
    if np.isinf(DarkSignalFrame).any():
        warnings.warn(
            "Unphysical high value for dark current from fixed pattern noise distribution"
            " will result in inf values. Enable a FWC model to ensure a physical limit.",
            RuntimeWarning,
        )
    
    return DarkSignalFrame

def dark_current_induced(
    detector : Detector, 
    DepletionVolume: float,
    AnnealingTime: float,
    Dd: float,
    ShotNoise: bool,
    seed: Optional[int] = None,
) -> None:
    
    """Add induced dark current to the detector charge 
    
    Parameters
    ----------
    detector : Detector
        Pyxel detector object.    
    DepletionVolume : float
        DepletionVolume parameter. Unit µm3.
    IntegrationTime : float
        IntegrationTime parameter. Unit s.
    Annealingtime : float
        Parameter Annealing time. Unit: s
    Dd : float
        Displacment dose parameter. Unit TeV/g

    """
    geo = detector.geometry
    temperature = detector.environment.temperature
    nuDark, muDark = DamageFactorsSilicon (AnnealingTime, temperature, DepletionVolume, Dd)
    IntegrationTime = detector.time_step
    NumberOfRows, NumberOfColumns = geo.shape
    with set_random_seed(seed):
        DarkSignalFrame = computeDarkCurrentInduced(NumberOfRows, NumberOfColumns, muDark, nuDark, IntegrationTime, ShotNoise)
    detector.charge.add_charge_array(DarkSignalFrame)
    
    
    
    
    
    
    
    