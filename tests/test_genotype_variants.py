#!/usr/bin/env python

"""Tests for `genotype_variants` package."""


import unittest
import pandas as pd
from click.testing import CliRunner

from genotype_variants.commands import small_variants
from genotype_variants import cli


class TestGenotype_variants(unittest.TestCase):
    """Tests for `genotype_variants` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.d_maf = pd.read_csv('test_data/test_duplex.maf', sep="\t", header="infer", index_col=[0,4])
        self.s_maf = pd.read_csv('test_data/test_simplex.maf', sep="\t", header="infer", index_col=[0,4])

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        return
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'genotype_variants.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

    def test_merge_simplex_duplex(self):
        """
        Test simplex-duplex MAF generation

        :return:
        """
        df_merge = small_variants.create_duplexsimplex(self.d_maf, self.s_maf)
        expected = pd.read_csv('test_data/expected.maf', sep='\t', index_col=[0,4])
        pd.testing.assert_frame_equal(df_merge, expected)
        print('heres')
       # assert df_merge
        # todo: asserts for the expected merged numbers?
