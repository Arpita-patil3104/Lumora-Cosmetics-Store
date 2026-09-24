from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = "Create LUMORA categories and products"

    def handle(self, *args, **kwargs):

        categories_data = [
            ("Makeup", "makeup", "Beautiful makeup essentials"),
            ("Skincare", "skincare", "Glow and care for your skin"),
            ("Haircare", "haircare", "Healthy and beautiful hair"),
            ("Fragrance", "fragrance", "Elegant fragrances for every day"),
            ("Bath & Body", "bath-body", "Everyday body care essentials"),
            ("Wellness", "wellness", "Self-care and wellness products"),
        ]

        categories = {}

        for name, slug, description in categories_data:
            category, created = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": description,
                    "is_active": True,
                },
            )

            categories[slug] = category

        products_data = [
            {
                "category": "skincare",
                "name": "Glow Hydrating Face Serum",
                "slug": "glow-hydrating-face-serum",
                "brand": "LUMORA",
                "description": "A lightweight hydrating serum for soft, glowing and healthy-looking skin.",
                "price": 899,
                "sale_price": 699,
                "stock": 50,
                "rating": 4.7,
                "reviews_count": 128,
                "is_featured": True,
                "is_new_arrival": True,
            },
            {
                "category": "skincare",
                "name": "Radiant Skin Moisturizer",
                "slug": "radiant-skin-moisturizer",
                "brand": "LUMORA",
                "description": "A nourishing daily moisturizer that keeps skin smooth and hydrated.",
                "price": 749,
                "sale_price": 599,
                "stock": 65,
                "rating": 4.6,
                "reviews_count": 96,
                "is_featured": True,
            },
            {
                "category": "skincare",
                "name": "Daily Shield SPF 50 Sunscreen",
                "slug": "daily-shield-spf-50-sunscreen",
                "brand": "LUMORA",
                "description": "Lightweight SPF 50 sunscreen for everyday protection.",
                "price": 799,
                "sale_price": 649,
                "stock": 80,
                "rating": 4.8,
                "reviews_count": 214,
                "is_bestseller": True,
            },
            {
                "category": "makeup",
                "name": "Velvet Matte Lip Color",
                "slug": "velvet-matte-lip-color",
                "brand": "LUMORA",
                "description": "Smooth matte lip color with a comfortable finish.",
                "price": 499,
                "sale_price": 399,
                "stock": 100,
                "rating": 4.5,
                "reviews_count": 87,
                "is_bestseller": True,
            },
            {
                "category": "makeup",
                "name": "Soft Glow Liquid Blush",
                "slug": "soft-glow-liquid-blush",
                "brand": "LUMORA",
                "description": "Buildable liquid blush for a natural healthy glow.",
                "price": 599,
                "sale_price": 499,
                "stock": 70,
                "rating": 4.6,
                "reviews_count": 74,
                "is_new_arrival": True,
            },
            {
                "category": "makeup",
                "name": "Everyday Nude Eyeshadow Palette",
                "slug": "everyday-nude-eyeshadow-palette",
                "brand": "LUMORA",
                "description": "Versatile nude shades perfect for everyday makeup looks.",
                "price": 999,
                "sale_price": 799,
                "stock": 45,
                "rating": 4.7,
                "reviews_count": 143,
                "is_featured": True,
            },
            {
                "category": "haircare",
                "name": "Silk Repair Hair Serum",
                "slug": "silk-repair-hair-serum",
                "brand": "LUMORA",
                "description": "A lightweight hair serum that helps smooth and nourish dry hair.",
                "price": 649,
                "sale_price": 549,
                "stock": 60,
                "rating": 4.5,
                "reviews_count": 91,
                "is_bestseller": True,
            },
            {
                "category": "haircare",
                "name": "Nourish & Shine Shampoo",
                "slug": "nourish-shine-shampoo",
                "brand": "LUMORA",
                "description": "Gentle everyday shampoo for clean, soft and shiny hair.",
                "price": 599,
                "sale_price": 499,
                "stock": 75,
                "rating": 4.4,
                "reviews_count": 63,
            },
            {
                "category": "fragrance",
                "name": "Bloom Eau De Parfum",
                "slug": "bloom-eau-de-parfum",
                "brand": "LUMORA",
                "description": "A graceful floral fragrance with a fresh elegant finish.",
                "price": 1299,
                "sale_price": 1099,
                "stock": 35,
                "rating": 4.8,
                "reviews_count": 119,
                "is_featured": True,
                "is_bestseller": True,
            },
            {
                "category": "fragrance",
                "name": "Velvet Rose Body Mist",
                "slug": "velvet-rose-body-mist",
                "brand": "LUMORA",
                "description": "A soft floral body mist for an effortless everyday fragrance.",
                "price": 599,
                "sale_price": 449,
                "stock": 90,
                "rating": 4.5,
                "reviews_count": 52,
                "is_new_arrival": True,
            },
            {
                "category": "bath-body",
                "name": "Silky Body Lotion",
                "slug": "silky-body-lotion",
                "brand": "LUMORA",
                "description": "Rich yet lightweight body lotion for smooth hydrated skin.",
                "price": 499,
                "sale_price": 399,
                "stock": 100,
                "rating": 4.6,
                "reviews_count": 105,
                "is_bestseller": True,
            },
            {
                "category": "bath-body",
                "name": "Vanilla Cloud Body Wash",
                "slug": "vanilla-cloud-body-wash",
                "brand": "LUMORA",
                "description": "A creamy vanilla body wash for a refreshing bathing experience.",
                "price": 449,
                "sale_price": 349,
                "stock": 85,
                "rating": 4.4,
                "reviews_count": 68,
            },
        ]

        for data in products_data:
            category = categories[data.pop("category")]

            Product.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    **data,
                    "category": category,
                    "is_active": True,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "LUMORA seed data created successfully! 6 categories and 12 products added."
            )
        )