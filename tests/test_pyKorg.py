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


def test_fit():
    obs_wls = np.array([5000.0, 5001.0, 5002.0])
    obs_flux = np.array([1.0, 1.1, 1.2])
    obs_err = np.array([0.1, 0.1, 0.1])
    linelist = korg.get_APOGEE_DR17_linelist()
    initial_guesses = {"Teff": 5000}
    fixed_params = {"logg": 4.0}

    korg.fit.fit_spectrum(
        obs_wls,
        obs_flux,
        obs_err,
        linelist,
        initial_guesses,
        fixed_params,
        R=100_000,
        time_limit=1.0,
        hydrogen_lines=False,  # forwarded to synthesis
    )
