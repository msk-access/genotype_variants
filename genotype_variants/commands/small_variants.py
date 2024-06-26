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


# Generate
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
@click.option(
    "-si",
    "--sample-id",
    required=False,
    type=click.STRING,
    help="Override default sample name",
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
    threads,
    sample_id
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

    logger.info("small_variants: Input MAF: %s", input_maf)
    logger.info("small_variants: Reference FASTA: %s", reference_fasta)
    if not (patient_id or sample_id):
        logger.error(
            "genotype_variants:small_variants:generate:: either Patient ID or Sample ID must be provided",
            )
        exit(1)
    if patient_id:
            logger.info("small_variants: Patient ID: %s", patient_id)
    if sample_id:
            logger.info("small_variants: Sample ID: %s", sample_id)
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
            sample_id
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
            sample_id
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
            sample_id
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

@click_log.simple_verbosity_option(logger)
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
    sample_id
):

    """This will help generate command for GetBaseCountMultiSample"""

    # if no sample_id is provided, it is inferred from the patient_id
    if not sample_id:
        logger.warning("genotype_variants:small_variants:generate_gbcms: No Sample ID found: Inferring Sample ID from Patient ID for for Geontyping.")
        sample_id = patient_id
    logger.info("genotype_variants:small_variants:generate_gbcms: Sample ID found. Genotyping using Sample ID.")
    outfile = sample_id + "-" + btype + "_genotyped.maf"
    output_maf = pathlib.Path.cwd().joinpath(outfile)
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
        + " --generic_counting"
    )

    return (cmd, output_maf)


