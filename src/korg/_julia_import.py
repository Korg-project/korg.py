"""
This module initializes juliacall and imports Korg if these tasks aren't already done
"""

import os
import sys
import warnings

# Check if JuliaCall is already loaded, and if so, warn the user
# about the relevant environment variables. If not loaded,
# set up sensible defaults.
if "juliacall" in sys.modules:
    handle_signals = os.environ.get("PYTHON_JULIACALL_HANDLE_SIGNALS")
    if handle_signals:
        handle_signals_msg = (
            f"Currently, PYTHON_JULIACALL_HANDLE_SIGNALS is set to '{handle_signals}'."
        )
    else:
        handle_signals_msg = "Currently, PYTHON_JULIACALL_HANDLE_SIGNALS is not set. "

    warnings.warn(
        "juliacall module already imported, so korg will not configure `PYTHON_JULIACALL_HANDLE_SIGNALS` or `PYTHON_JULIACALL_THREADS`."
        "You should set `PYTHON_JULIACALL_HANDLE_SIGNALS=yes` to avoid segfaults. "
        + handle_signals_msg
    )
else:
    # Required to avoid segfaults (https://juliapy.github.io/PythonCall.jl/dev/faq/)
    if os.environ.get("PYTHON_JULIACALL_HANDLE_SIGNALS", "yes") != "yes":
        warnings.warn(
            "PYTHON_JULIACALL_HANDLE_SIGNALS environment variable is set to something other than 'yes' or ''. "
            "You will experience segfaults if running with multithreading."
        )

    if os.environ.get("PYTHON_JULIACALL_THREADS", "auto") != "auto":
        warnings.warn(
            "PYTHON_JULIACALL_THREADS environment variable is set to something other than 'auto', "
            "so korg.py was not able to set it. You may wish to set it to `'auto'` for full use "
            "of your CPU."
        )

    # TODO: Remove these when juliapkg lets you specify this
    for k, default in (
        ("PYTHON_JULIACALL_HANDLE_SIGNALS", "yes"),
        ("PYTHON_JULIACALL_THREADS", "auto"),
        ("PYTHON_JULIACALL_OPTLEVEL", "3"),
    ):
        os.environ[k] = os.environ.get(k, default)


from juliacall import Main as jl  # type: ignore

jl_version = (jl.VERSION.major, jl.VERSION.minor, jl.VERSION.patch)

# Next, automatically load the juliacall extension if we're in a Jupyter notebook
autoload_extensions = os.environ.get("PYKORG_AUTOLOAD_EXTENSIONS")
if autoload_extensions is not None:
    os.environ["PYTHON_JULIACALL_AUTOLOAD_IPYTHON_EXTENSION"] = autoload_extensions

jl.seval("using Korg")
Korgjl = jl.Korg
