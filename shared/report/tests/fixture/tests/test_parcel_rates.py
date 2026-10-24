import pytest

from src.parcel_rates import shipping_rate


def test_parcel_of_half_a_kilo_costs_500():
    assert shipping_rate(0.5) == 500


def test_parcel_of_exactly_1_kg_stays_in_the_lightest_band():
    assert shipping_rate(1) == 500


def test_parcel_of_3_kg_costs_900():
    assert shipping_rate(3) == 900


def test_parcel_of_exactly_5_kg_stays_in_the_middle_band():
    assert shipping_rate(5) == 900


def test_parcel_of_12_kg_costs_1800():
    assert shipping_rate(12) == 1800


def test_remote_light_parcel_adds_150():
    assert shipping_rate(0.5, remote=True) == 650


def test_remote_heavy_parcel_adds_300():
    assert shipping_rate(12, remote=True) == 2100


def test_zero_weight_is_rejected():
    with pytest.raises(ValueError, match="weight must be positive"):
        shipping_rate(0)


def test_parcel_over_20_kg_is_rejected():
    with pytest.raises(ValueError, match="over 20 kg"):
        shipping_rate(20.5)
