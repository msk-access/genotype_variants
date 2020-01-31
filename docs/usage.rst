=====
Usage
=====

To use genotype_variants in a project::

    import genotype_variants


To use `small_variants generate` via command line here are the options::

    help: 
    ------

    > genotype_variants small_variants generate --help
    Usage: genotype_variants small_variants generate [OPTIONS]

    Command that helps to generate genotyped MAF, the output file will be
    labelled with  patient identifier as prefix

    Options:
    -i, --input-maf PATH            Full path to small variants input file in
                                    MAF format  [required]
    -r, --reference-fasta PATH      Full path to reference file in FASTA format
                                    [required]
    -p, --patient-id TEXT           Alphanumeric string indicating patient
                                    identifier  [required]
    -b, --standard-bam PATH         Full path to standard bam file, Note: This
                                    option assumes that the .bai file is present
                                    at same location as the bam file
    -d, --duplex-bam PATH           Full path to duplex bam file, Note: This
                                    option assumes that the .bai file is present
                                    at same location as the bam file
    -s, --simplex-bam PATH          Full path to simplex bam file, Note: This
                                    option assumes that the .bai file is present
                                    at same location as the bam file
    -g, --gbcms-path PATH           Full path to GetBaseCountMultiSample
                                    executable with fragment support  [required]
    -fd, --filter-duplicate INTEGER
                                    Filter duplicate parameter for
                                    GetBaseCountMultiSample
    -fc, --fragment-count INTEGER   Fragment Count parameter for
                                    GetBaseCountMultiSample
    -mapq, --mapping-quality INTEGER
                                    Mapping quality for GetBaseCountMultiSample
    -t, --threads INTEGER           Number of threads to use for
                                    GetBaseCountMultiSample
    -v, --verbosity LVL             Either CRITICAL, ERROR, WARNING, INFO or
                                    DEBUG
    --help                          Show this message and exit.


.. code-block:: console 
    
    genotype_variants small_variants generate \
    -i /path/to/input_maf \
    -r /path/to/reference_fasta \
    -g /path/to/GetBaseCountsMultiSample \
    -p patient_id \
    -b standard_bam
    -d duplex_bam \
    -s simplex_bam 
