# p-winds

[![Documentation Status](https://readthedocs.org/projects/p-winds/badge/?version=latest)](https://p-winds.readthedocs.io/en/latest/?badge=latest) [![Build Status](https://travis-ci.com/ladsantos/p-winds.svg?branch=main)](https://travis-ci.com/ladsantos/p-winds) [![Coverage Status](https://coveralls.io/repos/github/ladsantos/p-winds/badge.svg?branch=main)](https://coveralls.io/github/ladsantos/p-winds?branch=main) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4551621.svg)](https://doi.org/10.5281/zenodo.4551621)

 Python implementation of Parker wind models for planetary atmospheres. **So many p's!** (Hence the name for the code.)

The main objective of this code is to produce simplified, 1-D models of the upper atmosphere of a planet, and perform radiative transfer to calculate observable spectral signatures. 

The scalable implementation of 1D models allows for atmospheric retrievals to calculate atmospheric escape rates and temperatures. In addition, the modular implementation allows for a smooth plugging-in of more complex descriptions to forward model their corresponding spectral signatures (e.g., self-consistent or 3D models).

A paper describing `p-winds` and its usage for research-grade astronomical applications is currently in preparation. In the meantime, if you use this code in your research, please consider citing it: [10.5281/zenodo.4551621](https://doi.org/10.5281/zenodo.4551621).

Background
----------
`p-winds` is largely based on the theoretical framework of [Oklopčić & Hirata (2018)](https://ui.adsabs.harvard.edu/abs/2018ApJ...855L..11O/abstract) and [Lampón et al. (2020)](https://ui.adsabs.harvard.edu/abs/2020A%26A...636A..13L/abstract), which themselves based their work on the stellar wind model of [Parker (1958)](https://ui.adsabs.harvard.edu/abs/1958ApJ...128..664P/abstract).

Installation
------------

You can install `p-winds` using [`conda-forge`](https://conda-forge.org), `pip`, or by compiling it from source.

### Option 1: Using `conda-forge` (stable version)

Simply run the following commands:
```angular2html
conda update conda
conda install -c conda-forge p-winds
```

### Option 2: Using `pip` (stable version)

Even easier:
```angular2html
pip install p-winds
```

### Option 3: Compile from source (development version)

First, clone the repository and then navigate to it:
```angular2html
git clone https://github.com/ladsantos/p-winds.git
cd p-winds
```

And then compile it from source:
```angular2html
python setup.py install
```

You can test the installation from source with ``pytest`` (you may need to
install ``pytest`` first):
```angular2html
pytest tests
```

Quickstart example
------------------
Check out a quickstart [Google Colab Notebook here](https://colab.research.google.com/drive/1mTh6_YEgCRl6DAKqnmRp2XMOW8CTCvm7?usp=sharing). A similar quickstart Jupyter notebook is also available inside the `docs/source/` folder.

Future features and known problems
--------
Check out the [open issues](https://github.com/ladsantos/p-winds/issues).