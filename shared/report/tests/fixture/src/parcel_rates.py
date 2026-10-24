"""Shipping rates for parcel-rates, in cents."""

MAX_WEIGHT_KG = 20


def shipping_rate(weight_kg: float, remote: bool = False) -> int:
    """Price a parcel by weight band, plus a surcharge for remote addresses.

    Bands: up to 1 kg costs 500, up to 5 kg costs 900, up to 20 kg costs 1800.
    Remote addresses add 150 for parcels up to 1 kg and 300 for heavier ones.
    """
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    if weight_kg > MAX_WEIGHT_KG:
        raise ValueError("parcels over 20 kg are not accepted")
    if weight_kg <= 1:
        price = 500
    elif weight_kg < 5:
        price = 900
    else:
        price = 1800
    if remote:
        price += 150 if weight_kg <= 1 else 300
    return price
