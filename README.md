# tox-add-factor

tox-add-factor allows addition of factors on the command line,
so that they can be used to select dependencies and commands.

Any factor can be added with `--prepend-factor` and `--append-factor`.
The added factors can be combined with the `-e` argument and
`TOXENV` environment variable.

## CI factors

The argument `add-ci-factor` will detect the CI from the list below and add
it as a factor or fallback to adding "ci":

- appveyor
- cirrusci
- travis

To always add a "ci" factor, use `--append-factor=ci`.

Many CI services use a username which are the name of the service name.
For those services, the `--prepend-username-factor` may be helpful.

## Platform factors

Three specific factors can be added to simplify selecting OS and arch:
The following example depends on `--prepend-ostype-factor`

```ini
[testenv:osdeps]
deps =
  linux: distro
  windows: jaraco.windows
commands =
  linux: distro --help
  windows: enver --help
```

The factor names are determined by https://github.com/workhorsy/py-osinfo
This may change in the future if
[distro issue 177](https://github.com/nir0s/distro/issues/177)
is ever fixed.

The factors `--prepend-cpuarch-factor` and `--prepend-archraw-factor`
are provided by https://github.com/workhorsy/py-cpuinfo .

The cpuarch factor currently only supports:

- x86_32
- x86_64
- arm_7
- arm_8
- ppc_64
- s390x

With the above two factors added, `deps` can contain
`windows-x86_32: M2CryptoWin32` (however that may not install due to its deps).

If tox is run on an arch not in that list, the cpuarch factor will be omitted
with a warning which provides the archraw factor name which can be used.  
