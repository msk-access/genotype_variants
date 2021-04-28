=================
genotype_variants
=================


.. image:: https://img.shields.io/pypi/v/genotype_variants.svg
        :target: https://pypi.python.org/pypi/genotype_variants

.. image:: https://img.shields.io/github/workflow/status/msk-access/genotype_variants/validate   
        :alt: GitHub Workflow Status

.. image:: https://readthedocs.org/projects/genotype-variants/badge/?version=latest
        :target: https://genotype-variants.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Project to genotype SNV, INDELS and SV.


* Free software: Apache Software License 2.0
* Documentation: https://genotype-variants.readthedocs.io.


Features
--------

Currently this module only supports genotyping and merging small variants (SNV and INDELS).

For this we have the following command line submodule called **small_variants**. 

Which have the following sub-commands:

* **generate**: To run GetBaseCountMultiSample on given BAM files
* **merge**: To merge MAF format files w.r.t counts generated from the `generate` command.
* **all**: This will run both of the sub-commands above `generate` and `merge` togather.
* **multiple-samples**: This will run sub-commands `all` for multiple samples in the provided metadata file

**Please read the USAGE** (https://genotype-variants.readthedocs.io/en/latest/usage.html) **section of the documentation for more information**

Requires GetBaseCountMultiSample v1.2.4 and above

To Do
-----

* Tagging genotyped files for thresholds
* Genotyping normal buffy coats
* Genotype structural variants calls


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
