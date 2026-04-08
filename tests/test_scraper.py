"""
Tests unitaires pour scraper.py
Aucune requête réseau — le HTML est construit directement en mémoire.
"""
from bs4 import BeautifulSoup
from scraper import (
    _extract_price,
    _extract_rating,
    _extract_title,
    get_books_from_page,
    get_categories,
    get_next_page_url,
)


def make_article(title="Un livre", price="£12.99", rating="Three") -> BeautifulSoup:
    """Construit un article HTML minimal représentant un livre."""
    html = f"""
    <article class="product_pod">
        <h3><a href="livre.html" title="{title}">...</a></h3>
        <p class="price_color">{price}</p>
        <p class="star-rating {rating}"></p>
    </article>
    """
    return BeautifulSoup(html, "html.parser").find("article")


class TestExtractTitle:
    def test_titre_normal(self):
        assert _extract_title(make_article(title="Le Petit Prince")) == "Le Petit Prince"

    def test_h3_manquant_retourne_none(self):
        soup = BeautifulSoup("<article class='product_pod'></article>", "html.parser").find("article")
        assert _extract_title(soup) is None

    def test_attribut_title_manquant_retourne_none(self):
        soup = BeautifulSoup(
            "<article class='product_pod'><h3><a href='x.html'>...</a></h3></article>",
            "html.parser"
        ).find("article")
        assert _extract_title(soup) is None


class TestExtractPrice:
    def test_prix_normal(self):
        assert _extract_price(make_article(price="£19.99")) == "£19.99"

    def test_balise_manquante_retourne_none(self):
        soup = BeautifulSoup("<article class='product_pod'></article>", "html.parser").find("article")
        assert _extract_price(soup) is None


class TestExtractRating:
    def test_note_normale(self):
        assert _extract_rating(make_article(rating="Five")) == "Five"

    def test_balise_manquante_retourne_none(self):
        soup = BeautifulSoup("<article class='product_pod'></article>", "html.parser").find("article")
        assert _extract_rating(soup) is None

    def test_une_seule_classe_retourne_none(self):
        soup = BeautifulSoup(
            "<article class='product_pod'><p class='star-rating'></p></article>",
            "html.parser"
        ).find("article")
        assert _extract_rating(soup) is None


class TestGetNextPageUrl:
    def test_bouton_suivant_present(self):
        html = "<ul><li class='next'><a href='page-2.html'>next</a></li></ul>"
        soup = BeautifulSoup(html, "html.parser")
        current = "https://books.toscrape.com/catalogue/category/books/fiction_10/index.html"
        result = get_next_page_url(soup, current)
        assert result == "https://books.toscrape.com/catalogue/category/books/fiction_10/page-2.html"

    def test_pas_de_bouton_suivant(self):
        soup = BeautifulSoup("<ul></ul>", "html.parser")
        assert get_next_page_url(soup, "https://example.com/page-1.html") is None


class TestGetCategories:
    def test_categories_normales(self):
        html = """
        <ul class="nav-list">
            <li><a href="catalogue/index.html">Books</a></li>
            <li><a href="catalogue/category/books/fiction_10/index.html">Fiction</a></li>
            <li><a href="catalogue/category/books/mystery_3/index.html">Mystery</a></li>
        </ul>
        """
        soup = BeautifulSoup(html, "html.parser")
        categories = get_categories(soup)
        assert len(categories) == 2
        assert categories[0]["name"] == "Fiction"
        assert "fiction_10" in categories[0]["url"]

    def test_menu_absent_retourne_liste_vide(self):
        soup = BeautifulSoup("<div></div>", "html.parser")
        assert get_categories(soup) == []


class TestGetBooksFromPage:
    def test_plusieurs_livres(self):
        html = """
        <section>
            <article class="product_pod">
                <h3><a title="Livre A">...</a></h3>
                <p class="price_color">£10.00</p>
                <p class="star-rating Two"></p>
            </article>
            <article class="product_pod">
                <h3><a title="Livre B">...</a></h3>
                <p class="price_color">£20.00</p>
                <p class="star-rating Four"></p>
            </article>
        </section>
        """
        soup = BeautifulSoup(html, "html.parser")
        books = get_books_from_page(soup, "Fiction")
        assert len(books) == 2
        assert books[0]["title"] == "Livre A"
        assert books[1]["category"] == "Fiction"

    def test_aucun_article_retourne_liste_vide(self):
        soup = BeautifulSoup("<section></section>", "html.parser")
        assert get_books_from_page(soup, "Fiction") == []
