# These tests are meant to make sure that the python<->julia interop is working
# correctly. They are not meant to test the correctness of Korg.jl, which this
# package wraps.

import numpy as np
from numpy.random.mtrand import f
import pytest

import korg


def test_builtin_linelists():
    korg.get_APOGEE_DR17_linelist()
    korg.get_GALAH_DR3_linelist()
    korg.get_VALD_solar_linelist()


def test_get_GES_linelist_parameters():
    # Test without molecules
    linelist2 = korg.get_GES_linelist(include_molecules=False)
    len_without = len(linelist2)

    # Test with molecules explicitly
    linelist3 = korg.get_GES_linelist(include_molecules=True)
    len_with = len(linelist3)

    assert len_without != len_with


def test_linelist_parsing():
    korg.read_linelist("tests/data/linelist.vald")


def test_ExoMol_loading():
    linelist = korg.load_ExoMol_linelist(
        "CaH",
        "tests/data/ExoMol/40Ca-1H__XAB_abridged.states",
        "tests/data/ExoMol/40Ca-1H__XAB_abridged.trans",
        6800,
        6810,
        line_strength_cutoff=-np.inf,  # don't filter anything out
    )
    assert len(linelist._lines) == 284


def test_air_vacuum():
    for f in [korg.air_to_vacuum, korg.vacuum_to_air]:
        assert isinstance(f(1000), float)
        assert isinstance(f(np.array([1000.0, 2000.0])), np.ndarray)


def test_air_vacuum_consistency():
    wavelengths = np.array([4000.0, 5000.0, 6000.0, 7000.0])

    # Test round-trip conversion
    vacuum_wls = korg.air_to_vacuum(wavelengths)
    air_wls = korg.vacuum_to_air(vacuum_wls)

    # Should be close to original (within numerical precision)
    np.testing.assert_allclose(wavelengths, air_wls, rtol=1e-10)

    # Vacuum wavelengths should be longer than air wavelengths
    assert np.all(vacuum_wls > wavelengths)


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


def test_synth_return_values():
    """Test that synth returns properly shaped arrays with reasonable values."""
    wls, flux, continuum = korg.synth(Teff=5777, logg=4.44, wavelengths=(5000, 5010))

    # Check return types and shapes
    assert isinstance(wls, np.ndarray)
    assert isinstance(flux, np.ndarray)
    assert isinstance(continuum, np.ndarray)
    assert wls.ndim == 1
    assert flux.ndim == 1
    assert continuum.ndim == 1
    assert len(wls) == len(flux) == len(continuum)

    # Check wavelength bounds
    assert wls[0] >= 5000
    assert wls[-1] <= 5010
    assert np.all(np.diff(wls) > 0)  # wavelengths should be increasing

    # Check flux and continuum values are reasonable (0-1 for rectified)
    assert np.all(flux >= 0)
    assert np.all(flux <= 1.001)  # allow small numerical tolerance
    assert np.all(continuum > 0)


def test_synth_parameters():
    """Test that all the synth parameters do something"""

    args = {"Teff": 5777, "logg": 4.44, "wavelengths": (5000, 5005)}
    _, flux_default, _ = korg.synth(**args)

    # custom linelist
    _, flux_GALAH, _ = korg.synth(**args, linelist=korg.get_GALAH_DR3_linelist())
    assert not np.array_equal(flux_default, flux_GALAH)

    _, flux_metal_poor, _ = korg.synth(M_H=-1.0, **args)
    assert not np.array_equal(flux_default, flux_metal_poor)

    _, flux_alpha, _ = korg.synth(alpha_H=0.4, **args)
    assert not np.array_equal(flux_default, flux_alpha)

    _, flux_C, _ = korg.synth(C=0.2, **args)
    assert not np.array_equal(flux_default, flux_C)

    _, unrect_flux, _ = korg.synth(rectify=False, **args)
    assert np.all(unrect_flux > 1)  # these should be big
    assert not np.array_equal(unrect_flux, flux_default)

    _, flux_rot, _ = korg.synth(vsini=10, **args)
    assert not np.array_equal(flux_rot, flux_default)

    _, flux_mic, _ = korg.synth(vmic=2.0, **args)
    assert not np.array_equal(flux_mic, flux_default)

    _, flux_mic, _ = korg.synth(R=10_000, **args)
    assert not np.array_equal(flux_mic, flux_default)


def test_synth_wavelength_formats():
    wls1, flux1, _ = korg.synth(Teff=5777, logg=4.44, wavelengths=(5000, 5010))
    assert wls1[0] >= 5000 and wls1[-1] <= 5010

    # Multiple ranges - test that it accepts the format without error
    wls2, flux2, _ = korg.synth(
        Teff=5777, logg=4.44, wavelengths=[(5000, 5005), (5200, 5205, 0.03)]
    )
    # Check that all wavelengths are within the specified ranges
    assert np.all(wls2 >= 5000) and np.all(wls2 <= 5205)
    assert not np.any(np.logical_and(wls2 > 5005, wls2 < 5200))


def test_error_handling():
    """Test basic error handling."""
    # Test invalid file path for read_linelist
    with pytest.raises(Exception):  # Julia will throw some kind of exception
        korg.read_linelist("nonexistent_file.vald")

    # Test invalid temperature for synth
    with pytest.raises(Exception):
        korg.synth(Teff=-1000, logg=4.44)  # Negative temperature should fail
