from collections.abc import Iterable
from typing import Callable, NamedTuple

from korg._python_interface import Array1dF64, Array2dF64, KFloat, Linelist

from ._julia_import import Korgjl


class FitResult(NamedTuple):
    best_fit_params: dict[str, KFloat]
    obs_wl_mask: Array1dF64
    covariance: tuple[list[str], Array2dF64]
    trace: list[dict[str, KFloat]]


def fit_spectrum(
    obs_wls: Array1dF64,
    obs_flux: Array1dF64,
    obs_err: Array1dF64,
    linelist: Linelist,
    initial_guesses: dict[str, KFloat],
    fixed_params: dict[str, KFloat] = {},
    *,
    windows: Iterable[tuple[KFloat, KFloat]] | None = None,
    R: KFloat | None | Callable[[KFloat], KFloat] = None,
    wl_buffer: KFloat = 1.0,
    precision: KFloat = 1e-4,
    time_limit: KFloat = 10_000,
    adjust_continuum: bool = False,
    **synthesis_kwargs,
) -> FitResult:
    """Find the parameters and abundances that best match a rectified observed spectrum.

    Parameters
    ----------
    obs_wls
        the wavelengths of the observed spectrum in any format accepted by synthesize
        (see `Wavelengths <https://ajwheeler.github.io/Korg.jl/stable/Wavelengths/>`_)
    obs_flux
        the observed flux
    obs_err
        the uncertainty in the observed flux
    linelist
        the linelist to use for synthesis
    initial_guesses
        a dict containing initial guesses for the parameters to fit. See
        "Specifying parameters" below.
    fixed_params
        a dict containing parameters to hold fixed during fitting (default: empty).
        See "Specifying parameters" below.

    ``initial_guesses`` and ``fixed_params`` can also be specified as Dicts instead of NamedTuples, which is
    more convenient when calling Korg from python.

    Specifying parameters
    ---------------------

    Required parameters
    ^^^^^^^^^^^^^^^^^^^

    ``Teff`` and ``logg`` *must* be specified in either ``initial_guesses`` or ``fixed_params``.

    Optional Parameters
    ^^^^^^^^^^^^^^^^^^^

    These can be specified in either ``initial_guesses`` or ``fixed_params``, but if they are not default
    values are used.

    - ``M_H``: the metallicity of the star, in dex. Default: ``0.0``
    - ``alpha_H``: the alpha enhancement of the star, in dex. Default: ``M_H``. Note that, because of the
      parameter range supported by ``Korg.interpolate_marcs``, only values within ±1 of ``M_H``
      are supported.
    - ``vmic``: the microturbulence velocity, in km/s. Default: ``1.0``
    - ``vsini``: the projected rotational velocity of the star, in km/s. Default: ``0.0``.
      See ``Korg.apply_rotation`` for details.
    - ``epsilon``: the linear limb-darkening coefficient. Default: ``0.6``. Used for applying rotational
      broadening only. See ``Korg.apply_rotation`` for details.
    - Individual elements, e.g. ``Na``, specify the solar-relative ([X/H]) abundance of that element.

    Other Parameters
    ----------------
    R
        the resolution of the observed spectrum. This is required. It can be specified as a
        function of wavelength, in which case it will be evaluated at the observed wavelengths.
    windows
        a vector of wavelength pairs, each of which specifies a wavelength
        "window" to synthesize and contribute to the total χ². If not specified, the entire spectrum is
        used. Overlapping windows are automatically merged.
    adjust_continuum
        (default: ``false``) if true, adjust the continuum with the best-fit linear
        correction within each window, minimizing the chi-squared between data and model at every step
        of the optimization.
    wl_buffer
        the number of Å to add to each side of the synthesis range for each window.
    time_limit
        the maximum number of seconds to spend in the optimizer. (default: ``10_000``).
        The optimizer will only checks against the time limit after each step, so the actual wall time
        may exceed this limit.
    precision
        specifies the tolerance for the solver to accept a solution. The solver operates on
        transformed parameters, so ``precision`` doesn't translate straightforwardly to Teff, logg, etc, but
        the default value, ``1e-4``, provides a theoretical worst-case tolerance of about 0.15 K in ``Teff``,
        0.0002 in ``logg``, 0.0001 in ``M_H``, and 0.0004 in detailed abundances. In practice the precision
        achieved by the optimizer is about 10x bigger than this.
    **kwargs
        Any additional keyword arguments will be passed to `Korg.synthesize <https://ajwheeler.github.io/Korg.jl/stable/API/#Korg.synthesize>`_ when synthesizing the
        spectra for the fit.

    Returns
    -------
    FitResult
        A ``~FitResult`` with the following fields:
    """

    result = Korgjl.Fit.fit_spectrum(
        obs_wls,
        obs_flux,
        obs_err,
        linelist._lines,
        initial_guesses,
        fixed_params,
        windows=windows,
        R=R,
        wl_buffer=wl_buffer,
        precision=precision,
        time_limit=time_limit,
        adjust_continuum=adjust_continuum,
        **synthesis_kwargs,
    )

    return FitResult(
        result.best_fit_params,
        result.obs_wl_mask,
        result.covariance,
        result.trace,
    )
