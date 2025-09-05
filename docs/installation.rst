.. highlight:: shell

============
Installation
============

Requirements
************

* **Python 3.9 or higher**
* **pandas** (https://pandas.pydata.org/)
* **click** (https://palletsprojects.com/p/click/)
* **click-log** (https://github.com/click-contrib/click-log)

Stable Release
--------------
To install the latest stable release, run:

.. code-block:: console

    $ pip install genotype_variants

This is the preferred method to install genotype_variants, as it will always install the most recent stable release.

For development or specific version installation:

.. code-block:: console

    $ pip install genotype_variants==0.3.10

Using pipx (Recommended for CLI tools)
--------------------------------------
For isolated installation of CLI applications, use pipx:

.. code-block:: console

    $ pipx install genotype_variants


From Source
-----------

For development or to get the latest features, you can install from source:

1. Clone the repository:

.. code-block:: console

    $ git clone https://github.com/msk-access/genotype_variants.git
    $ cd genotype_variants

2. Install in development mode with all dependencies:

.. code-block:: console

    $ pip install -e '.[dev]'

This will install the package in editable mode along with development dependencies.

Docker
------
A Docker image is available for easy deployment:

.. code-block:: console

    $ docker pull ghcr.io/msk-access/genotype_variants:latest
