from collections.abc import Iterable
from typing import Callable

from korg._python_interface import Array1dF64, KFloat, Linelist

from ._julia_import import Korgjl

type KorgFitParamsType = dict[str, KFloat] | dict[str, int] | dict[str, float]


def fit_spectrum(
    obs_wls: Array1dF64,
    obs_flux: Array1dF64,
    obs_err: Array1dF64,
    linelist: Linelist,
    initial_guesses: KorgFitParamsType,
    fixed_params: KorgFitParamsType = {},
    *,
    windows: Iterable[tuple[KFloat, KFloat]] | None = None,
    R: KFloat | None | Callable[[KFloat], KFloat] = None,
    wl_buffer: KFloat = 1.0,
    precision: KFloat = 1e-4,
    time_limit: KFloat = 10_000,
    adjust_continuum=False,
    **synthesis_kwargs,
):
    Korgjl.Fit.fit_spectrum(
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
