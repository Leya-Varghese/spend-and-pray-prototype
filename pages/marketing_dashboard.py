
import streamlit as st
import csv
from pathlib import Path

st.set_page_config(
    page_title="Marketing Dashboard",
    page_icon="📊",
    layout="wide"
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ORDERS_FILE = DATA_DIR / "demo_orders.csv"
CAMPAIGNS_FILE = DATA_DIR / "campaigns.csv"

st.title("📊 Marketing Attribution Dashboard")
st.write(
    "Understand which marketing campaigns "
    "are connected to customer purchases."
)


def load_csv(path):
    if not path.exists():
        return []

    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def match_order(order, campaigns):
    campaign_id = (order.get("campaign_id") or "").strip()
    promo_code = (order.get("promo_code") or "").strip().upper()

    id_match = next(
        (
            c for c in campaigns
            if campaign_id == c["campaign_id"]
        ),
        None
    ) if campaign_id else None

    promo_match = next(
        (
            c for c in campaigns
            if promo_code == c["promo_code"].upper()
        ),
        None
    ) if promo_code else None

    if id_match and promo_match:
        if id_match["campaign_id"] != promo_match["campaign_id"]:
            return "Needs Review", None

    if id_match:
        return "Matched", id_match

    if promo_match:
        return "Matched", promo_match

    if campaign_id or promo_code:
        return "Needs Review", None

    return "Unattributed", None


orders = load_csv(ORDERS_FILE)
campaigns = load_csv(CAMPAIGNS_FILE)

if not orders:
    st.warning("No orders found. Place a demo order first.")
    st.stop()

if not campaigns:
    st.warning("No campaigns found. Create a campaign first.")
    st.stop()

total_revenue = 0.0
matched_revenue = 0.0
matched_orders = 0

status_counts = {
    "Matched": 0,
    "Unattributed": 0,
    "Needs Review": 0
}

channel_results = {}
campaign_results = {}

for order in orders:
    try:
        revenue = float(order.get("order_total") or 0)
    except ValueError:
        revenue = 0.0

    total_revenue += revenue

    status, campaign = match_order(order, campaigns)
    status_counts[status] += 1

    if status == "Matched":
        matched_orders += 1
        matched_revenue += revenue

        channel = campaign["channel"]
        campaign_name = campaign["campaign_name"]

        if channel not in channel_results:
            channel_results[channel] = {
                "orders": 0,
                "revenue": 0.0
            }

        if campaign_name not in campaign_results:
            campaign_results[campaign_name] = {
                "orders": 0,
                "revenue": 0.0
            }

        channel_results[channel]["orders"] += 1
        channel_results[channel]["revenue"] += revenue

        campaign_results[campaign_name]["orders"] += 1
        campaign_results[campaign_name]["revenue"] += revenue


# ----------------------------------
# OVERVIEW
# ----------------------------------

st.divider()
st.subheader("Performance Overview")

coverage = matched_orders / len(orders) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", len(orders))
col2.metric("Total Revenue", f"${total_revenue:,.2f}")
col3.metric("Matched Revenue", f"${matched_revenue:,.2f}")
col4.metric("Attribution Coverage", f"{coverage:.1f}%")


# ----------------------------------
# ATTRIBUTION STATUS
# ----------------------------------

st.divider()
st.subheader("Attribution Status")

for status, count in status_counts.items():
    st.write(f"**{status}: {count} orders**")
    st.progress(count / len(orders))


# ----------------------------------
# CHANNEL PERFORMANCE
# ----------------------------------

st.divider()
st.subheader("Marketing Channel Performance")

if channel_results:
    for channel, data in sorted(
        channel_results.items(),
        key=lambda item: item[1]["revenue"],
        reverse=True
    ):
        with st.container(border=True):
            st.write(f"**{channel}**")
            col1, col2 = st.columns(2)
            col1.metric("Matched Orders", data["orders"])
            col2.metric(
                "Matched Revenue",
                f"${data['revenue']:,.2f}"
            )
else:
    st.info("No matched marketing channels yet.")


# ----------------------------------
# CAMPAIGN PERFORMANCE
# ----------------------------------

st.divider()
st.subheader("Campaign Performance")

if campaign_results:
    for name, data in sorted(
        campaign_results.items(),
        key=lambda item: item[1]["revenue"],
        reverse=True
    ):
        with st.container(border=True):
            st.write(f"**{name}**")
            st.write(f"Orders: {data['orders']}")
            st.write(f"Revenue: ${data['revenue']:,.2f}")
else:
    st.info("No matched campaigns yet.")

# ----------------------------------
# MARKETING BUDGET & ROAS
# ----------------------------------

st.divider()
st.subheader("💰 Marketing Budget & ROAS")

total_budget = 0.0

for campaign in campaigns:
    try:
        total_budget += float(campaign.get("budget") or 0)
    except (ValueError, TypeError):
        pass

estimated_roas = (
    matched_revenue / total_budget
    if total_budget > 0
    else None
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Campaign Budget",
    f"${total_budget:,.2f}"
)

col2.metric(
    "Matched Revenue",
    f"${matched_revenue:,.2f}"
)

col3.metric(
    "Budget-Based ROAS",
    f"{estimated_roas:.2f}x"
    if estimated_roas is not None
    else "N/A"
)

st.caption(
    "Budget-based ROAS is an estimate using allocated "
    "campaign budgets, not confirmed advertising expenditure."
)


# ----------------------------------
# CHANNEL COMPARISON
# ----------------------------------

st.divider()
st.subheader("📊 Revenue by Marketing Channel")

if channel_results:

    maximum_revenue = max(
        data["revenue"]
        for data in channel_results.values()
    )

    for channel, data in sorted(
        channel_results.items(),
        key=lambda item: item[1]["revenue"],
        reverse=True
    ):

        st.write(
            f"**{channel} — ${data['revenue']:,.2f}**"
        )

        proportion = (
            data["revenue"] / maximum_revenue
            if maximum_revenue > 0
            else 0
        )

        st.progress(proportion)

else:
    st.info("No matched campaign revenue available.")
