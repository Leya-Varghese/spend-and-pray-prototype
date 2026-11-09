
import streamlit as st

# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="Spend & Pray",
    page_icon="🌶️",
    layout="wide"
)


# ----------------------------------
# SESSION STATE
# ----------------------------------

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "campaign_tracking" not in st.session_state:
    st.session_state.campaign_tracking = {}


# ----------------------------------
# CAMPAIGN LINK DETECTION
# ----------------------------------

params = st.query_params

campaign_keys = [
    "campaign_id",
    "utm_source",
    "utm_medium",
    "utm_campaign"
]

has_campaign_link = any(
    key in params for key in campaign_keys
)

# Automatically select Customer when a campaign link is opened.
# Only handle each campaign link once per session.

if has_campaign_link:

    incoming_tracking = {
        key: params.get(key, "")
        for key in campaign_keys
        if key in params
    }

    campaign_signature = tuple(
        incoming_tracking.get(key, "")
        for key in campaign_keys
    )

    if (
        st.session_state.get("last_campaign_signature")
        != campaign_signature
    ):
        st.session_state.user_role = "Customer"
        st.session_state.last_campaign_signature = (
            campaign_signature
        )

    # Preserve tracking information for checkout.
    st.session_state.campaign_tracking = incoming_tracking


# ----------------------------------
# ROLE FUNCTIONS
# ----------------------------------

def select_role(role):
    st.session_state.user_role = role
    st.rerun()


def change_role():
    st.session_state.user_role = None

    # Clear previous tracking when switching roles.
    st.session_state.campaign_tracking = {}
    st.session_state.last_campaign_signature = None

    # Remove campaign parameters from the current URL.
    st.query_params.clear()

    st.rerun()


# ----------------------------------
# BUSINESS OWNER HOME / TUTORIAL
# ----------------------------------

def business_owner_home():

    st.title("🌶️ Spend & Pray")

    st.subheader(
        "Marketing Attribution & Source Tracking System"
    )

    st.success("👔 Business Owner View")

    st.write(
        "Welcome to the Spend & Pray prototype, "
        "developed to help HotVile Hot Sauce Co. "
        "connect marketing campaigns to customer "
        "purchases and evaluate campaign performance."
    )

    st.divider()

    st.header("📖 How to Use This Prototype")

    st.caption(
        "Follow these five steps to explore the "
        "marketing attribution workflow."
    )

    steps = [
        (
            "Create a Marketing Campaign",
            "Open Create Campaign. Enter a campaign "
            "name, choose a marketing channel, and "
            "set a budget. The system generates a "
            "campaign ID, tracking URL, QR code, "
            "and promotional code."
        ),
        (
            "Open the HotVile Store",
            "Use the generated campaign tracking "
            "URL to open the customer storefront. "
            "The system captures available campaign "
            "information from the link."
        ),
        (
            "Place a Demo Order",
            "Select a hot sauce, add it to the cart, "
            "and complete checkout using fictional "
            "customer details."
        ),
        (
            "Review Order Matching",
            "Open Order Matching to see whether "
            "the order is Matched, Unattributed, "
            "or Needs Review."
        ),
        (
            "Explore the Marketing Dashboard",
            "Review attributed revenue, attribution "
            "coverage, campaign performance, and "
            "budget-based ROAS."
        )
    ]

    for number, (title, description) in enumerate(
        steps, start=1
    ):

        with st.container(border=True):

            st.markdown(
                f"#### Step {number}: {title}"
            )

            st.write(description)

    st.info(
        "💡 Tip: Create a campaign and open its "
        "tracking URL in a new browser tab to "
        "simulate a customer arriving from a "
        "marketing activity."
    )

    st.caption(
        "Academic prototype | Demonstration data only"
    )


# ----------------------------------
# WELCOME / ROLE SELECTION
# ----------------------------------

if st.session_state.user_role is None:

    st.title("🌶️ Welcome to Spend & Pray")

    st.subheader(
        "Marketing Attribution & Source Tracking System"
    )

    st.write(
        "An interactive prototype developed "
        "for HotVile Hot Sauce Co."
    )

    st.info(
        "Select a role to continue. "
        "No username or password is required."
    )

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.header("👔 Business Owner")

            st.write(
                "Create marketing campaigns, "
                "review order attribution, and "
                "analyze marketing performance."
            )

            if st.button(
                "Continue as Business Owner",
                use_container_width=True,
                type="primary"
            ):
                select_role("Business Owner")

    with col2:

        with st.container(border=True):

            st.header("🛒 Customer")

            st.write(
                "Browse HotVile hot sauces, "
                "add products to your cart, "
                "and place a demonstration order."
            )

            if st.button(
                "Continue as Customer",
                use_container_width=True
            ):
                select_role("Customer")

    st.caption(
        "Prototype role selection only. "
        "No real authentication is performed."
    )


# ----------------------------------
# ROLE-BASED NAVIGATION
# ----------------------------------

else:

    role = st.session_state.user_role

    with st.sidebar:

        st.markdown(
            f"**Current Role:** {role}"
        )

        if st.button(
            "🔄 Switch Role",
            use_container_width=True
        ):
            change_role()

    if role == "Business Owner":

        pages = {
            "Business Owner": [
                st.Page(
                    business_owner_home,
                    title="Home & Tutorial",
                    icon="🏠",
                    default=True
                ),
                st.Page(
                    "pages/create_campaign.py",
                    title="Create Campaign",
                    icon="📣"
                ),
                st.Page(
                    "pages/order_matching.py",
                    title="Order Matching",
                    icon="🔗"
                ),
                st.Page(
                    "pages/marketing_dashboard.py",
                    title="Marketing Dashboard",
                    icon="📊"
                )
            ]
        }

    else:

        pages = {
            "Customer": [
                st.Page(
                    "pages/hot_sauce_store.py",
                    title="HotVile Hot Sauce Store",
                    icon="🌶️",
                    url_path="hot_sauce_store"
                )
            ]
        }

    navigation = st.navigation(pages)

    navigation.run()
