"""Shared utility helpers used across blueprints."""
import re


def slugify(text: str) -> str:
    """Convert any text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text or 'item'


def unique_product_slug(name: str, product_id: int | None = None) -> str:
    """
    Generate a unique slug for a product name.
    If product_id is given, the existing product with that id is excluded
    from the uniqueness check (for edits).
    """
    from app.models import Product
    base = slugify(name)
    slug, n = base, 1
    while True:
        q = Product.query.filter_by(slug=slug)
        if product_id:
            q = q.filter(Product.id != product_id)
        if not q.first():
            return slug
        n += 1
        slug = f'{base}-{n}'
