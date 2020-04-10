import os
import sys
import logging
import time
import pathlib
import subprocess
import numpy as np
import re
from genotype_variants.run_cmd import run_cmd
from genotype_variants.create_duplex_simplex_dataframe import (
    create_duplex_simplex_dataframe as cdsd,
)
from genotype_variants.create_all_maf_dataframe import create_all_maf_dataframe as camd

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
@coauthor: Maysun Hasan
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
@click.option(
    "-g",
    "--gbcms-path",
    required=True,
    type=click.Path(exists=True),
    help="Full path to GetBaseCountMultiSample executable with fragment support",
)
@click.option(
    "-fd",
    "--filter-duplicate",
    required=False,
    default=0,
    type=click.INT,
    help="Filter duplicate parameter for GetBaseCountMultiSample",
)
@click.option(
    "-fc",
    "--fragment-count",
    required=False,
    default=1,
    type=click.INT,
    help="Fragment Count parameter for GetBaseCountMultiSample",
)
@click.option(
    "-mapq",
    "--mapping-quality",
    required=False,
    default=20,
    type=click.INT,
    help="Mapping quality for GetBaseCountMultiSample",
)
@click.option(
    "-t",
    "--threads",
    required=False,
    default=1,
    type=click.INT,
    help="Number of threads to use for GetBaseCountMultiSample",
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
    filter_duplicate,
    fragment_count,
    mapping_quality,
    threads
):
    """Command that helps to generate genotyped MAF,
    the output file will be labelled with
    patient identifier as prefix"""
    pid = os.getpid()
    logger_file = "genotype_variants_" + str(pid) + ".log"
    logger_output = pathlib.Path.cwd().joinpath(logger_file)
    fh = logging.FileHandler(logger_output)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(
        "=========================================================================="
    )
    logger.info(
        ">>> Running genotype_variants for small variants to generate genotypes <<<"
    )
    logger.info(
        "=========================================================================="
    )
    t1_start = time.perf_counter()
    t2_start = time.process_time()
    if standard_bam or duplex_bam or simplex_bam:
        pass
    else:
        logger.error(
            "Required to specify at-least one input BAM file option. Please refer to the README for more information"
        )
        exit(1)

    logger.info("small_variants: Patient ID: %s", patient_id)
    logger.info("small_variants: Input MAF: %s", input_maf)
    logger.info("small_variants: Reference FASTA: %s", reference_fasta)
    if standard_bam:
        logger.info("small_variants: Standard BAM: %s", standard_bam)
    if duplex_bam:
        logger.info("small_variants: Duplex BAM: %s", duplex_bam)
    if simplex_bam:
        logger.info("small_variants: Simplex BAM: %s", simplex_bam)
    logger.info("small_variants: GetBaseCountMultiSample -> Path: %s", gbcms_path)
    logger.info(
        "small_variants: GetBaseCountMultiSample -> Filter Duplicate: %s",
        str(filter_duplicate),
    )
    logger.info(
        "small_variants: GetBaseCountMultiSample -> Fragment Count: %s",
        str(fragment_count),
    )
    logger.info(
        "small_variants: GetBaseCountMultiSample -> Mapping Quality: %s",
        str(mapping_quality),
    )
    logger.info("small_variants: GetBaseCountMultiSample -> Threads: %s", str(threads))

    # Run GetBaseMultisampleCount for each available bam file
    std_output_maf = None
    duplex_output_maf = None
    simplex_output_maf = None
    p1, p2, p3 = None, None, None
    if standard_bam:
        btype = "STANDARD"
        (cmd, std_output_maf) = generate_gbcms_cmd(
            input_maf,
            btype,
            reference_fasta,
            gbcms_path,
            patient_id,
            standard_bam,
            filter_duplicate,
            fragment_count,
            mapping_quality,
            threads,
        )
        p1 = run_cmd(cmd)
        logger.info(
            "small_variants: Done running gbcms on %s and data has been written to %s",
            standard_bam,
            std_output_maf,
        )

    if duplex_bam:
        btype = "DUPLEX"
        (cmd, duplex_output_maf) = generate_gbcms_cmd(
            input_maf,
            btype,
            reference_fasta,
            gbcms_path,
            patient_id,
            duplex_bam,
            filter_duplicate,
            fragment_count,
            mapping_quality,
            threads,
        )
        p2 = run_cmd(cmd)
        logger.info(
            "small_variants: Done running gbcms on %s and data has been written to %s",
            duplex_bam,
            duplex_output_maf,
        )

    if simplex_bam:
        btype = "SIMPLEX"
        (cmd, simplex_output_maf) = generate_gbcms_cmd(
            input_maf,
            btype,
            reference_fasta,
            gbcms_path,
            patient_id,
            simplex_bam,
            filter_duplicate,
            fragment_count,
            mapping_quality,
            threads,
        )
        p3 = run_cmd(cmd)
        logger.info(
            "small_variants: Done running gbcms on %s and data has been written to %s",
            simplex_bam,
            simplex_output_maf,
        )

    logger.info("small_variants: Completed processing based on the given instructions")

    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")
    return (std_output_maf, simplex_output_maf, duplex_output_maf)


