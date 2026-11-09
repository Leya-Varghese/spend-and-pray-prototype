
import streamlit as st

from attribution_engine import process_orders, calculate_kpis

# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="Order Matching",
    page_icon="🔗",
    layout="wide"
)

# ----------------------------------
# PAGE HEADER
# ----------------------------------

st.title("🔗 Marketing Order Matching")

st.write(
    "Track customer purchases and identify which "
    "marketing campaigns generated attributed orders."
)

# ----------------------------------
# LOAD SHARED ATTRIBUTION ENGINE
# ----------------------------------

results, campaigns = process_orders()
kpis = calculate_kpis(results)

if not results:
    st.warning("No customer orders found.")
    st.stop()

total_orders = kpis["total_orders"]
matched = kpis["matched_orders"]
unattributed = kpis["unattributed_orders"]
needs_review = kpis["needs_review"]
matched_revenue = kpis["matched_revenue"]
coverage = kpis["coverage"]

# ----------------------------------
# FILTER STATE
# ----------------------------------

if "order_filter" not in st.session_state:
    st.session_state.order_filter = "All"

# ----------------------------------
# KPI SUMMARY
# ----------------------------------

st.divider()
st.subheader("Attribution Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Orders", total_orders)

    if st.button(
        "View All Orders",
        use_container_width=True
    ):
        st.session_state.order_filter = "All"

with col2:
    st.metric("Matched Orders", matched)

    if st.button(
        "View Matched",
        use_container_width=True
    ):
        st.session_state.order_filter = "Matched"

with col3:
    st.metric("Unattributed Orders", unattributed)

    if st.button(
        "View Unattributed",
        use_container_width=True
    ):
        st.session_state.order_filter = "Unattributed"

with col4:
    st.metric("Needs Review", needs_review)

    if st.button(
        "View Needs Review",
        use_container_width=True
    ):
        st.session_state.order_filter = "Needs Review"

# ----------------------------------
# ADDITIONAL METRICS
# ----------------------------------

st.divider()

col5, col6 = st.columns(2)

with col5:
    st.metric(
        "Attribution Coverage",
        f"{coverage:.1f}%"
    )

with col6:
    st.metric(
        "Matched Revenue",
        f"${matched_revenue:,.2f}"
    )

# ----------------------------------
# FILTER ORDER RESULTS
# ----------------------------------

st.divider()

selected_filter = st.session_state.order_filter

st.subheader(f"{selected_filter} Orders")

if selected_filter == "All":

    filtered_results = results

else:

    filtered_results = [
        order
        for order in results
        if order["status"] == selected_filter
    ]

st.caption(
    f"Showing {len(filtered_results)} of {total_orders} orders"
)

# ----------------------------------
# DISPLAY ORDERS AS LIST
# ----------------------------------

if not filtered_results:

    st.info("No orders found in this category.")

else:

    # List headers
    header = st.columns([2, 2, 1, 1.5, 2, 1.5])

    header[0].write("**Order ID**")
    header[1].write("**Customer**")
    header[2].write("**Revenue**")
    header[3].write("**Status**")
    header[4].write("**Campaign**")
    header[5].write("**Channel**")

    st.divider()

    for order in filtered_results:

        cols = st.columns([2, 2, 1, 1.5, 2, 1.5])

        cols[0].write(order["order_id"])

        cols[1].write(order["customer"])

        cols[2].write(
            f"${order['revenue']:.2f}"
        )

        cols[3].write(order["status"])

        cols[4].write(order["campaign_name"])

        cols[5].write(order["channel"])

        st.divider()

# ----------------------------------
# ATTRIBUTION EXPLANATION
# ----------------------------------

with st.expander("ℹ️ How Order Matching Works"):

    st.write(
        "**Matched:** The order has a Campaign ID "
        "or promo code matching a saved campaign."
    )

    st.write(
        "**Unattributed:** The order contains no "
        "Campaign ID or promotional code."
    )

    st.write(
        "**Needs Review:** The order contains "
        "unverified or conflicting tracking signals."
    )

    st.info(
        "Marketing attribution identifies associations "
        "between campaigns and purchases. It does not "
        "prove that a campaign caused a purchase."
    )
