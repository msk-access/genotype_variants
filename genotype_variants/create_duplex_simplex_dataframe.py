import logging
import numpy as np
import sys

"""
create_duplex_simplex_dataframe
~~~~~~~~~~~~~~~
:Description: Code to merge duplex and simplex fragment counts in MAF format
"""
"""
Created on February 10, 2020
Description: Code to merge duplex and simplex fragment counts in MAF format
@author: Ronak H Shah & Maysun Hasan
"""
# Making logging possible
logger = logging.getLogger("genotype_variants")
logger.info(
    "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Generating duplex simplex dataframe"
)
# Adopted from Maysun script
def create_duplex_simplex_dataframe(simplex_dataframe, duplex_dataframe):
    """Code to merge duplex and simplex fragment counts in MAF format
    """
    np.seterr(divide="ignore", invalid="ignore")
    mutation_key = [
        "Chromosome",
        "Start_Position",
        "End_Position",
        "Reference_Allele",
        "Tumor_Seq_Allele2",
    ]
    df_s = simplex_dataframe.copy()
    df_d = duplex_dataframe.copy()

    # Prep Simplex
    try:
        df_s.rename(
            columns={
                "t_alt_count_fragment": "t_alt_count_fragment_simplex",
                "t_ref_count_fragment": "t_ref_count_fragment_simplex",
                "t_total_count_fragment": "t_total_count_fragment_simplex",
            },
            inplace=True,
        )
        logger.debug(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe::Successfully renamed column names in simplex data frame"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Could not rename column names in simplex data frame due to error, %s",
            e,
        )
        exit(1)

    try:
        df_s["Tumor_Seq_Allele2"] = df_s["Tumor_Seq_Allele1"]
        logger.debug(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Successfully generated Tumor_Seq_Allele2 column"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Could not generate Tumor_Seq_Allele2 column due to error, %s",
            e,
        )
        exit(1)

    try:
        df_s["t_total_count_fragment_simplex"] = (
            df_s["t_ref_count_fragment_simplex"] + df_s["t_alt_count_fragment_simplex"]
        )
        logger.debug(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Successfully generated t_total_count_fragment_simplex column"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Could not generate t_total_count_fragment_simplex column due to error, %s",
            e,
        )
        exit(1)

    try:
        df_s["t_vaf_fragment_simplex"] = (
            df_s["t_alt_count_fragment_simplex"]
            / (
                df_s["t_alt_count_fragment_simplex"].astype(int)
                + df_s["t_ref_count_fragment_simplex"].astype(int)
            )
        ).round(4)
        df_s["t_vaf_fragment_simplex"].fillna(0, inplace=True)
        logger.debug(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Successfully generated t_vaf_fragment_simplex column"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Could not generate t_vaf_fragment_simplex column due to error, %s",
            e,
        )
        exit(1)

    try:
        df_s["Tumor_Sample_Barcode"] = df_s["Tumor_Sample_Barcode"].str.replace(
            "-SIMPLEX", ""
        )
        logger.debug(
            "genotype_variants:small_variants:create_duplex_simplex_dataframe:: Successfully renamed samples in Tumor_Sample_Barcode for duplex data frame"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not rename samples in Tumor_Sample_Barcode for simplex data frame, due to error, %s",
            e,
        )

    try:
        df_s.set_index(mutation_key, drop=False, inplace=True)
        logger.debug(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Successfully reset the index for simplex data frame"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not reset the index for simplex data frame, due to error, %s",
            e,
        )

    # Prep Duplex
    try:
        df_d.rename(
            columns={
                "t_alt_count_fragment": "t_alt_count_fragment_duplex",
                "t_ref_count_fragment": "t_ref_count_fragment_duplex",
                "t_total_count_fragment": "t_total_count_fragment_duplex",
            },
            inplace=True,
        )
        logger.debug(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe::Successfully renamed column names in duplex data frame"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Could not rename column names in duplex data frame due to error, %s",
            e,
        )
        exit(1)

    try:
        df_d["Tumor_Seq_Allele2"] = df_d["Tumor_Seq_Allele1"]
        logger.debug(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Successfully generated Tumor_Seq_Allele2 column"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Could not generate Tumor_Seq_Allele2 column due to error, %s",
            e,
        )
        exit(1)

    try:
        df_d["t_total_count_fragment_duplex"] = (
            df_d["t_ref_count_fragment_duplex"] + df_d["t_alt_count_fragment_duplex"]
        )
        logger.debug(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Successfully generated t_total_count_fragment_duplex column"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Could not generate t_total_count_fragment_duplex column due to error, %s",
            e,
        )
        exit(1)

    try:
        df_d["t_vaf_fragment_duplex"] = (
            df_d["t_alt_count_fragment_duplex"]
            / (
                df_d["t_alt_count_fragment_duplex"].astype(int)
                + df_d["t_ref_count_fragment_duplex"].astype(int)
            )
        ).round(4)
        df_d["t_vaf_fragment_duplex"].fillna(0, inplace=True)
        logger.debug(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Successfully generated t_vaf_fragment_duplex column"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants::create_duplex_simplex_dataframe:: Could not generate t_vaf_fragment_duplex column due to error, %s",
            e,
        )
        exit(1)

    try:
        df_d["Tumor_Sample_Barcode"] = df_d["Tumor_Sample_Barcode"].str.replace(
            "-DUPLEX", ""
        )
        logger.debug(
            "genotype_variants:small_variants:create_duplex_simplex_dataframe:: Successfully renamed samples in Tumor_Sample_Barcode for duplex data frame"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not rename samples in Tumor_Sample_Barcode for duplex data frame, due to error, %s",
            e,
        )

    try:
        df_d.set_index(mutation_key, drop=False, inplace=True)
        logger.debug(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Successfully reset the index for duplex data frame"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not reset the index for duplex data frame, due to error, %s",
            e,
        )

    # Merge
    df_ds = None
    try:
        df_d = df_d.reindex(df_s.index)
        df_ds = df_s.merge(
            df_d[
                [
                    "t_ref_count_fragment_duplex",
                    "t_alt_count_fragment_duplex",
                    "t_total_count_fragment_duplex",
                    "t_vaf_fragment_duplex",
                ]
            ],
            left_index=True,
            right_index=True,
        )
        logger.info(
            "genotype_variants:small_variants:create_duplex_simplex_dataframe:: Successfully created merge data frame for simplex and duplex data"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not create merge data frame for simplex and duplex data due to error, %s",
            e,
        )
        exit(1)
    ##Add
    try:
        df_ds["t_ref_count_fragment_simplex_duplex"] = (
            df_ds["t_ref_count_fragment_simplex"] + df_ds["t_ref_count_fragment_duplex"]
        )
        df_ds["t_alt_count_fragment_simplex_duplex"] = (
            df_ds["t_alt_count_fragment_simplex"] + df_ds["t_alt_count_fragment_duplex"]
        )
        df_ds["t_total_count_fragment_simplex_duplex"] = (
            df_ds["t_alt_count_fragment_simplex_duplex"]
            + df_ds["t_ref_count_fragment_simplex_duplex"]
        )
        df_ds["t_vaf_fragment_simplex_duplex"] = (
            df_ds["t_alt_count_fragment_simplex_duplex"]
            / (
                df_ds["t_alt_count_fragment_simplex_duplex"].astype(int)
                + df_ds["t_ref_count_fragment_simplex_duplex"].astype(int)
            )
        ).round(4)
        df_ds["t_vaf_fragment_simplex_duplex"].fillna(0, inplace=True)
        logger.debug(
            "genotype_variants:small_variants:create_duplex_simplex_dataframe:: Successfully generated column for merged counts"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not generate merged count column in the merged data frame due to error, %s",
            e,
        )
        exit(1)

    ##clean up
    try:
        df_ds.drop(
            [
                "t_ref_count",
                "t_ref_count_forward",
                "t_alt_count",
                "t_alt_count_forward",
                "t_total_count",
                "t_total_count_forward",
                "t_variant_frequency",
            ],
            axis=1,
            inplace=True,
        )
        logger.debug(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Successfully dropped columns after merge"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not drop columns after merge, %s",
            e,
        )
        exit(1)

    # Rename Sample Names
    try:
        df_ds["Tumor_Sample_Barcode"] = (
            df_ds["Tumor_Sample_Barcode"] + "-SIMPLEX-DUPLEX"
        )
        logger.debug(
            "genotype_variants:small_variants:create_duplex_simplex_dataframe:: Successfully renamed samples in Tumor_Sample_Barcode for merged data frame"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not rename samples in Tumor_Sample_Barcode for merged data frame, due to error, %s",
            e,
        )
        exit(1)

    try:
        df_ds.set_index(mutation_key, drop=False, inplace=True)
        logger.debug(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Successfully reset the index for merged data frame"
        )
    except:
        e = sys.exc_info()[0]
        logger.error(
            "genotype:variants:small_variants:create_duplex_simplex_dataframe:: Could not reset the index for merged data frame, due to error, %s",
            e,
        )
        exit(1)

    logger.info(
        "Successfully merged data frame and the counts for simplex and duplex MAF"
    )
    return df_ds
