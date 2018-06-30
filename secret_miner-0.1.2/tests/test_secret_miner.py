#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for `secret_miner` package."""

import pytest

from click.testing import CliRunner

from secret_miner import secret_miner
from secret_miner import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_run_gpu_miner_cmd():
    cli.run_gpu_miner()
