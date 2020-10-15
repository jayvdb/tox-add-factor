"""Tox hook implementations."""
from __future__ import print_function

import os

import tox

try:
    from tox.reporter import warning
except ImportError:
    warning = lambda s: None

from .envlist import add_factors, AFTER, BEFORE


@tox.hookimpl
def tox_addoption(parser):
    """Add arguments."""
    parser.add_argument("--append-factor", type=str, nargs="+", help="Append a factor.")

    parser.add_argument(
        "--prepend-factor", type=str, nargs="+", help="Prepend a factor."
    )

    parser.add_argument(
        "--prepend-archraw-factor",
        action="store_true",
        help="Prepend raw CPU arch arch to factors, such as ia32, armv8_a, aarch64.",
    )

    parser.add_argument(
        "--prepend-cpuarch-factor",
        action="store_true",
        help="Prepend CPU arch to factors, such as x86_32, x86_64, arm_7, arm_8.",
    )

    parser.add_argument(
        "--prepend-ostype-factor",
        action="store_true",
        help="Prepend OS type to factors, such as linux, macos, windows.",
    )

    parser.add_argument(
        "--prepend-username-factor",
        action="store_true",
        help="Prepend username to factors.",
    )

    parser.add_argument(
        "--add-ci-factor",
        action="store_true",
        help="Add CI factors if environment variable is set, such as appveyor, travis or fallback ci.",
    )


@tox.hookimpl(trylast=True)
def tox_configure(config):
    """Check for the presence of the added options."""
    if config.option.prepend_archraw_factor:
        from cpuinfo.cpuinfo import DataSource  # noqa

        archraw_factor_name = DataSource.arch_string_raw.replace("-", "_").lower()
        if not config.option.prepend_factor:
            config.option.prepend_factor = [archraw_factor_name]
        else:
            config.option.prepend_factor.insert(0, archraw_factor_name)

    if config.option.prepend_cpuarch_factor:
        from cpuinfo.cpuinfo import _parse_arch, DataSource  # noqa

        try:
            arch, _ = _parse_arch(DataSource.arch_string_raw)
            arch = arch.lower()
            if not config.option.prepend_factor:
                config.option.prepend_factor = [arch]
            else:
                config.option.prepend_factor.insert(0, arch)
        except Exception:
            archraw_factor_name = DataSource.arch_string_raw.replace("-", "_").lower()
            warning(
                'cpuarch not available for archraw "{}"'.format(archraw_factor_name)
            )

    if config.option.prepend_ostype_factor:
        from osinfo.osinfo import _get_os_type  # noqa

        if not config.option.prepend_factor:
            config.option.prepend_factor = [_get_os_type().lower()]
        else:
            config.option.prepend_factor.insert(0, _get_os_type().lower())

    if config.option.add_ci_factor and "CI" in os.environ:
        extra_factor = None
        if "APPVEYOR" in os.environ or "TRAVIS" in os.environ:
            config.option.prepend_username_factor = True
        elif "CIRRUS_CI" in os.environ:
            extra_factor = "cirrusci"
        else:
            extra_factor = "ci"

        if extra_factor:
            if not config.option.append_factor:
                config.option.append_factor = [extra_factor]
            else:
                config.option.append_factor.insert(0, extra_factor)

    if config.option.prepend_username_factor:
        import getpass  # noqa

        username = getpass.getuser()
        if username:
            username = username.lower()

        if not config.option.prepend_factor:
            config.option.prepend_factor = [username]
        else:
            config.option.prepend_factor.insert(0, username)

    if config.option.prepend_factor:
        add_factors(config, config.option.prepend_factor, position=BEFORE)
    if config.option.append_factor:
        add_factors(config, config.option.append_factor, position=AFTER)
