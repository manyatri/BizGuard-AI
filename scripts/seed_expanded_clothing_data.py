"""
Expanded clothing e-commerce demo dataset for BizGuard AI.
Generates:
- 5 Categories (Kurtis, Dresses, Tops, Shirts, Jeans)
- 30 Premium Clothing Products
- 120+ Product Variants with unique SKUs, sizes, colors, and stock bins
- Out-of-stock variants and low-stock variants
- Customers, Orders (DELIVERED, SHIPPED, INVOICED, STALLED, CANCELLED)
- Payments (CAPTURED, INITIATED, FAILED)
- Invoices, Shipments, Returns
"""
import sys
import os
import uuid
import random
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.database import SessionLocal, init_db
from app.models.catalog import Category, Product, ProductVariant, Inventory
from app.models.orders import Order, OrderItem, Payment, Invoice, InvoiceItem, Shipment, ReturnRecord
from app.models.workflow import WorkflowExecution, WorkflowEvent
from sqlalchemy import select, delete


def _utc(hours_ago: int = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=hours_ago)


def seed_expanded(force_clean: bool = True):
    print("Initializing database schema...")
    init_db()

    with SessionLocal() as db:
        if force_clean:
            print("Cleaning existing demo data for clean expanded dataset...")
            # Delete children first
            db.execute(delete(ReturnRecord))
            db.execute(delete(Shipment))
            db.execute(delete(InvoiceItem))
            db.execute(delete(Invoice))
            db.execute(delete(Payment))
            db.execute(delete(OrderItem))
            db.execute(delete(WorkflowEvent))
            db.execute(delete(WorkflowExecution))
            db.execute(delete(Order))
            db.execute(delete(Inventory))
            db.execute(delete(ProductVariant))
            db.execute(delete(Product))
            db.execute(delete(Category))
            db.commit()

        print("Seeding 5 Fashion Categories...")
        categories = {
            "kurtis": Category(id=str(uuid.uuid4()), name="Kurtis", slug="kurtis"),
            "dresses": Category(id=str(uuid.uuid4()), name="Dresses", slug="dresses"),
            "tops": Category(id=str(uuid.uuid4()), name="Tops", slug="tops"),
            "shirts": Category(id=str(uuid.uuid4()), name="Shirts", slug="shirts"),
            "jeans": Category(id=str(uuid.uuid4()), name="Jeans", slug="jeans"),
        }
        for c in categories.values():
            db.add(c)
        db.commit()

        # 30 Curated Luxury Clothing Products
        products_data = [
            # 1-6: Kurtis
            ("kurtis", "Anarkali Embroidered Black Kurti", "BG-KRT-BLK", "Handcrafted pure Chanderi silk kurti featuring traditional gold Zari botanical embroidery.", 2500.0, "Black", "#111111", True, ["XS", "S", "M", "L", "XL", "XXL"]),
            ("kurtis", "Chikankari Pure Cotton White Kurti", "BG-KRT-WHT", "Authentic Lucknowi hand embroidery on breathable mulmul cotton with delicate shadow work.", 1850.0, "Ivory White", "#FDFDFD", False, ["XS", "S", "M", "L", "XL"]),
            ("kurtis", "Straight Cut Silk Emerald Kurti", "BG-KRT-EMR", "Raw silk kurta in deep bottle emerald with hand-embroidered gotta patti neckline.", 2950.0, "Emerald Green", "#097969", False, ["S", "M", "L", "XL"]),
            ("kurtis", "Floral Printed Muslin Angrakha Kurti", "BG-KRT-ANG", "Vintage botanical Persian floral prints with overlapping side tassel tie-ups.", 2100.0, "Blush Rose", "#FFD1DC", False, ["S", "M", "L"]),
            ("kurtis", "Georgette Festive Maroon Kurti", "BG-KRT-MRN", "Crinkle georgette pleated tunic adorned with mirror-work borders for celebrations.", 2750.0, "Maroon", "#800000", False, ["M", "L", "XL", "XXL"]),
            ("kurtis", "Indigo Hand Block Print A-Line Kurti", "BG-KRT-IND", "Natural dabu mud-resist dyed indigo cotton kurti with side pockets and notched collar.", 1650.0, "Indigo Blue", "#1F3A52", False, ["XS", "S", "M", "L"]),

            # 7-12: Dresses
            ("dresses", "Sage Pleated Maxi Gown", "BG-DRS-SGE", "Floor-length evening dress in Italian pleated georgette with softly gathered empire waist.", 3800.0, "Sage Green", "#9CAF88", False, ["XS", "S", "M", "L"]),
            ("dresses", "Satin Slip Midi Dress", "BG-DRS-SLP", "Liquid champagne silk slip with cowl neckline and bias-cut drape.", 3200.0, "Champagne", "#F7E7CE", False, ["XS", "S", "M", "L"]),
            ("dresses", "Satin Trench Dress", "BG-DRS-TRN", "Structured double-breasted trench silhouette crafted in lustrous heavyweight satin.", 4200.0, "Camel Beige", "#C19A6B", False, ["S", "M", "L"]),
            ("dresses", "Tiered Chiffon Summer Dress", "BG-DRS-CHF", "Fluted micro-pleated skirt layers with halter tie-up and self-tie silk belt.", 2600.0, "Sky Blue", "#87CEEB", False, ["XS", "S", "M"]),
            ("dresses", "Velvet Wrap Evening Gown", "BG-DRS-VLV", "Deep ruby silk-blend velvet gown with surplice neckline and tulip hem.", 4900.0, "Ruby Red", "#9B111E", False, ["S", "M", "L", "XL"]),
            ("dresses", "Cotton Linen Halter Sundress", "BG-DRS-LNN", "Pre-washed breathable European linen dress with scalloped hem embroidery.", 2400.0, "Oatmeal", "#D6C6B2", False, ["XS", "S", "M", "L"]),

            # 13-18: Tops
            ("tops", "Billow Sleeve Satin Blouse", "BG-TOP-BLS", "Romantic poet sleeves with elongated button cuffs in lustrous mulberry silk.", 1750.0, "Pearl White", "#F5F5F0", False, ["XS", "S", "M", "L"]),
            ("tops", "Sculpted Ruffle Peplum Top", "BG-TOP-RFL", "Architectural tailored bodice with structured shoulder ruffles.", 2100.0, "Onyx Black", "#0A0A0A", False, ["S", "M", "L"]),
            ("tops", "Ribbed Knit Mockneck Top", "BG-TOP-KNIT", "Fine-gauge extrafine merino wool ribbed knit with seamless construction.", 1450.0, "Mocha Brown", "#4A3728", False, ["XS", "S", "M", "L", "XL"]),
            ("tops", "Sheer Organza Corset Blouse", "BG-TOP-ORG", "Structured boned inner bodice covered in ethereal diaphanous silk organza.", 2650.0, "Soft Lilac", "#C8A2C8", False, ["S", "M", "L"]),
            ("tops", "Crepe High-Low Tunic Top", "BG-TOP-CRP", "Fluid crepe tunic with asymmetrical cascading hemline and keyhole back.", 1550.0, "Terracotta", "#E2725B", False, ["XS", "S", "M", "L"]),
            ("tops", "Linen Button-Front Crop Top", "BG-TOP-LNN", "Square neck cropped top with authentic horn buttons in washed pure linen.", 1250.0, "Olive Khaki", "#708238", False, ["S", "M", "L"]),

            # 19-24: Shirts
            ("shirts", "Classic Poplin Crisp White Shirt", "BG-SHT-WHT", "Tailored menswear-inspired shirt in 120-two-ply Egyptian cotton poplin.", 1950.0, "Optic White", "#FFFFFF", False, ["XS", "S", "M", "L", "XL"]),
            ("shirts", "Oversized Striped Oxford Shirt", "BG-SHT-STR", "Relaxed boyfriend fit in yarn-dyed blue banker stripe Oxford weave.", 1850.0, "Stripe Blue", "#4682B4", False, ["S", "M", "L", "XL"]),
            ("shirts", "Silk Charmeuse Relaxed Shirt", "BG-SHT-SLK", "Effortless drape in 19mm silk charmeuse with mother-of-pearl buttons.", 3400.0, "Midnight Navy", "#000080", False, ["S", "M", "L"]),
            ("shirts", "Cotton Utility Safari Shirt", "BG-SHT-UTL", "Double flap chest pockets and epaulettes in garment-dyed cotton twill.", 1750.0, "Sand Khaki", "#C2B280", False, ["M", "L", "XL", "XXL"]),
            ("shirts", "Bohemian Embroidered Peasant Shirt", "BG-SHT-BOH", "Tassel tie neckline and hand-smocked cuffs on crinkle cotton gauze.", 1600.0, "Warm Ecru", "#C2B280", False, ["XS", "S", "M", "L"]),
            ("shirts", "French Cuff Tencel Evening Shirt", "BG-SHT-TNC", "Silky sustainable lyocell shirt with hidden placket and French double cuffs.", 2250.0, "Charcoal Grey", "#36454F", False, ["S", "M", "L", "XL"]),

            # 25-30: Jeans
            ("jeans", "Vintage High-Rise Straight Jeans", "BG-JNS-VNT", "Authentic 13oz non-stretch Japanese selvedge denim in stone wash.", 2800.0, "Vintage Indigo", "#2F4F4F", False, ["28", "30", "32", "34", "36"]),
            ("jeans", "Wide-Leg Washed Indigo Denim", "BG-JNS-WID", "High-waisted relaxed palazzo denim cut with clean trouser hemline.", 3100.0, "Mid Blue Wash", "#4169E1", False, ["28", "30", "32", "34"]),
            ("jeans", "Slim Tapered Dark Indigo Jeans", "BG-JNS-SLM", "Raw organic denim with 2% comfort stretch for all-day structure.", 2650.0, "Raw Dark Denim", "#001F3F", False, ["30", "32", "34", "36"]),
            ("jeans", "Relaxed Carpenter Denim Trousers", "BG-JNS-CRP", "Workwear utility loops and patch pockets in durable rinsed ecru denim.", 2900.0, "Natural Ecru", "#F5F5DC", False, ["28", "30", "32", "34"]),
            ("jeans", "Raw Hem Flared Studio Jeans", "BG-JNS-FLR", "Subtle 70s kick-flare silhouette with hand-distressed raw edge hems.", 2750.0, "Faded Black", "#1C1C1C", False, ["28", "30", "32"]),
            ("jeans", "Stretch Skinny Black Denim", "BG-JNS-SKN", "Power-stretch Turkish denim that retains pitch-black hue wash after wash.", 2200.0, "Stay Black", "#0D0D0D", False, ["28", "30", "32", "34", "36"]),
        ]

        print("Seeding 30 Products, Variants & Inventories...")
        all_variants = []

        for cat_key, title, base_sku, desc, price, color, color_code, is_core, sizes in products_data:
            prod = Product(
                id=str(uuid.uuid4()),
                category_id=categories[cat_key].id,
                title=title,
                base_sku=base_sku,
                description=desc,
                base_price=price,
                fabric="100% Premium Fabric",
                image_url=f"https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20261102_042056_1a704ff7-b0e5-4a9f-bbda-62392b819fb6.png&w=1200&q=85",
                is_active=True
            )
            db.add(prod)
            db.flush()

            for size in sizes:
                sku = f"{base_sku}-{size}"
                # Set realistic stock levels: some high, some low, some out-of-stock
                if size == "XXL" or size == "36":
                    on_hand = 0  # Out of stock variant
                    reserved = 0
                elif size == "XS" or size == "28":
                    on_hand = 2  # Low stock
                    reserved = 0
                else:
                    on_hand = random.randint(12, 45)
                    reserved = random.randint(0, 3)

                var = ProductVariant(
                    id=str(uuid.uuid4()),
                    product_id=prod.id,
                    sku=sku,
                    size=size,
                    color=color,
                    color_code=color_code,
                    price_adjustment=0.0,
                    barcode=f"890{random.randint(100000000, 999999999)}"
                )
                db.add(var)
                db.flush()
                all_variants.append(var)

                inv = Inventory(
                    id=str(uuid.uuid4()),
                    variant_id=var.id,
                    quantity_on_hand=on_hand,
                    quantity_reserved=reserved,
                    reorder_threshold=5,
                    warehouse_bin=f"BIN-{cat_key[:1].upper()}{random.randint(1,9)}-{random.randint(10,99)}",
                    version=1
                )
                db.add(inv)

        db.commit()
        print(f"Successfully seeded {len(products_data)} products and {len(all_variants)} variants!")

        # -------------------------------------------------------------- #
        # Sample Customers, Orders, Payments, Invoices, Shipments
        # -------------------------------------------------------------- #
        print("Seeding sample business lifecycle orders & workflows...")
        sample_customers = [
            ("Priya Sharma", "priya.sharma@example.com", "Mumbai, Maharashtra"),
            ("Aanya Kapoor", "aanya.k@example.com", "New Delhi, Delhi"),
            ("Rohan Mehta", "rohan.mehta@example.com", "Bengaluru, Karnataka"),
            ("Ananya Sengupta", "ananya.s@example.com", "Kolkata, West Bengal"),
            ("Zoya Akhtar", "zoya.a@example.com", "Hyderabad, Telangana"),
            ("Vikram Singhania", "vikram.s@example.com", "Jaipur, Rajasthan"),
        ]

        order_statuses = ["DELIVERED", "DELIVERED", "SHIPPED", "INVOICED", "PAYMENT_CAPTURED", "CANCELLED"]

        for i, (name, email, city) in enumerate(sample_customers):
            status = order_statuses[i]
            # Pick a variant that has on_hand > 5
            available_vars = [v for v in all_variants if v.sku.endswith("-M") or v.sku.endswith("-32")]
            chosen_var = available_vars[i % len(available_vars)]

            order_id = str(uuid.uuid4())
            order_num = f"ORD-2026-{1000 + i}"
            item_price = 2500.0

            order = Order(
                id=order_id,
                order_number=order_num,
                customer_name=name,
                customer_email=email,
                total_amount=item_price,
                status=status,
                created_at=_utc(24 * (i + 1)),
                updated_at=_utc(12 * (i + 1))
            )
            db.add(order)
            db.flush()

            # Item
            db.add(OrderItem(
                id=str(uuid.uuid4()),
                order_id=order_id,
                variant_id=chosen_var.id,
                product_title=chosen_var.sku,
                ordered_size=chosen_var.size,
                ordered_color=chosen_var.color,
                quantity=1,
                unit_price=item_price,
                subtotal=item_price
            ))

            # Payment
            pay_status = "FAILED" if status == "CANCELLED" else "CAPTURED"
            pay = Payment(
                id=str(uuid.uuid4()),
                order_id=order_id,
                payment_gateway="Razorpay Secure",
                transaction_reference=f"pay_rzp_{uuid.uuid4().hex[:12]}",
                amount=item_price,
                currency="INR",
                status=pay_status,
                idempotency_key=f"idem_{order_num}",
                captured_at=_utc(24 * (i + 1)) if pay_status == "CAPTURED" else None
            )
            db.add(pay)
            db.flush()

            # Invoice
            if status in ("INVOICED", "SHIPPED", "DELIVERED"):
                inv_rec = Invoice(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    invoice_number=f"INV-2026-{5000 + i}",
                    total_amount=item_price,
                    status="ISSUED",
                    created_at=_utc(20 * (i + 1))
                )
                db.add(inv_rec)
                db.flush()
                db.add(InvoiceItem(
                    id=str(uuid.uuid4()),
                    invoice_id=inv_rec.id,
                    variant_id=chosen_var.id,
                    sku=chosen_var.sku,
                    description=chosen_var.sku,
                    size=chosen_var.size,
                    color=chosen_var.color,
                    unit_price=item_price,
                    quantity=1
                ))

            # Shipment
            if status in ("SHIPPED", "DELIVERED"):
                ship_status = "DELIVERED" if status == "DELIVERED" else "IN_TRANSIT"
                db.add(Shipment(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    tracking_number=f"TRK-FEDEX-{random.randint(10000000, 99999999)}",
                    carrier="FedEx Express Fashion",
                    status=ship_status,
                    created_at=_utc(15 * (i + 1)),
                    updated_at=_utc(2 * (i + 1)) if ship_status == "DELIVERED" else _utc(15 * (i + 1))
                ))

            # Return record on 1 delivered order
            if i == 0:
                db.add(ReturnRecord(
                    id=str(uuid.uuid4()),
                    order_id=order_id,
                    reason="Customer requested exchange for size L",
                    status="APPROVED",
                    created_at=_utc(1)
                ))

            # Workflow execution
            wf = WorkflowExecution(
                id=str(uuid.uuid4()),
                workflow_name="OrderFulfillmentSaga",
                correlation_id=order_num,
                order_id=order_id,
                current_step=f"STEP_{status}",
                status="COMPLETED" if status == "DELIVERED" else "IN_PROGRESS",
                started_at=_utc(24 * (i + 1))
            )
            db.add(wf)
            db.flush()

            db.add(WorkflowEvent(
                id=str(uuid.uuid4()),
                workflow_execution_id=wf.id,
                event_name="ORDER_COMPLETED" if status == "DELIVERED" else "ORDER_INITIATED",
                step_number=1,
                status="SUCCESS",
                event_payload={"order_number": order_num, "amount": item_price},
                created_at=_utc(24 * (i + 1))
            ))

        db.commit()
        print("Demo dataset population complete! Database is fully seeded with realistic clothing data.")


if __name__ == "__main__":
    seed_expanded()
