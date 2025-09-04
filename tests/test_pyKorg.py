# These tests are meant to make sure that the python<->julia interop is working
# correctly. They are not meant to test the correctness of Korg.jl, which this
# package wraps.

import numpy as np

import korg


def test_linelists():
    korg.get_APOGEE_DR17_linelist()
    korg.get_GALAH_DR3_linelist()
    korg.get_GES_linelist(include_molecules=False)
    korg.get_VALD_solar_linelist()


def test_synth():
    korg.synth(Teff=5777, logg=4.44)


def test_air_vacuum():
    for f in [korg.air_to_vacuum, korg.vacuum_to_air]:
        assert isinstance(f(1000), float)
        assert isinstance(f(np.array([1000.0, 2000.0])), np.ndarray)
