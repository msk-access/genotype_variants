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
logger.info("genotype:variants:small_variants::create_all_maf_dataframe:: Generating duplex simplex dataframe")
# Adopted from Maysun script
def create_all_maf_dataframe(original_dataframe, standard_dataframe, simplex_duplex_dataframe):
    """Code to merge all the data frames generated from MAF files into one data frame
    """
    np.seterr(divide="ignore", invalid="ignore")
    mutation_key = [
        "Chromosome",
        "Start_Position",
        "End_Position",
        "Reference_Allele",
        "Tumor_Seq_Allele1",
        "Tumor_Seq_Allele2",
    ]
    (df_ds,df_s,df_o) = None
    if(simplex_duplex_dataframe):
        df_ds = simplex_duplex_dataframe.copy()
        df_ds.sort_values(["Chromosome", "Start_Position", "End_Position"],inplace=True)
    if(standard_dataframe):
        df_s = standard_dataframe.copy()
        df_s.sort_values(["Chromosome", "Start_Position", "End_Position"],inplace=True)
    if(original_dataframe):
        df_o = original_dataframe.copy()
        df_o.sort_values(["Chromosome", "Start_Position", "End_Position"],inplace=True)

    # Prep Simplex duplex
    if(df_ds):
        try:
            df_ds.rename(
                columns={
                    "t_alt_count_fragment": "t_alt_count_fragment_simplex_duplex",
                    "t_ref_count_fragment": "t_ref_count_fragment_simplex_duplex",
                    "t_total_count_fragment": "t_total_count_fragment_simplex_duplex",
                    "t_vaf_fragment": "t_vaf_fragment_simplex_duplex",

                },
                inplace=True,
            )
            logger.debug("genotype:variants:small_variants:create_all_maf_dataframe::Successfully renamed column names in simplex duplex data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants::create_all_maf_dataframe:: Could not rename column names in simplex duplex data frame due to error, %s", e)
            exit(1)

        try:
            df_ds["Tumor_Sample_Barcode"] = df_ds["Tumor_Sample_Barcode"].str.replace(
            "-SIMPLEX-DUPLEX", "")
            logger.debug("genotype_variants:small_variants:create_all_maf_dataframe:: Successfully renamed samples in Tumor_Sample_Barcode for simplex duplex data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not rename samples in Tumor_Sample_Barcode for simplex duplex data frame, due to error, %s", e)

        try:
            df_ds.set_index("Tumor_Sample_Barcode", append=True, drop=False, inplace=True)
            logger.debug("genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for simplex duplex data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for simplex duplex data frame, due to error, %s", e)
        
    # Prep Standard
    if(df_s):
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
            logger.debug("genotype:variants:small_variants:create_all_maf_dataframe::Successfully renamed column names in standard data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants::create_all_maf_dataframe:: Could not rename column names in standard data frame due to error, %s", e)
            exit(1)

        try:
            df_s["t_total_count_reverse_standard"] = df_s["t_total_count_standard"] - df_ds["t_total_count_forward_standard"]
            df_s["t_ref_count_reverse_standard"] = df_s["t_total_count_reverse_standard"] - df_ds["t_ref_count_forward_standard"]
            df_s["t_alt_count_reverse_standard"] = df_s["t_total_count_reverse_standard"] - df_ds["t_alt_count_forward_standard"]
            logger.debug("genotype:variants:small_variants::create_all_maf_dataframe:: Successfully generated reverse count columns in standard data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants::create_all_maf_dataframe:: Could not generate reverse count columns in standard data frame due to error, %s", e)
            exit(1)
        
        try:
            df_d["Tumor_Sample_Barcode"] = df_d["Tumor_Sample_Barcode"].str.replace(
            "-STANDARD", "")
            logger.debug("genotype_variants:small_variants:create_all_maf_dataframe:: Successfully renamed samples in Tumor_Sample_Barcode for standard data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not rename samples in Tumor_Sample_Barcode for standard data frame, due to error, %s", e)

        try:
            df_d.set_index("Tumor_Sample_Barcode", append=True, drop=False, inplace=True)
            logger.debug("genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for standard data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for standard data frame, due to error, %s", e)
        
    #Prep Original
    if(df_o):
        try:
            df_o.set_index("Tumor_Sample_Barcode", append=True, drop=False, inplace=True)
            logger.debug("genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for original data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for original data frame, due to error, %s", e)
        
    # Merge STANDARD with DUPLEX-SIMPLEX data frame
    df_s_ds = None
    if(df_ds and df_s):
        try:
            df_s_ds = df_s.merge(
                df_ds[[
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
                    "t_vaf_fragment_simplex_duplex"
                ]],
                left_index=True,
                right_index=True,
            )
            logger.info("genotype_variants:small_variants:create_all_maf_dataframe:: Successfully created merge data frame for standard, simplex and duplex data")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not create merge data frame for standard, simplex and duplex data due to error, %s", e)
            exit(1)
        try:
            df_s_ds.set_index(mutation_key, drop=False, inplace=True)
            logger.debug("genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for merged data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for merged data frame, due to error, %s", e)
    
    # Merge Original with STANDARD-DUPLEX-SIMPLEX data frame
    df_s_ds = None
    if(df_s_ds):
        try:
            df_o_s_ds = df_o.merge(
                df_s_ds[[
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
                    "t_vaf_fragment_simplex_duplex"
                    ]],
                left_index=True,
                right_index=True,
            )
            logger.info("genotype_variants:small_variants:create_all_maf_dataframe:: Successfully created merge data frame for original, standard, simplex and duplex data")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not create merge data frame for original, standard, simplex and duplex data due to error, %s", e)
            exit(1)
    
        try:
            df_o_s_ds.set_index(mutation_key, drop=False, inplace=True)
            logger.debug("genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for merged data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for merged data frame, due to error, %s", e)
    
    df_o_ds = None
    if(df_ds, df_o):
        try:
            df_o_ds = df_o.merge(
                df_ds[[
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
                    "t_vaf_fragment_simplex_duplex"
                    ]],
                left_index=True,
                right_index=True,
            )
            logger.info("genotype_variants:small_variants:create_all_maf_dataframe:: Successfully created merge data frame for original, simplex and duplex data")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not create merge data frame for original, simplex and duplex data due to error, %s", e)
            exit(1)
    
        try:
            df_o_ds.set_index(mutation_key, drop=False, inplace=True)
            logger.debug("genotype:variants:small_variants:create_all_maf_dataframe:: Successfully reset the index for merged data frame")
        except:
            e = sys.exc_info()[0]
            logger.error("genotype:variants:small_variants:create_all_maf_dataframe:: Could not reset the index for merged data frame, due to error, %s", e)
    

    logger.info("Successfully merged data frame")
    
    if(df_o_s_ds)
        return df_o_s_ds
    elif(df_o_ds):
        return df_o_ds
    else:
        return df_s_ds
