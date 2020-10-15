"""Tox envlist manipulation."""
import os

try:
    from tox.reporter import warning
except ImportError:
    warning = lambda s: None

from tox.config import _split_env as split_env
from tox.config import ParseIni, SectionReader, testenvprefix

BEFORE = 1
AFTER = 2


class _ParseIniWrapper(ParseIni):
    def __init__(self, config, ini):
        self.config = config
        self._cfg = ini


def _filter_factors(name, factors):
    name_items = set(split_env(name))
    new_factors = []
    for factor in factors:
        if factor not in name_items:
            name_items.add(factor)
            new_factors.append(factor)
    return new_factors


def AFTER(name, factors):
    factors = _filter_factors(name, factors)
    return name + "-" + "-".join(factors)


def BEFORE(name, factors):
    factors = _filter_factors(name, factors)
    return "-".join(factors) + "-" + name


def _add_to_each(s, factors, position=AFTER):
    items = split_env(s)
    items = [position(item, factors) for item in items]
    return ",".join(items)


def add_factors(config, factors, position=AFTER):
    ini = config._cfg

    config_ini = _ParseIniWrapper(config, ini)

    for envname, envconfig in list(config.envconfigs.items()):
        newname = position(envname, factors)
        env_factors = envconfig.factors.copy()
        for factor in factors:
            env_factors.add(factor)
        reader = SectionReader(
            envname, ini, fallbacksections=["testenv"], factors=env_factors
        )
        reader.addsubstitutions(toxinidir=config.toxinidir, homedir=config.homedir)
        reader.addsubstitutions(toxworkdir=config.toxworkdir)
        reader.addsubstitutions(distdir=config.distdir)
        reader.addsubstitutions(distshare=config.distshare)
        if hasattr(config, "temp_dir"):
            reader.addsubstitutions(temp_dir=config.temp_dir)

        section = "{}{}".format(testenvprefix, envname)
        newenv = config_ini.make_envconfig(
            newname, section, reader._subs, config, replace=True
        )
        config.envconfigs[newname] = newenv

    # envlist
    if "TOXENV" in os.environ:
        os.environ["TOXENV"] = _add_to_each(os.environ["TOXENV"], factors, position)
    if config.option.env:
        config.option.env = [
            _add_to_each(item, factors, position) for item in config.option.env
        ]

    config.envlist = [position(item, factors) for item in config.envlist]
    if hasattr(config, "envlist_default"):
        config.envlist_default = [
            position(item, factors) for item in config.envlist_default
        ]