def generate_gbcms_cmd(
    input_maf,
    btype,
    reference_fasta,
    gbcms_path,
    patient_id,
    bam,
    filter_duplicate,
    fragment_count,
    mapping_quality,
    threads,
):
    sample_id = patient_id + "-" + btype
    output_maf = pathlib.Path.cwd().joinpath(sample_id + "_genotyped.maf")

    cmd = (
        str(gbcms_path)
        + " --bam "
        + sample_id
        + ":"
        + str(bam)
        + " --filter_duplicate "
        + str(filter_duplicate)
        + " --fragment_count "
        + str(fragment_count)
        + " --maf "
        + str(input_maf)
        + " --maq "
        + str(mapping_quality)
        + " --omaf"
        + " --output "
        + str(output_maf)
        + " --fasta "
        + str(reference_fasta)
        + " --thread "
        + str(threads)
    )

    return (cmd, output_maf)


@cli.command()
@click.option(
    "-i",
    "--input-maf",
    required=False,
    type=click.Path(exists=True),
    help="Full path to small variants input file in MAF format used for input to GBCMS for generating genotypes",
)
@click.option(
    "-std",
    "--input-standard-maf",
    required=False,
    type=click.Path(exists=True),
    help="Full path to small variants input file in MAF format generated by GBCMS for standard_bam",
)
@click.option(
    "-d",
    "--input-duplex-maf",
    required=False,
    type=click.Path(exists=True),
    help="Full path to small variants input file in MAF format generated by GBCMS for duplex_bam",
)
@click.option(
    "-s",
    "--input-simplex-maf",
    required=False,
    type=click.Path(exists=True),
    help="Full path to small variants input file in MAF format generated by GBCMS for simplex_bam",
)
@click.option(
    "-p",
    "--patient-id",
    required=True,
    type=click.STRING,
    help="Alphanumeric string indicating patient identifier",
)
@click_log.simple_verbosity_option(logger)
def merge(
    patient_id, input_maf, input_standard_maf, input_duplex_maf, input_simplex_maf
):
    """ 
    Given original input MAF used as an input for GBCMS along with 
    GBCMS generated output MAF for standard_bam, duplex_bam or simplex bam, 
    Merge them into a single output MAF format. 
    If both duplex_bam and simplex_bam based MAF are provided
    the program will generate merged genotypes as well.
    The output file will be based on the give alphanumeric patient identifier as prefix.
    """
    pid = os.getpid()
    logger_file = "genotype_variants_" + str(pid) + ".log"
    logger_output = pathlib.Path.cwd().joinpath(logger_file)
    fh = logging.FileHandler(logger_output)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(
        "========================================================================"
    )
    logger.info(
        ">>> Running genotype_variants for small variants to merge MAF output <<<"
    )
    logger.info(
        "========================================================================"
    )
    t1_start = time.perf_counter()
    t2_start = time.process_time()

    number_of_variables = 0
    for status in (input_maf, input_standard_maf, input_duplex_maf, input_simplex_maf):
        if status:
            number_of_variables += 1
    if number_of_variables >= 2:
        pass
    else:
        logger.error(
            "genotype_variants:small_variants:merge:: At least two MAF input need to be provided for us to merge."
        )
        exit(1)
    o_maf, i_maf, d_maf, s_maf = None, None, None, None
    if input_maf:
        logger.info(
            "genotype_variants:small_variants:merge:: Original MAF -> %s", input_maf
        )
        o_maf = pd.read_csv(input_maf, sep="\t", header="infer", index_col=False)
    if input_standard_maf:
        logger.info(
            "genotype_variants:small_variants:merge:: STANDARD BAM MAF -> %s",
            input_standard_maf,
        )
        i_maf = pd.read_csv(input_standard_maf, sep="\t", header="infer", index_col=False)
    if input_duplex_maf:
        d_maf = pd.read_csv(input_duplex_maf, sep="\t", header="infer", index_col=False)
        logger.info(
            "genotype_variants:small_variants:merge:: DUPLEX BAM MAF -> %s",
            input_duplex_maf,
        )
    if input_simplex_maf:
        s_maf = pd.read_csv(input_simplex_maf, sep="\t", header="infer", index_col=False)
        logger.info(
            "genotype_variants:small_variants:merge:: SIMPLEX BAM MAF -> %s",
            input_simplex_maf,
        )

    # generate duplex simplex data frame
    ds_maf = None

    if d_maf is not None and s_maf is not None:
        ds_maf = cdsd(s_maf, d_maf)
        file_name = pathlib.Path.cwd().joinpath(
            patient_id + "-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        write_csv(file_name, ds_maf)

    # generate data frame based on satisfying conditions
    file_name = None
    (df_o_s_ds, df_s_ds, df_s_ds) = None, None, None
    if o_maf is not None and i_maf is not None and ds_maf is not None:
        df_o_s_ds = camd(o_maf, i_maf, ds_maf)
        file_name = pathlib.Path.cwd().joinpath(
            patient_id + "-ORG-STD-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        write_csv(file_name, df_o_s_ds)
    elif o_maf is not None and i_maf is not None:
        pass
    elif o_maf is not None and ds_maf is not None:
        df_o_ds = camd(o_maf, None, ds_maf)
        file_name = pathlib.Path.cwd().joinpath(
            patient_id + "-ORG-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        write_csv(file_name, df_o_ds)
    elif i_maf is not None and ds_maf is not None:
        df_s_ds = camd(None, i_maf, ds_maf)
        file_name = pathlib.Path.cwd().joinpath(
            patient_id + "-STD-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        write_csv(file_name, df_s_ds)
    elif i_maf is not None and d_maf is not None:
        pass
    elif i_maf is not None and s_maf is not None:
        pass
    elif o_maf is not None and d_maf is not None:
        pass
    elif o_maf is not None and s_maf is not None:
        pass
    else:
        file_name = pathlib.Path.cwd().joinpath(
            patient_id + "-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        write_csv(file_name, ds_maf)
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")
    return file_name


def write_csv(file_name, data_frame):
    try:
        data_frame.to_csv(str(file_name), sep="\t", index=False)
        logger.info(
            "genotype_variants:small_variants:create_csv:: merged genotyped data has been written to %s",
            file_name,
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype_variants:small_variants:create_csv:: could not write to CSV file, due to error: %s",
            e,
        )
        exit(1)


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
@click.option(
    "-g",
    "--gbcms-path",
    required=True,
    type=click.Path(exists=True),
    help="Full path to GetBaseCountMultiSample executable with fragment support",
)
@click.option(
    "-fd",
    "--filter-duplicate",
    required=False,
    default=0,
    type=click.INT,
    help="Filter duplicate parameter for GetBaseCountMultiSample",
)
@click.option(
    "-fc",
    "--fragment-count",
    required=False,
    default=1,
    type=click.INT,
    help="Fragment Count parameter for GetBaseCountMultiSample",
)
@click.option(
    "-mapq",
    "--mapping-quality",
    required=False,
    default=20,
    type=click.INT,
    help="Mapping quality for GetBaseCountMultiSample",
)
@click.option(
    "-t",
    "--threads",
    required=False,
    default=1,
    type=click.INT,
    help="Number of threads to use for GetBaseCountMultiSample",
)
@click_log.simple_verbosity_option(logger)
def all(
    input_maf,
    reference_fasta,
    gbcms_path,
    patient_id,
    standard_bam,
    duplex_bam,
    simplex_bam,
    filter_duplicate,
    fragment_count,
    mapping_quality,
    threads,
):
    """
    Command that helps to generate genotyped MAF and 
    merge the genotyped MAF.
    the output file will be labelled with 
    patient identifier as prefix
    """
    pid = os.getpid()
    logger_file = "genotype_variants_" + str(pid) + ".log"
    logger_output = pathlib.Path.cwd().joinpath(logger_file)
    fh = logging.FileHandler(logger_output)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(
        "========================================================================================"
    )
    logger.info(
        ">>> Running genotype_variants for small variants to generate genotypes and merge MAF <<<"
    )
    logger.info(
        "========================================================================================="
    )
    t1_start = time.perf_counter()
    t2_start = time.process_time()
    (standard_maf, simplex_maf, duplex_maf) = generate.callback(
        input_maf,
        reference_fasta,
        gbcms_path,
        patient_id,
        standard_bam,
        duplex_bam,
        simplex_bam,
        filter_duplicate,
        fragment_count,
        mapping_quality,
        threads,
    )
    final_file = merge.callback(patient_id, input_maf, standard_maf, duplex_maf, simplex_maf)
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")
    return final_file

@cli.command()
@click.option(
    "-i",
    "--input-metadata",
    required=True,
    type=click.Path(exists=True),
    help="Full path to metadata file in TSV/EXCEL format, with following headers: patient_id, maf, standard_bam, duplex_bam, simplex_bam. Make sure to use full paths inside the metadata file",
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
    "-fd",
    "--filter-duplicate",
    required=False,
    default=0,
    type=click.INT,
    help="Filter duplicate parameter for GetBaseCountMultiSample",
)
@click.option(
    "-fc",
    "--fragment-count",
    required=False,
    default=1,
    type=click.INT,
    help="Fragment Count parameter for GetBaseCountMultiSample",
)
@click.option(
    "-mapq",
    "--mapping-quality",
    required=False,
    default=20,
    type=click.INT,
    help="Mapping quality for GetBaseCountMultiSample",
)
@click.option(
    "-t",
    "--threads",
    required=False,
    default=1,
    type=click.INT,
    help="Number of threads to use for GetBaseCountMultiSample",
)
@click_log.simple_verbosity_option(logger)
def multiple_patient(
    input_metadata,
    reference_fasta,
    gbcms_path,
    filter_duplicate,
    fragment_count,
    mapping_quality,
    threads,
):
    """
    Command that helps to generate genotyped MAF and 
    merge the genotyped MAF for multiple patients.
    the output file will be labelled with 
    patient identifier as prefix

    Expected header of metadata_file in any order:
    patient_id
    maf
    standard_bam
    duplex_bam
    simplex_bam
    
    For maf, standard_bam, duplex_bam and simplex_bam please include full path to the file.
    """
    pid = os.getpid()
    logger_file = "genotype_variants_" + str(pid) + ".log"
    logger_output = pathlib.Path.cwd().joinpath(logger_file)
    fh = logging.FileHandler(logger_output)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info(
        "========================================================================================"
    )
    logger.info(
        ">>> Running genotype_variants for small variants to generate genotypes and merge MAF <<<"
    )
    logger.info(
        "========================================================================================="
    )
    t1_start = time.perf_counter()
    t2_start = time.process_time()
    metadata = pd.DataFrame()
    try:
        metadata = pd.read_excel(input_metadata)
    except:
        e = sys.exc_info()[0]
        logger.warning(
            "genotype_variants:small_variants:multiple_patient:: could not read to EXCEL file, due to error: %s",
            e,
        )
        logger.warning(
            "genotype_variants:small_variants:multiple_patient:: Assuming its as TSV file"
        )
        pass
    try:
        metadata = pd.read_csv(input_metadata, sep="\t", header="infer")
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype_variants:small_variants:multiple_patient:: could not read TSV file, due to error: %s. Please fix and rerun the script",
            e,
        )
        exit(1)
    for ind in metadata.index:
        if pd.notnull(metadata['maf'][ind]):
            if pathlib.Path(metadata['maf'][ind]).is_file():
                input_maf = metadata['maf'][ind]
            else:
                logger.error("genotype_variants::small_variants::multiple_patient:: Maf file to genotype variants is present but the path is invalid. Please provide a valid path")
                exit(1)
        else:
            logger.error("genotype_variants::small_variants::multiple_patient:: Maf file to genotype variants is not present and is required.")
            exit(1)
        if pd.notnull(metadata['standard_bam'][ind]): 
            if pathlib.Path(metadata['standard_bam'][ind]).is_file():
                standard_bam = metadata['standard_bam'][ind]
            else:
                standard_bam = None
        else:
            standard_bam = None
            logger.info("genotype_variants::small_variants::multiple_patient:: Standard BAM file to genotype variants is not present.")
        if pd.notnull(metadata['duplex_bam'][ind]):
            if pathlib.Path(metadata['duplex_bam'][ind]).is_file():
                duplex_bam = metadata['duplex_bam'][ind]
            else:
                duplex_bam = None
        else:
            duplex_bam = None
        if pd.notnull(metadata['simplex_bam'][ind]):
            if pathlib.Path(metadata['simplex_bam'][ind]).is_file():
                simplex_bam = metadata['simplex_bam'][ind]
            else:
                simplex_bam = None
        else:
            simplex_bam = None
        if duplex_bam and simplex_bam:
            logger.info("genotype_variants::small_variants::multiple_patient:: duplex_bam and simplex_bam are present for genotype variants.")
        else:
            logger.error("genotype_variants::small_variants::multiple_patient:: duplex_bam and simplex_bam are not present for genotype variants! Please provide both of them to run genotype_variants.")
            exit(1)
        if pd.notnull(metadata['patient_id'][ind]):
            patient_id = metadata['patient_id'][ind]
        else:
            logger.error("genotype_variants:small_variants:multiple_patient:: Patient Id is not a string, please check input metadata file and try again.")
            exit(1)
        logger.info("genotype_variants:small_variants::multiple_patient:: %s is being processed", patient_id)
        final_file = all.callback(
            input_maf,
            reference_fasta,
            gbcms_path,
            patient_id,
            standard_bam,
            duplex_bam,
            simplex_bam,
            filter_duplicate,
            fragment_count,
            mapping_quality,
            threads,
        )
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")
    return
