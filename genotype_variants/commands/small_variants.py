import os
import sys
import logging
import time
import pathlib
import genotype_variants.run_cmd as run_cmd

try:
    import click
except ImportError as e:
    print(
        "small_variants: click is not installed, please install click as it is one of the requirements."
    )
    exit(1)
try:
    import click_log
except ImportError as e:
    print(
        "small_variants: click-log is not installed, please install click_log as it is one of the requirements."
    )
    exit(1)
try:
    import pandas as pd
except ImportError as e:
    print(
        "small_variants: pandas is not installed, please install pandas as it is one of the requirements."
    )
    exit(1)
"""
small_variants
~~~~~~~~~~~~~~~
:Description: console script for genotyping small variants
"""
"""
Created on January 29, 2020
Description: console script for genotyping small variants
@author: Ronak H Shah
"""
BASE_DIR = pathlib.Path("__file__").resolve().parent
# Making logging possible
logger = logging.getLogger("genotype_variants")
click_log.basic_config(logger)
click_log.ColorFormatter.colors["info"] = dict(fg="green")


@click.group()
def cli():
    """Sub-commands for genotyping small variants"""
    pass


@cli.command()
@click.option(
    "-i",
    "--input-maf",
    required=True,
    type=click.Path(exists=True),
    help="Full path to small variants input file in MAF format",
)
@click.option(
    "-r",
    "--reference-fasta",
    required=True,
    type=click.Path(exists=True),
    help="Full path to reference file in FASTA format",
)
@click.option(
    "-g",
    "--gbcms-path",
    required=True,
    type=click.Path(exists=True),
    help="Full path to GetBaseCountMultiSample executable with fragment support",
)
@click.option(
    "-p",
    "--patient-id",
    required=True,
    type=click.STRING,
    help="Alphanumeric string indicating patient identifier",
)
@click.option(
    "-b",
    "--standard-bam",
    required=False,
    type=click.Path(exists=True),
    help="Full path to standard bam file, Note: This option assumes that the .bai file is present at same location as the bam file",
)
@click.option(
    "-d",
    "--duplex-bam",
    required=False,
    type=click.Path(exists=True),
    help="Full path to duplex bam file, Note: This option assumes that the .bai file is present at same location as the bam file",
)
@click.option(
    "-s",
    "--simplex-bam",
    required=False,
    type=click.Path(exists=True),
    help="Full path to simplex bam file, Note: This option assumes that the .bai file is present at same location as the bam file",
)
@click_log.simple_verbosity_option(logger)
def generate(
    input_maf,
    reference_fasta,
    gbcms_path,
    patient_id,
    standard_bam,
    duplex_bam,
    simplex_bam,
):
    """Command that helps to generate genotyped MAF,
    the output file will be labelled with 
    patient identifier as prefix"""
    logger_output = pathlib.Path.cwd().joinpath("genotype_variants.log")
    fh = logging.FileHandler(logger_output)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info("====================================================")
    logger.info(">>> Running genotype_variants for small variants <<<")
    logger.info("====================================================")
    t1_start = time.perf_counter()
    t2_start = time.process_time()
    if standard_bam or duplex_bam or simplex_bam:
        pass
    else:
        logger.error(
            "Required to specify at-least one input BAM file option. Please refer to the README for more information"
        )
        exit(1)
    # Run GetBaseMultisampleCount for each available bam file
    if standard_bam:
        btype = "standard"
        (cmd, std_output_maf) = generate_gbcms_cmd(
            input_maf, btype, reference_fasta, gbcms_path, patient_id, standard_bam
        )
        exit_code = run_cmd(cmd)
    if duplex_bam:
        btype = "duplex"
        (cmd, duplex_output_maf) = generate_gbcms_cmd(
            input_maf, btype, reference_fasta, gbcms_path, patient_id, duplex_bam
        )
        exit_code = run_cmd(cmd)
    if simplex_bam:
        btype = "simplex"
        (cmd, simplex_output_maf) = generate_gbcms_cmd(
            input_maf, btype, reference_fasta, gbcms_path, patient_id, simplex_bam
        )
        exit_code = run_cmd(cmd)
    merge_maf(
        patient_id, input_maf, std_output_maf, duplex_output_maf, simplex_output_maf
    )
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")
    return


def generate_gbcms_cmd(input_maf, btype, reference_fasta, gbcms_path, patient_id, bam):
    sample_id = patient_id + "-" + btype
    output_maf = pathlib.Path.cwd().joinpath(sample_id + "_genotyped.maf")

    cmd = (
        str(gbcms_path)
        + " --bam "
        + sample_id
        + ":"
        + str(bam)
        + " --filter_duplicate 0"
        + " --fragment_count 1"
        + " --maf "
        + str(input_maf)
        + " --mapq 20"
        + " --omaf"
        + " --output "
        + str(output_maf)
        + " --fasta "
        + str(reference_fasta)
        + " --threads 1"
    )

    return (cmd, output_maf)


def merge_maf(
    patient_id, input_maf, std_output_maf, duplex_output_maf, simplex_output_maf
):
    pass

