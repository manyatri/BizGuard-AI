import sys
import os
import uuid

# Ensure backend directory is in python sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.database import SessionLocal, init_db
from app.models.catalog import Category, Product, ProductVariant, Inventory
from sqlalchemy import select

def seed():
    print("Initializing database schema...")
    init_db()

    with SessionLocal() as db:
        # Check if already seeded
        existing_cats = db.scalars(select(Category)).first()
        if existing_cats:
            print("Database already contains catalog records. Skipping seed.")
            return

        print("Seeding luxury clothing catalog categories...")
        cat_ethnic = Category(id=str(uuid.uuid4()), name="Ethnic Wear", slug="ethnic-wear")
        cat_western = Category(id=str(uuid.uuid4()), name="Western Dresses", slug="western-dresses")
        cat_tops = Category(id=str(uuid.uuid4()), name="Tops & Blouses", slug="tops-blouses")
        cat_denim = Category(id=str(uuid.uuid4()), name="Denim & Trousers", slug="denim-trousers")
        
        db.add_all([cat_ethnic, cat_western, cat_tops, cat_denim])
        db.commit()

        print("Seeding clothing products, sizes, color variants and inventory bins...")
        
        # 1. The Core Hero Item: Anarkali Embroidered Black Kurti
        p_kurti = Product(
            id=str(uuid.uuid4()),
            category_id=cat_ethnic.id,
            title="Anarkali Embroidered Black Kurti",
            base_sku="BG-KRT-BLK",
            description="Handcrafted pure Chanderi silk kurti featuring traditional gold Zari botanical embroidery, flared silhouette, and mandarin collar.",
            fabric="100% Chanderi Silk with Cotton Silk Lining",
            base_price=119.00,
            image_url="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042056_1a704ff7-b0e5-4a9f-bbda-62392b819fb6.png&w=1200&q=85",
            is_active=True
        )
        db.add(p_kurti)
        db.flush()

        kurti_sizes = [
            ("XS", 25, 2, "BIN-E1-04"),
            ("S", 40, 5, "BIN-E1-05"),
            ("M", 18, 0, "BIN-E1-06"),   # Target item for the hackathon scenario!
            ("L", 12, 2, "BIN-E1-07"),   # Buggy destination item!
            ("XL", 8, 1, "BIN-E1-08"),
            ("XXL", 4, 0, "BIN-E1-09")
        ]

        for size, on_hand, reserved, bin_loc in kurti_sizes:
            var = ProductVariant(
                id=str(uuid.uuid4()),
                product_id=p_kurti.id,
                sku=f"BG-KRT-BLK-{size}",
                size=size,
                color="Jet Black",
                color_code="#111111",
                price_adjustment=0.00,
                barcode=f"890441029{size}9"
            )
            db.add(var)
            db.flush()

            inv = Inventory(
                id=str(uuid.uuid4()),
                variant_id=var.id,
                quantity_on_hand=on_hand,
                quantity_reserved=reserved,
                reorder_threshold=5,
                warehouse_bin=bin_loc,
                version=1
            )
            db.add(inv)

        # 2. Sage Pleated Maxi Gown
        p_gown = Product(
            id=str(uuid.uuid4()),
            category_id=cat_western.id,
            title="Sage Pleated Maxi Gown",
            base_sku="BG-DRS-SGE",
            description="Floor-length evening dress in Italian pleated georgette with crossover bodice and softly gathered empire waist.",
            fabric="100% Italian Pleated Georgette",
            base_price=220.00,
            image_url="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042057_080e85b0-b4aa-4072-8eb9-2304c7baf42b.png&w=1200&q=85",
            is_active=True
        )
        db.add(p_gown)
        db.flush()

        for size, on_hand, reserved, bin_loc in [("XS", 15, 1, "BIN-W2-01"), ("S", 22, 3, "BIN-W2-02"), ("M", 30, 4, "BIN-W2-03"), ("L", 14, 2, "BIN-W2-04")]:
            var = ProductVariant(
                id=str(uuid.uuid4()),
                product_id=p_gown.id,
                sku=f"BG-DRS-SGE-{size}",
                size=size,
                color="Sage Green",
                color_code="#8A9A86",
                price_adjustment=0.00,
                barcode=f"890441031{size}2"
            )
            db.add(var)
            db.flush()
            inv = Inventory(
                id=str(uuid.uuid4()),
                variant_id=var.id,
                quantity_on_hand=on_hand,
                quantity_reserved=reserved,
                warehouse_bin=bin_loc
            )
            db.add(inv)

        # 3. Champagne Satin Trench Coat Dress
        p_trench = Product(
            id=str(uuid.uuid4()),
            category_id=cat_western.id,
            title="Champagne Satin Trench Coat Dress",
            base_sku="BG-TRN-CHP",
            description="Double-breasted trench silhouette in luminous heavyweight silk satin with matching horn buckles and notched lapel.",
            fabric="Heavyweight Mulberry Silk Satin",
            base_price=235.00,
            image_url="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042056_1a704ff7-b0e5-4a9f-bbda-62392b819fb6.png&w=1200&q=85",
            is_active=True
        )
        db.add(p_trench)
        db.flush()

        for size, on_hand, reserved, bin_loc in [("S", 12, 1, "BIN-W3-01"), ("M", 18, 2, "BIN-W3-02"), ("L", 10, 0, "BIN-W3-03")]:
            var = ProductVariant(
                id=str(uuid.uuid4()),
                product_id=p_trench.id,
                sku=f"BG-TRN-CHP-{size}",
                size=size,
                color="Champagne",
                color_code="#EED9C4",
                price_adjustment=0.00,
                barcode=f"890441042{size}8"
            )
            db.add(var)
            db.flush()
            inv = Inventory(
                id=str(uuid.uuid4()),
                variant_id=var.id,
                quantity_on_hand=on_hand,
                quantity_reserved=reserved,
                warehouse_bin=bin_loc
            )
            db.add(inv)

        # 4. Blush Billow Sleeve Silk Blouse
        p_top = Product(
            id=str(uuid.uuid4()),
            category_id=cat_tops.id,
            title="Blush Billow Sleeve Silk Blouse",
            base_sku="BG-TOP-BLS",
            description="Voluminous romantic raglan sleeve top tailored from fluid washed crepe with mother-of-pearl buttons.",
            fabric="100% Washed Silk Crepe",
            base_price=86.00,
            image_url="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042057_080e85b0-b4aa-4072-8eb9-2304c7baf42b.png&w=1200&q=85",
            is_active=True
        )
        db.add(p_top)
        db.flush()

        for size, on_hand, reserved, bin_loc in [("XS", 20, 2, "BIN-T1-01"), ("S", 35, 3, "BIN-T1-02"), ("M", 28, 1, "BIN-T1-03"), ("L", 16, 0, "BIN-T1-04")]:
            var = ProductVariant(
                id=str(uuid.uuid4()),
                product_id=p_top.id,
                sku=f"BG-TOP-BLS-{size}",
                size=size,
                color="Blush Pink",
                color_code="#E8C5C8",
                price_adjustment=0.00,
                barcode=f"890441053{size}5"
            )
            db.add(var)
            db.flush()
            inv = Inventory(
                id=str(uuid.uuid4()),
                variant_id=var.id,
                quantity_on_hand=on_hand,
                quantity_reserved=reserved,
                warehouse_bin=bin_loc
            )
            db.add(inv)

        # 5. Vintage Washed Wide Leg Selvedge Denim
        p_denim = Product(
            id=str(uuid.uuid4()),
            category_id=cat_denim.id,
            title="Vintage Washed Wide Leg Selvedge Denim",
            base_sku="BG-JNS-VNT",
            description="High-rise wide leg jean crafted on vintage shuttle looms from 14oz Japanese selvedge denim with natural indigo wash.",
            fabric="100% Cotton 14oz Selvedge Denim",
            base_price=140.00,
            image_url="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042056_1a704ff7-b0e5-4a9f-bbda-62392b819fb6.png&w=1200&q=85",
            is_active=True
        )
        db.add(p_denim)
        db.flush()

        for size, on_hand, reserved, bin_loc in [("28", 14, 1, "BIN-D1-01"), ("30", 25, 4, "BIN-D1-02"), ("32", 30, 2, "BIN-D1-03"), ("34", 18, 1, "BIN-D1-04"), ("36", 8, 0, "BIN-D1-05")]:
            var = ProductVariant(
                id=str(uuid.uuid4()),
                product_id=p_denim.id,
                sku=f"BG-JNS-VNT-{size}",
                size=size,
                color="Indigo Vintage Wash",
                color_code="#4A6572",
                price_adjustment=0.00,
                barcode=f"890441064{size}1"
            )
            db.add(var)
            db.flush()
            inv = Inventory(
                id=str(uuid.uuid4()),
                variant_id=var.id,
                quantity_on_hand=on_hand,
                quantity_reserved=reserved,
                warehouse_bin=bin_loc
            )
            db.add(inv)

        db.commit()
        print("Successfully seeded clothing catalog with sizes, colors, and inventory!")

if __name__ == "__main__":
    seed()
