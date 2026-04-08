"""
Tests unitaires pour transform.py
"""
import pytest
from transform import clean_price, clean_rating, transform_books


class TestCleanPrice:
    def test_prix_normal(self):
        assert clean_price("£12.99") == 12.99

    def test_prix_entier(self):
        assert clean_price("£10.00") == 10.0

    def test_prix_avec_artefact_encodage(self):
        # "Â£" est un artefact fréquent de mauvais encodage UTF-8
        assert clean_price("Â£51.77") == 51.77

    def test_none_retourne_none(self):
        assert clean_price(None) is None

    def test_chaine_vide_retourne_none(self):
        assert clean_price("") is None

    def test_valeur_non_numerique_retourne_none(self):
        assert clean_price("£abc") is None

    def test_type_non_string_retourne_none(self):
        assert clean_price(12.99) is None


class TestCleanRating:
    @pytest.mark.parametrize("raw,expected", [
        ("One",   1),
        ("Two",   2),
        ("Three", 3),
        ("Four",  4),
        ("Five",  5),
    ])
    def test_toutes_les_notes_valides(self, raw, expected):
        assert clean_rating(raw) == expected

    def test_note_inconnue_retourne_none(self):
        assert clean_rating("Six") is None

    def test_none_retourne_none(self):
        assert clean_rating(None) is None

    def test_casse_incorrecte_retourne_none(self):
        assert clean_rating("three") is None


class TestTransformBooks:
    def test_liste_vide_retourne_dataframe_vide(self):
        df = transform_books([])
        assert df.empty
        assert list(df.columns) == ["title", "price", "rating", "category", "scraped_at"]

    def test_transformation_normale(self):
        raw = [{"title": "Un livre", "price": "£9.99", "rating": "Four", "category": "Fiction"}]
        df = transform_books(raw)
        assert len(df) == 1
        assert df.iloc[0]["price"] == 9.99
        assert df.iloc[0]["rating"] == 4

    def test_colonne_scraped_at_presente(self):
        raw = [{"title": "Un livre", "price": "£9.99", "rating": "Two", "category": "Fiction"}]
        df = transform_books(raw)
        assert "scraped_at" in df.columns

    def test_ligne_sans_titre_supprimee(self):
        raw = [
            {"title": "Valide",  "price": "£5.00", "rating": "One",  "category": "Art"},
            {"title": None,      "price": "£3.00", "rating": "Two",  "category": "Art"},
        ]
        df = transform_books(raw)
        assert len(df) == 1
        assert df.iloc[0]["title"] == "Valide"
