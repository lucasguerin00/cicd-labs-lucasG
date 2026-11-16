"""Tests unitaires des règles de prix — POINT DE DÉPART (Atelier 1).

Complétez ce fichier : objectif >= 90 % de couverture sur minishop/pricing.py.
"""

from decimal import Decimal
from minishop.pricing import coupon_discount, line_total, money, quote, shipping_cost

import pytest
from minishop.pricing import coupon_discount, line_total, money, quote, shipping_cost

from minishop.pricing import line_total, money, quote

pytestmark = pytest.mark.unit


def test_money_arrondi_commercial():
    """0.125 s'arrondit à 0.13 (ROUND_HALF_UP), pas 0.12."""
    assert money("0.125") == Decimal("0.13")


def test_line_total_sans_remise():
    assert line_total(Decimal("12.50"), 2) == Decimal("25.00")


def test_quote_panier_vide():
    """Un panier vide coûte 0 € : pas de frais de livraison."""
    q = quote([])
    assert q.total == Decimal("0.00")
    assert q.shipping == Decimal("0.00")


# TODO Atelier 1 :
#  - remise volume à partir de 10 unités (et pas à 9 !)
#  - quantités invalides (0, 100, -1, "2", True) -> ValueError   (astuce : @pytest.mark.parametrize)
#  - coupons WELCOME10 / FIXED5 / FREESHIP (seuils inclus/exclus), coupon inconnu, casse
#  - livraison offerte à partir de 50 € APRÈS remise
#  - produit inconnu -> KeyError

# --- Remise volume ---
def test_pas_de_remise_a_9():
    assert line_total(Decimal("10"), 9) == Decimal("90.00")

def test_remise_volume_a_10():
    assert line_total(Decimal("10"), 10) == Decimal("95.00")

# --- Quantités invalides (paramétré) ---
@pytest.mark.parametrize("qty", [0, -1, 100, "2", True])
def test_quantite_invalide(qty):
    with pytest.raises(ValueError):
        line_total(Decimal("10"), qty)

# --- Coupons : valeurs limites (paramétré) ---
@pytest.mark.parametrize("subtotal, attendu", [
    (Decimal("19.99"), Decimal("0.00")),   # juste sous le seuil
    (Decimal("20.00"), Decimal("2.00")),   # seuil inclus
])
def test_welcome10_seuil(subtotal, attendu):
    assert coupon_discount(subtotal, "WELCOME10") == attendu

def test_coupon_inconnu():
    with pytest.raises(ValueError):
        coupon_discount(Decimal("50"), "BIDON")

def test_coupon_insensible_a_la_casse():
    assert coupon_discount(Decimal("20"), " welcome10 ") == Decimal("2.00")

# --- Livraison ---
@pytest.mark.parametrize("montant, attendu", [
    (Decimal("49.99"), Decimal("4.90")),
    (Decimal("50.00"), Decimal("0.00")),
])
def test_livraison_seuil(montant, attendu):
    assert shipping_cost(montant, None, empty=False) == attendu

def test_freeship_livraison_offerte():
    assert shipping_cost(Decimal("10"), "FREESHIP", empty=False) == Decimal("0.00")


@pytest.mark.parametrize("subtotal, attendu", [
    (Decimal("29.99"), Decimal("0.00")),
    (Decimal("30.00"), Decimal("5.00")),
])
def test_fixed5_seuil(subtotal, attendu):
    assert coupon_discount(subtotal, "FIXED5") == attendu

@pytest.mark.parametrize("coupon", [None, ""])
def test_sans_coupon(coupon):
    assert coupon_discount(Decimal("100"), coupon) == Decimal("0.00")

def test_freeship_ne_donne_pas_de_remise():
    assert coupon_discount(Decimal("100"), "FREESHIP") == Decimal("0.00")

def test_livraison_panier_vide():
    assert shipping_cost(Decimal("0"), None, empty=True) == Decimal("0.00")

def test_as_dict_panier_vide():
    d = quote([]).as_dict()
    assert d["lines"] == []
    assert d["total"] == "0.00"
    assert d["coupon"] is None

def test_line_total_arrondi_demi_centime():
    # 0.25 x 10 = 2.50, -5 % = 2.375 -> 2.38 (HALF_UP), pas 2.37
    assert line_total(Decimal("0.25"), 10) == Decimal("2.38")