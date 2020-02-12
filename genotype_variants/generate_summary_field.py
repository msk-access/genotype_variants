import logging
import numpy as np

"""
generate_summary_field
~~~~~~~~~~~~~~~
:Description: Code to Generate Summary Field
"""
"""
Created on February 10, 2020
Description: Code to Generate Summary Field
@author: Ronak H Shah & Maysun Hasan
"""
# Making logging possible
logger = logging.getLogger("genotype_variants")


def generate_summary_field(df_fillout):
    """Code to Generate Summary Field"""
    np.seterr(divide="ignore", invalid="ignore")
    df_fillout = df_fillout.copy()
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
