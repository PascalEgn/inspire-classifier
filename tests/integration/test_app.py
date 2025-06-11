# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2024 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

import json
from math import isclose

import pytest


def test_health_check(app_client):
    assert app_client.get("/api/health").status_code == 200

@pytest.mark.usefixtures("_trained_pipeline")
def test_classifier_accepts_only_post(trained_app_client):
    assert (
        trained_app_client.post(
            "/api/predict/coreness",
            json=dict(title="foo bar", abstract="foobar foobar"),
        ).status_code
        == 200
    )
    assert trained_app_client.get("/api/predict/coreness").status_code == 405

@pytest.mark.usefixtures("_trained_pipeline")
def test_classifier(trained_app_client):
    response = trained_app_client.post(
        "/api/predict/coreness", json=dict(title="foo bar", abstract="foobar foobar")
    )

    result = json.loads(response.data)

    assert response.status_code == 200
    assert set(result.keys()) == {"prediction", "scores"}
    assert result["prediction"] in {"rejected", "non_core", "core"}
    assert set(result["scores"].keys()) == {"rejected", "non_core", "core"}
    assert isclose(
        result["scores"]["rejected"]
        + result["scores"]["non_core"]
        + result["scores"]["core"],
        1.0,
        abs_tol=1e-2,
    )

@pytest.mark.usefixtures("_trained_pipeline")
def test_classifier_serializes_input(app_client):
    assert (
        app_client.post("/api/predict/coreness", json=dict(title="foo bar")).status_code
        == 422
    )
    assert (
        app_client.post(
            "/api/predict/coreness", json=dict(abstract="foo bar")
        ).status_code
        == 422
    )

@pytest.mark.usefixtures("_trained_pipeline")
def test_classifier_doesnt_accept_extra_fields(app_client):
    assert (
        app_client.post(
            "/api/predict/coreness",
            json=dict(title="foo bar", abstract="foo bar", author="foo"),
        ).status_code
        == 422
    )
