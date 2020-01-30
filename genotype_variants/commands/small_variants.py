import os
import sys
import logging
import time
import pathlib
import subprocess
import numpy as np
import re
from genotype_variants.run_cmd import run_cmd

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
    default=20
    type=click.INT,
    help="Mapping quality for GetBaseCountMultiSample",
)
@click.option(
    "-t",
    "--threads",
    required=False,
    default=1
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
    logger.info("Patient ID: %s", patient_id)
    logger.info("Input MAF: %s", input_maf)
    logger.info("Reference FASTA: %s", reference_fasta)
    logger.info("GetBaseCountMultiSample: %s", gbcms_path)
    if standard_bam:
        logger.info("Standard BAM: %s", standard_bam)
    if duplex_bam:
        logger.info("Duplex BAM: %s", duplex_bam)
    if simplex_bam:
        logger.info("Simplex BAM: %s", simplex_bam)
    # Run GetBaseMultisampleCount for each available bam file
    std_output_maf = None
    duplex_output_maf = None
    simplex_output_maf = None
    p1, p2, p3 = None, None, None
    if standard_bam:
        btype = "STANDARD"
        (cmd, std_output_maf) = generate_gbcms_cmd(
            input_maf, btype, reference_fasta, gbcms_path, patient_id, standard_bam
        )
        p1 = run_cmd(cmd)
    if duplex_bam:
        btype = "DUPLEX"
        (cmd, duplex_output_maf) = generate_gbcms_cmd(
            input_maf, btype, reference_fasta, gbcms_path, patient_id, duplex_bam
        )
        p2 = run_cmd(cmd)
    if simplex_bam:
        btype = "SIMPLEX"
        (cmd, simplex_output_maf) = generate_gbcms_cmd(
            input_maf, btype, reference_fasta, gbcms_path, patient_id, simplex_bam
        )
        p3 = run_cmd(cmd)

    merge_maf(patient_id, input_maf, duplex_output_maf, simplex_output_maf)
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


def merge_maf(patient_id, input_maf, duplex_output_maf, simplex_output_maf):
    i_maf = pd.read_csv(input_maf, sep="\t", header="infer")
    d_maf = pd.read_csv(duplex_output_maf, sep="\t", header="infer")
    s_maf = pd.read_csv(simplex_output_maf, sep="\t", header="infer")
    df_merge = create_duplexsimplex(s_maf, d_maf)
    df_merge.to_csv("test.maf", sep="\t", index=False)

#Adopted from Maysun script
def create_duplexsimplex(df_s, df_d):
    np.seterr(divide="ignore", invalid="ignore")
    mutation_key = [
        "Chromosome",
        "Start_Position",
        "End_Position",
        "Reference_Allele",
        "Tumor_Seq_Allele1",
    ]
    df_s = df_s.copy()
    df_d = df_d.copy()
    # Prep Simplex
    df_s.rename(
        columns={
            "t_alt_count_fragment": "t_alt_count_fragment_simplex",
            "t_ref_count_fragment": "t_ref_count_fragment_simplex",
        },
        inplace=True,
    )
    df_s["Tumor_Sample_Barcode"] = df_s["Tumor_Sample_Barcode"].str.replace(
        "-SIMPLEX", ""
    )
    df_s.set_index("Tumor_Sample_Barcode", append=True, drop=False, inplace=True)
    # Prep Duplex
    df_d.rename(
        columns={
            "t_alt_count_fragment": "t_alt_count_fragment_duplex",
            "t_ref_count_fragment": "t_ref_count_fragment_duplex",
        },
        inplace=True,
    )
    df_d["Tumor_Sample_Barcode"] = df_d["Tumor_Sample_Barcode"].str.replace(
        "-DUPLEX", ""
    )
    df_d.set_index("Tumor_Sample_Barcode", append=True, drop=False, inplace=True)
    # Merge
    df_ds = df_s.merge(
        df_d[["t_ref_count_fragment_duplex", "t_alt_count_fragment_duplex"]],
        left_index=True,
        right_index=True,
    )
    ##Add
    df_ds["t_ref_count_fragment"] = (
        df_ds["t_ref_count_fragment_simplex"] + df_ds["t_ref_count_fragment_duplex"]
    )
    df_ds["t_alt_count_fragment"] = (
        df_ds["t_alt_count_fragment_simplex"] + df_ds["t_alt_count_fragment_duplex"]
    )
    df_ds["t_total_count_fragment"] = (
        df_ds["t_alt_count_fragment"] + df_ds["t_ref_count_fragment"]
    )
    ##clean up
    df_ds.drop(
        [
            "t_ref_count_fragment_simplex",
            "t_ref_count_fragment_duplex",
            "t_alt_count_fragment_simplex",
            "t_alt_count_fragment_duplex",
        ],
        axis=1,
        inplace=True,
    )
    df_ds["Tumor_Sample_Barcode"] = df_ds["Tumor_Sample_Barcode"] + "-SIMPLEX-DUPLEX"
    df_ds.set_index(mutation_key, drop=False, inplace=True)
    df_ds = find_VAFandsummary(df_ds)
    return df_ds


def find_VAFandsummary(df_fillout):
    df_fillout = df_fillout.copy()
    # find the VAF from the fillout
    df_fillout["t_vaf_fragment"] = (
        df_fillout["t_alt_count_fragment"]
        / (
            df_fillout["t_alt_count_fragment"].astype(int)
            + df_fillout["t_ref_count_fragment"].astype(int)
        )
    ).round(4)
    df_fillout["summary_fragment"] = (
        "DP="
        + (
            df_fillout["t_alt_count_fragment"].astype(int)
            + df_fillout["t_ref_count_fragment"].astype(int)
        ).astype(str)
        + ";RD="
        + df_fillout["t_ref_count_fragment"].astype(str)
        + ";AD="
        + df_fillout["t_alt_count_fragment"].astype(str)
        + ";VF="
        + df_fillout["t_vaf_fragment"].fillna(0).astype(str)
    )
    return df_fillout

