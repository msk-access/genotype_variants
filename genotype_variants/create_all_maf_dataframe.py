import logging
import numpy as np
import sys

"""
create_all_maf_dataframe
~~~~~~~~~~~~~~~
:Description: Code to merge all the data frames generated from MAF files into one data frame
"""
"""
Created on February 10, 2020
Description: Code to merge all the data frames generated from MAF files into one data frame
@author: Ronak H Shah & Maysun Hasan
"""
# Making logging possible
logger = logging.getLogger("genotype_variants")
logger.info(
    "genotype:variants:small_variants::create_all_maf_dataframe:: Generating duplex simplex dataframe"
)
# Adopted from Maysun script
def create_all_maf_dataframe(
    original_dataframe, standard_dataframe, simplex_duplex_dataframe
):
    """Code to merge all the data frames generated from MAF files into one data frame"""
    np.seterr(divide="ignore", invalid="ignore")
    mutation_key = [
        "Chromosome",
        "Start_Position",
        "End_Position",
        "Reference_Allele",
        "Tumor_Seq_Allele2",
    ]
    (df_ds, df_s, df_o) = None, None, None
    if simplex_duplex_dataframe is not None:
        df_ds = simplex_duplex_dataframe.copy()
    if standard_dataframe is not None:
        df_s = standard_dataframe.copy()
    if original_dataframe is not None:
        df_o = original_dataframe.copy()

    # Prep Simplex duplex
    if df_ds is not None:
        try:
            df_ds["Tumor_Sample_Barcode"] = df_ds["Tumor_Sample_Barcode"].str.replace(
                "-SIMPLEX-DUPLEX", ""
            )
            logger.debug(
                "genotype_variants:small_variants:create_all_maf_dataframe:: Successfully renamed samples in Tumor_Sample_Barcode for simplex duplex data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not rename samples in Tumor_Sample_Barcode for simplex duplex data frame, due to error, %s",
                e,
            )
            exit(1)

        try:
            df_ds.set_index(mutation_key, drop=False, inplace=True)
            logger.debug(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for simplex duplex data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for simplex duplex data frame, due to error, %s",
                e,
            )
            exit(1)

    # Prep Standard
    if df_s is not None:
        try:
            df_s.rename(
                columns={
                    "t_alt_count": "t_alt_count_standard",
                    "t_ref_count": "t_ref_count_standard",
                    "t_total_count": "t_total_count_standard",
                    "t_variant_frequency": "t_variant_frequency_standard",
                    "t_alt_count_forward": "t_alt_count_forward_standard",
                    "t_ref_count_forward": "t_ref_count_forward_standard",
                    "t_total_count_forward": "t_total_count_forward_standard",
                },
                inplace=True,
            )
            logger.debug(
                "genotype:variants:small_variants:create_all_maf_dataframe::Successfully renamed column names in standard data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants::create_all_maf_dataframe:: Could not rename column names in standard data frame due to error, %s",
                e,
            )
            exit(1)

        if df_s.shape[0] > 0:
            try:
                df_s["t_alt_count_reverse_standard"] = (
                    df_s["t_alt_count_standard"] - df_s["t_alt_count_forward_standard"]
                )
                df_s["t_ref_count_reverse_standard"] = (
                    df_s["t_ref_count_standard"] - df_s["t_ref_count_forward_standard"]
                )
                df_s["t_total_count_reverse_standard"] = (
                    df_s["t_total_count_standard"]
                    - df_s["t_total_count_forward_standard"]
                )
                logger.debug(
                    "genotype:variants:small_variants::create_all_maf_dataframe:: Successfully generated reverse count columns in standard data frame"
                )
            except:
                e = sys.exc_info()[0]
                logger.error(
                    "genotype:variants:small_variants::create_all_maf_dataframe:: Could not generate reverse count columns in standard data frame due to error, %s",
                    e,
                )
                exit(1)
        else:
            df_s["t_alt_count_reverse_standard"] = []
            df_s["t_ref_count_reverse_standard"] = []
            df_s["t_total_count_reverse_standard"] = []

        try:
            df_s["Tumor_Sample_Barcode"] = df_s["Tumor_Sample_Barcode"].str.replace(
                "-STANDARD", ""
            )
            logger.debug(
                "genotype_variants:small_variants:create_all_maf_dataframe:: Successfully renamed samples in Tumor_Sample_Barcode for standard data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not rename samples in Tumor_Sample_Barcode for standard data frame, due to error, %s",
                e,
            )
            exit(1)

        try:
            df_s.set_index(mutation_key, drop=False, inplace=True)
            logger.debug(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for standard data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for standard data frame, due to error, %s",
                e,
            )
            exit(1)

    # Prep Original
    if df_o is not None:
        try:
            df_o.set_index(mutation_key, drop=False, inplace=True)
            logger.debug(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for original data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for original data frame, due to error, %s",
                e,
            )
            exit(1)

    # Merge STANDARD with DUPLEX-SIMPLEX data frame
    df_s_ds = None
    if df_ds is not None and df_s is not None:
        try:
            df_ds = df_ds.reindex(df_s.index)
            df_s_ds = df_s.merge(
                df_ds[
                    [
                        "t_ref_count_fragment_simplex",
                        "t_alt_count_fragment_simplex",
                        "t_total_count_fragment_simplex",
                        "t_vaf_fragment_simplex",
                        "t_ref_count_fragment_duplex",
                        "t_alt_count_fragment_duplex",
                        "t_total_count_fragment_duplex",
                        "t_vaf_fragment_duplex",
                        "t_ref_count_fragment_simplex_duplex",
                        "t_alt_count_fragment_simplex_duplex",
                        "t_total_count_fragment_simplex_duplex",
                        "t_vaf_fragment_simplex_duplex",
                    ]
                ],
                left_index=True,
                right_index=True,
            )
            logger.info(
                "genotype_variants:small_variants:create_all_maf_dataframe:: Successfully created merge data frame for standard, simplex and duplex data"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not create merge data frame for standard, simplex and duplex data due to error, %s",
                e,
            )
            exit(1)
        try:
            df_s_ds.set_index(mutation_key, drop=False, inplace=True)
            logger.debug(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for merged data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for merged data frame, due to error, %s",
                e,
            )
            exit(1)

    # Merge Original with STANDARD-DUPLEX-SIMPLEX data frame
    df_o_s_ds = None
    if df_s_ds is not None:
        try:
            df_s_ds = df_s_ds.reindex(df_o.index)
            df_o_s_ds = df_o.merge(
                df_s_ds[
                    [
                        "t_ref_count_standard",
                        "t_alt_count_standard",
                        "t_total_count_standard",
                        "t_variant_frequency_standard",
                        "t_ref_count_forward_standard",
                        "t_alt_count_forward_standard",
                        "t_total_count_forward_standard",
                        "t_ref_count_reverse_standard",
                        "t_alt_count_reverse_standard",
                        "t_total_count_reverse_standard",
                        "t_ref_count_fragment_simplex",
                        "t_alt_count_fragment_simplex",
                        "t_total_count_fragment_simplex",
                        "t_vaf_fragment_simplex",
                        "t_ref_count_fragment_duplex",
                        "t_alt_count_fragment_duplex",
                        "t_total_count_fragment_duplex",
                        "t_vaf_fragment_duplex",
                        "t_ref_count_fragment_simplex_duplex",
                        "t_alt_count_fragment_simplex_duplex",
                        "t_total_count_fragment_simplex_duplex",
                        "t_vaf_fragment_simplex_duplex",
                    ]
                ],
                left_index=True,
                right_index=True,
            )
            logger.info(
                "genotype_variants:small_variants:create_all_maf_dataframe:: Successfully created merge data frame for original, standard, simplex and duplex data"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not create merge data frame for original, standard, simplex and duplex data due to error, %s",
                e,
            )
            exit(1)

        try:
            df_o_s_ds.set_index(mutation_key, drop=False, inplace=True)
            logger.debug(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for merged data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for merged data frame, due to error, %s",
                e,
            )
            exit(1)

    # Merge Original MAF data frame with STANDARD MAF data frame
    df_o_s = None
    if df_o is not None and df_s is not None:
        try:
            df_s = df_s.reindex(df_o.index)
            df_o_s = df_o.merge(
                df_s[
                    [
                        "t_ref_count_standard",
                        "t_alt_count_standard",
                        "t_total_count_standard",
                        "t_variant_frequency_standard",
                        "t_ref_count_forward_standard",
                        "t_alt_count_forward_standard",
                        "t_total_count_forward_standard",
                        "t_ref_count_reverse_standard",
                        "t_alt_count_reverse_standard",
                        "t_total_count_reverse_standard",
                    ]
                ],
                left_index=True,
                right_index=True,
            )
            logger.info(
                "genotype_variants:small_variants:create_all_maf_dataframe:: Successfully created merge data frame for original, standard, simplex and duplex data"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not create merge data frame for original, standard, simplex and duplex data due to error, %s",
                e,
            )
            exit(1)

        try:
            df_o_s.set_index(mutation_key, drop=False, inplace=True)
            logger.debug(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for merged data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for merged data frame, due to error, %s",
                e,
            )
            exit(1)

    # Merge original maf data frame with duplex and simplex and duplex data frame
    df_o_ds = None
    if df_ds is not None and df_o is not None:
        try:
            df_ds = df_ds.reindex(df_o.index)
            df_o_ds = df_o.merge(
                df_ds[
                    [
                        "t_ref_count_fragment_simplex",
                        "t_alt_count_fragment_simplex",
                        "t_total_count_fragment_simplex",
                        "t_vaf_fragment_simplex",
                        "t_ref_count_fragment_duplex",
                        "t_alt_count_fragment_duplex",
                        "t_total_count_fragment_duplex",
                        "t_vaf_fragment_duplex",
                        "t_ref_count_fragment_simplex_duplex",
                        "t_alt_count_fragment_simplex_duplex",
                        "t_total_count_fragment_simplex_duplex",
                        "t_vaf_fragment_simplex_duplex",
                    ]
                ],
                left_index=True,
                right_index=True,
            )
            logger.info(
                "genotype_variants:small_variants:create_all_maf_dataframe:: Successfully created merge data frame for original, simplex and duplex data"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not create merge data frame for original, simplex and duplex data due to error, %s",
                e,
            )
            exit(1)

        try:
            df_o_ds.set_index(mutation_key, drop=False, inplace=True)
            logger.debug(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for merged data frame"
            )
        except:
            e = sys.exc_info()[0]
            logger.error(
                "genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for merged data frame, due to error, %s",
                e,
            )
            exit(1)

    logger.info("Successfully merged data frame")

    if df_o_s_ds is not None:
        return df_o_s_ds
    elif df_o_ds is not None:
        return df_o_ds
    elif df_o_s is not None:
        return df_o_s
    else:
        return df_s_ds
