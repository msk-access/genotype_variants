#!/usr/bin/env python

"""Tests for `genotype_variants` package."""


import unittest
import pandas as pd

from genotype_variants.commands import small_variants
from genotype_variants.create_duplex_simplex_dataframe import (
    create_duplex_simplex_dataframe as cdsd,
)


class TestGenotype_variants(unittest.TestCase):
    """Tests for `genotype_variants` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.mutation_key = [
            "Chromosome",
            "Start_Position",
            "End_Position",
            "Reference_Allele",
            "Tumor_Seq_Allele2",
        ]
        self.d_maf = pd.read_csv(
            "tests/test_data/C-100000-L002-d02-DUPLEX_genotyped.maf",
            sep="\t",
            header="infer",
        )
        self.s_maf = pd.read_csv(
            "tests/test_data/C-100000-L002-d02-SIMPLEX_genotyped.maf",
            sep="\t",
            header="infer",
        )
        self.d_maf = self.d_maf.set_index(self.mutation_key, drop=False)
        self.s_maf = self.s_maf.set_index(self.mutation_key, drop=False)

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass

    def test_command_line_interface(self):
        """Test the CLI."""
        pass
        # runner = CliRunner()
        # result = runner.invoke(cli.main)
        # assert result.exit_code == 0
        # assert 'genotype_variants.cli.main' in result.output
        # help_result = runner.invoke(cli.main, ['--help'])
        # assert help_result.exit_code == 0
        # assert '--help  Show this message and exit.' in help_result.output

    def test_merge_simplex_duplex(self):
        """
        Test simplex-duplex MAF generation

        :return:
        """
        df_merge = cdsd(self.s_maf, self.d_maf)
        df_merge = df_merge.sort_index()
        expected = pd.read_csv(
            "tests/test_data/C-100000-L002-d02-SIMPLEX-DUPLEX_genotyped.maf", sep="\t"
        )
        expected = expected.set_index(self.mutation_key, drop=False)
        expected = expected.sort_index()
        pd.testing.assert_frame_equal(df_merge, expected)

        # SNP
        snp_index = (16, 68842732, 68842732, "A", "C")
        assert df_merge.loc[snp_index]["t_ref_count_fragment_simplex_duplex"] == 2737
        assert df_merge.loc[snp_index]["t_alt_count_fragment_simplex_duplex"] == 3
        assert df_merge.loc[snp_index]["t_total_count_fragment_simplex_duplex"] == 2740
        # # INS
        # insertion_index = (18, 48584855, 48584855, 'A',   'TTT')
        # assert df_merge.loc[insertion_index]['t_ref_count_fragment'] == 694
        # assert df_merge.loc[insertion_index]['t_alt_count_fragment'] == 4
        # assert df_merge.loc[insertion_index]['t_total_count_fragment'] == 698
        # DEL
        deletion_index = (5, 1295253, 1295262, "GGGTCGGGAC", "-")
        assert (
            df_merge.loc[deletion_index]["t_ref_count_fragment_simplex_duplex"] == 537
        )
        assert df_merge.loc[deletion_index]["t_alt_count_fragment_simplex_duplex"] == 0
        assert (
            df_merge.loc[deletion_index]["t_total_count_fragment_simplex_duplex"] == 537
        )