# Merge
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
    required=False,
    type=click.STRING,
    help="Alphanumeric string indicating patient identifier",
)
@click_log.simple_verbosity_option(logger)
def merge(
    patient_id, input_maf, input_standard_maf, input_duplex_maf, input_simplex_maf, sample_id, tumor_name_override
):
    """
    Given original input MAF used as an input for GBCMS along with
    GBCMS generated output MAF for standard_bam, duplex_bam or simplex bam,
    Merge them into a single output MAF format.
    If both duplex_bam and simplex_bam based MAF are provided
    the program will generate merged genotypes as well.
    The output file will be based on the give alphanumeric patient identifier as prefix, or sample identifier.
    Sample identifier is prioritized over patient identifier.
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

        create_empty_maf_if_missing(input_standard_maf)

        i_maf = pd.read_csv(
            input_standard_maf, sep="\t", header="infer", index_col=False
        )
    if input_duplex_maf:

        create_empty_maf_if_missing(input_duplex_maf)

        d_maf = pd.read_csv(input_duplex_maf, sep="\t", header="infer", index_col=False)
        logger.info(
            "genotype_variants:small_variants:merge:: DUPLEX BAM MAF -> %s",
            input_duplex_maf,
        )
    if input_simplex_maf:

        create_empty_maf_if_missing(input_simplex_maf)

        s_maf = pd.read_csv(
            input_simplex_maf, sep="\t", header="infer", index_col=False
        )
        logger.info(
            "genotype_variants:small_variants:merge:: SIMPLEX BAM MAF -> %s",
            input_simplex_maf,
        )

    # generate duplex simplex data frame
    ds_maf = None

    # base outfile path either provided sample name or patient id
    if not (patient_id or sample_id):
        logger.error(
            "genotype_variants:small_variants:generate:: either Patient ID or Sample ID must be provided",
            )
        exit(1)
    if patient_id:
            bam_id = patient_id
    if sample_id:
            bam_id = sample_id
    logger.info("small_variants: ID: %s", bam_id)
    outfile = bam_id
    if d_maf is not None and s_maf is not None:
        ds_maf = cdsd(s_maf, d_maf)
        if tumor_name_override:
            ds_maf['Tumor_Sample_Barcode'] = bam_id
        file_name = pathlib.Path.cwd().joinpath(
            outfile + "-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        write_csv(file_name, ds_maf)

    # generate data frame based on satisfying conditions
    file_name = None
    (df_o_s_ds, df_o_s, df_s_ds, df_s_ds) = None, None, None, None
    if o_maf is not None and i_maf is not None and ds_maf is not None:
        df_o_s_ds = camd(o_maf, i_maf, ds_maf)
        if tumor_name_override:
            df_o_s_ds['Tumor_Sample_Barcode'] = bam_id
        file_name = pathlib.Path.cwd().joinpath(
            outfile + "-ORG-STD-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        write_csv(file_name, df_o_s_ds)
    elif o_maf is not None and i_maf is not None:
        df_o_s = camd(o_maf, i_maf, None)
        if tumor_name_override:
            df_o_s['Tumor_Sample_Barcode'] = bam_id
        file_name = pathlib.Path.cwd().joinpath(
            outfile + "-ORG-STD" + "_genotyped.maf"
        )
        write_csv(file_name, df_o_s)
    elif o_maf is not None and ds_maf is not None:
        df_o_ds = camd(o_maf, None, ds_maf)
        if tumor_name_override:
            df_o_ds['Tumor_Sample_Barcode'] = bam_id
        file_name = pathlib.Path.cwd().joinpath(
            outfile + "-ORG-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        write_csv(file_name, df_o_ds)
    elif i_maf is not None and ds_maf is not None:
        df_s_ds = camd(None, i_maf, ds_maf)
        if tumor_name_override:
            df_s_ds['Tumor_Sample_Barcode'] = bam_id
        file_name = pathlib.Path.cwd().joinpath(
            outfile + "-STD-SIMPLEX-DUPLEX" + "_genotyped.maf"
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
            outfile + "-SIMPLEX-DUPLEX" + "_genotyped.maf"
        )
        if tumor_name_override:
            ds_maf['Tumor_Sample_Barcode'] = bam_id
        write_csv(file_name, ds_maf)
    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")
    return file_name


def create_empty_maf_if_missing(filename):
    header = [
        'Hugo_Symbol',
        'Entrez_Gene_Id',
        'Center',
        'NCBI_Build',
        'Chromosome',
        'Start_Position',
        'End_Position',
        'Strand',
        'Variant_Classification',
        'Variant_Type',
        'Reference_Allele',
        'Tumor_Seq_Allele1',
        'Tumor_Seq_Allele2',
        'dbSNP_RS',
        'dbSNP_Val_Status',
        'Tumor_Sample_Barcode',
        'Matched_Norm_Sample_Barcode',
        'Match_Norm_Seq_Allele1',
        'Match_Norm_Seq_Allele2',
        'Tumor_Validation_Allele1',
        'Tumor_Validation_Allele2',
        'Match_Norm_Validation_Allele1',
        'Match_Norm_Validation_Allele2',
        'Verification_Status',
        'Validation_Status',
        'Mutation_Status',
        'Sequencing_Phase',
        'Sequence_Source',
        'Validation_Method',
        'Score',
        'BAM_File',
        'Sequencer',
        't_ref_count',
        't_alt_count',
        'n_ref_count',
        'n_alt_count',
        'Caller',
        't_total_count',
        't_variant_frequency',
        't_total_count_forward',
        't_ref_count_forward',
        't_alt_count_forward',
        't_total_count_fragment',
        't_ref_count_fragment',
        't_alt_count_fragment']

    if not os.path.exists(filename):
        empty_df = pd.DataFrame(columns=header)
        empty_df.to_csv(filename, index=False, sep='\t')


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


# All
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
    required=False,
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
@click.option(
    "-si",
    "--sample-id",
    required=False,
    type=click.STRING,
    help="Override default sample name",
)
@click.option(
    "-to",
    "--tumor_name_override",
    required=False,
    is_flag=True,
    default=False,
    help="Override the MAF Tumor_Sample_Barcode name with the BAM Tumor Sample Barcode",
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
    sample_id,
    tumor_name_override

):
    """
    Command that helps to generate genotyped MAF and
    merge the genotyped MAF.
    the output file will be labelled with
    patient, or sample identifier as prefix. Sample identifier prioritized.
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
        sample_id
    )
    final_file = merge.callback(
        patient_id, input_maf, standard_maf, duplex_maf, simplex_maf, sample_id, tumor_name_override
    )

    t1_stop = time.perf_counter()
    t2_stop = time.process_time()
    logger.info("--------------------------------------------------")
    logger.info("Elapsed time: %.1f [min]" % ((t1_stop - t1_start) / 60))
    logger.info("CPU process time: %.1f [min]" % ((t2_stop - t2_start) / 60))
    logger.info("--------------------------------------------------")
    return final_file


