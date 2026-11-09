
import streamlit as st
import csv
import uuid
from pathlib import Path
from datetime import datetime, timezone
st.image(
    "images/companybanner.png",
    use_container_width=True
)
st.set_page_config(
    page_title="Hot Sauce Store",
    page_icon="🌶️",
    layout="wide"
)
params = st.query_params

if "campaign_tracking" not in st.session_state:
    st.session_state.campaign_tracking = {}

for key in [
    "campaign_id",
    "utm_source",
    "utm_medium",
    "utm_campaign"
]:
    if key in params:
        st.session_state.campaign_tracking[key] = params[key]

# Save orders to a CSV file for our classroom prototype

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

ORDERS_FILE = DATA_DIR / "demo_orders.csv"

ORDER_FIELDS = [
    "order_id",
    "order_date",
    "customer_name",
    "customer_email",
    "items",
    "order_total",
    "promo_code",
    "campaign_id",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "match_status"
]


def save_order(customer_name, customer_email, promo_code, total):
    tracking = st.session_state.get("campaign_tracking", {})

    order_id = "ORD-" + uuid.uuid4().hex[:8].upper()

    cart_items = []
    for product in products:
        quantity = st.session_state.cart.get(product["id"], 0)
        if quantity > 0:
            cart_items.append(f"{product['name']} x{quantity}")

    order = {
        "order_id": order_id,
        "order_date": datetime.now(timezone.utc).isoformat(),
        "customer_name": customer_name.strip(),
        "customer_email": customer_email.strip(),
        "items": "; ".join(cart_items),
        "order_total": round(total, 2),
        "promo_code": promo_code.strip().upper(),
        "campaign_id": tracking.get("campaign_id", ""),
        "utm_source": tracking.get("utm_source", ""),
        "utm_medium": tracking.get("utm_medium", ""),
        "utm_campaign": tracking.get("utm_campaign", ""),
        "match_status": "Pending"
    }

    file_exists = ORDERS_FILE.exists()

    with open(ORDERS_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=ORDER_FIELDS)

        if not file_exists or ORDERS_FILE.stat().st_size == 0:
            writer.writeheader()

        writer.writerow(order)

    return order

# Demo product catalog
products = [
    {
        "id": 1,
        "name": "Classic Red Hot Sauce",
        "price": 8.99,
        "heat": "Medium",
        "emoji": "🌶️"
    },
    {
        "id": 2,
        "name": "Mango Habanero",
        "price": 10.99,
        "heat": "Hot",
        "emoji": "🥭"
    },
    {
        "id": 3,
        "name": "Smoky Chipotle",
        "price": 9.99,
        "heat": "Mild",
        "emoji": "🔥"
    }
]

# Initialize shopping cart
if "cart" not in st.session_state:
    st.session_state.cart = {}

st.title("🌶️ Fire & Flavor")
st.subheader("Handcrafted Hot Sauces")
st.write("Discover bold flavors and find your perfect heat!")

st.divider()

st.header("Shop Our Sauces")

columns = st.columns(3)

for index, product in enumerate(products):
    with columns[index]:
        with st.container(border=True):
            st.markdown(
                f"<h1 style='text-align:center'>{product['emoji']}</h1>",
                unsafe_allow_html=True
            )

            st.subheader(product["name"])
            st.write(f"Heat Level: {product['heat']}")
            st.markdown(f"### ${product['price']:.2f}")

            if st.button(
                "Add to Cart",
                key=f"add_{product['id']}",
                use_container_width=True
            ):
                product_id = product["id"]
                st.session_state.cart[product_id] = (
                    st.session_state.cart.get(product_id, 0) + 1
                )
                st.success("Added to cart!")

st.divider()

st.header("🛒 Your Shopping Cart")

total = 0

if not st.session_state.cart:
    st.info("Your cart is empty.")
else:
    for product in products:
        quantity = st.session_state.cart.get(product["id"], 0)

        if quantity > 0:
            subtotal = quantity * product["price"]
            total += subtotal

            st.write(
                f"{product['name']} × {quantity} — ${subtotal:.2f}"
            )

    st.markdown(f"### Total: ${total:.2f}")

    st.divider()
    st.header("Checkout")

    with st.form("checkout_form"):
        customer_name = st.text_input("Customer Name")
        customer_email = st.text_input("Email Address")
        promo_code = st.text_input("Promo Code (Optional)")

        place_order = st.form_submit_button(
            "Place Demo Order",
            use_container_width=True
        )

        
        if place_order:
            if not customer_name.strip() or not customer_email.strip():
                st.error("Please enter your name and email.")
            else:
                order = save_order(
                    customer_name,
                    customer_email,
                    promo_code,
                    total
                )

                st.success("🎉 Demo order placed successfully!")
                st.write(f"Order ID: {order['order_id']}")
                st.write(f"Customer: {order['customer_name']}")
                st.write(f"Order Total: ${order['order_total']:.2f}")

                if order["campaign_id"]:
                    st.info(
                        "Campaign information captured: "
                        + order["campaign_id"]
                    )
                else:
                    st.info("No campaign ID captured for this order.")

                st.caption(
                    "Demo order saved. No real payment was collected."
                )

                st.session_state.cart = {}

    with st.expander("🔍 Marketing Tracking Debug"):
        st.json(st.session_state.campaign_tracking)
