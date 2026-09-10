=======
History
=======

0.3.12 (2026-09-10)
------------------
* Fixed ``small_variants multiple-samples`` (and ``all``/``generate`` when only
  ``--sample-id`` is given): ``generate_gbcms_cmd`` called ``all([...])`` where
  ``all`` resolves to the module-level Click command, not the builtin, so the
  argument check ran Click's parser on a list and raised
  ``TypeError: object of type 'NoneType' has no len()``. Now calls
  ``builtins.all`` and requires *either* ``patient_id`` or ``sample_id``.

0.3.11 (2026-09-10)
------------------
* Fixed ``small_variants multiple-samples``: its internal call to the ``all``
  command was missing the ``sample_id`` and ``tumor_name_override`` arguments
  (and passed ``sample_id`` in the ``patient_id`` position), causing a
  ``TypeError`` on every run
* Added ``-to/--tumor_name_override`` passthrough to ``multiple-samples``

0.3.10 (2024-09-05)
------------------
* Migrated build system to pyproject.toml and GitHub Actions
* Updated supported Python version to 3.9+
* Added pre-commit configuration and CI integration
* Refactored Docker build and GBCMS command generation
* Added support for flexible sample ID handling
* Improved error handling for empty dataframes
* Updated documentation and configuration for Read the Docs

0.3.5 (2023-01-15)
------------------
* Added option to override tumor barcode
* Improved fragment column handling in MAF processing
* Enhanced logging for better debugging
* Made patient/sample ID handling more flexible
* Updated Dockerfile and dependencies

0.3.4 (2022-11-10)
------------------
* Added support for complex variants
* Fixed issues with GBCMS command generation
* Improved dataframe formatting and error handling

0.3.1 (2022-07-15)
------------------
* Added GitHub Actions workflow for CI/CD
* Improved error handling for empty dataframes
* Added better handling of missing columns in MAF files

0.3.0 (2020-04-10)
------------------
* Release with merge for standard BAM maf and Input MAF
* Converted multiple-patient to multiple-sample functionality

0.2.1 (2020-04-09)
------------------

* Release bug fixes, where simplex numbers are listed as duplex and vice versa, during running `all` command.

0.2.0 (2020-04-08)
------------------

* Release with multiple-patient command.

0.1.0 (2020-01-30)
------------------

* First release on PyPI.