# Multiple Sample Process
@cli.command()
@click.option(
    "-i",
    "--input-metadata",
    required=True,
    type=click.Path(exists=True),
    help="Full path to metadata file in TSV/EXCEL format, with following headers: sample_id, maf, standard_bam, duplex_bam, simplex_bam. Make sure to use full paths inside the metadata file",
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
def multiple_samples(
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
    merge the genotyped MAF for multiple samples.
    the output file will be labelled with
    patient identifier, or sample identifier as prefix.
    Sample prioritized.

    Expected header of metadata_file in any order:
    sample_id,
    maf,
    standard_bam,
    duplex_bam,
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
    metadata = None
    try:
        metadata = pd.read_excel(input_metadata)
    except:
        e = sys.exc_info()[0]
        logger.warning(
            "genotype_variants:small_variants:multiple_samples:: could not read to EXCEL file, due to error: %s",
            e,
        )
        logger.warning(
            "genotype_variants:small_variants:multiple_samples:: Assuming its as TSV file"
        )
        pass
    if metadata is None:
        try:
            metadata = pd.read_csv(input_metadata, sep="\t", header="infer")
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype_variants:small_variants:multiple_samples:: could not read TSV file, due to error: %s. Please fix and rerun the script",
                e,
            )
            exit(1)
    else:
        pass
    for ind in metadata.index:
        if pd.notnull(metadata["maf"][ind]):
            if pathlib.Path(metadata["maf"][ind]).is_file():
                input_maf = metadata["maf"][ind]
            else:
                logger.error(
                    "genotype_variants::small_variants::multiple_samples:: Maf file to genotype variants is present but the path is invalid. Please provide a valid path"
                )
                exit(1)
        else:
            logger.error(
                "genotype_variants::small_variants::multiple_samples:: Maf file to genotype variants is not present and is required."
            )
            exit(1)
        if pd.notnull(metadata["standard_bam"][ind]):
            if pathlib.Path(metadata["standard_bam"][ind]).is_file():
                standard_bam = metadata["standard_bam"][ind]
            else:
                standard_bam = None
        else:
            standard_bam = None
            logger.info(
                "genotype_variants::small_variants::multiple_samples:: Standard BAM file to genotype variants is not present."
            )
        if pd.notnull(metadata["duplex_bam"][ind]):
            if pathlib.Path(metadata["duplex_bam"][ind]).is_file():
                duplex_bam = metadata["duplex_bam"][ind]
            else:
                duplex_bam = None
        else:
            duplex_bam = None
        if pd.notnull(metadata["simplex_bam"][ind]):
            if pathlib.Path(metadata["simplex_bam"][ind]).is_file():
                simplex_bam = metadata["simplex_bam"][ind]
            else:
                simplex_bam = None
        else:
            simplex_bam = None

        if standard_bam or duplex_bam or simplex_bam:
            logger.info(
                "genotype_variants::small_variants::multiple_samples:: standard_bam, duplex_bam and simplex_bam are present for genotype variants."
            )
        else:
            logger.warning(
                "genotype_variants::small_variants::multiple_samples:: one of standard_bam, duplex_bam and simplex_bam is not present for genotype variants! Either the Standard BAM or the Duplex BAM and the Simplex BAM should be present for genotype variants."
            )

        if pd.notnull(metadata["sample_id"][ind]):
            sample_id = metadata["sample_id"][ind]
        else:
            logger.error(
                "genotype_variants:small_variants:multiple_samples:: Sample id is not a string, please check input metadata file and try again."
            )
            exit(1)
        logger.info(
            "genotype_variants:small_variants::multiple_samples:: %s is being processed",
            sample_id,
        )
        final_file = all.callback(
            input_maf,
            reference_fasta,
            gbcms_path,
            sample_id,
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
