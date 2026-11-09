
import streamlit as st
import csv
import uuid
import io
import qrcode

from pathlib import Path
from datetime import date, datetime, timezone
from urllib.parse import urlencode

# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="Create Campaign",
    page_icon="📢",
    layout="wide"
)

# ----------------------------------
# DATA STORAGE
# ----------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CAMPAIGNS_FILE = DATA_DIR / "campaigns.csv"

CAMPAIGN_FIELDS = [
    "campaign_id",
    "campaign_name",
    "channel",
    "start_date",
    "end_date",
    "budget",
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "tracking_url",
    "promo_code",
    "created_at"
]

# Change this if your storefront uses a different URL
STORE_URL = "http://localhost:8501/hot_sauce_store"


# ----------------------------------
# SAVE CAMPAIGN FUNCTION
# ----------------------------------

def save_campaign(campaign):

    file_exists = CAMPAIGNS_FILE.exists()

    with open(
        CAMPAIGNS_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=CAMPAIGN_FIELDS
        )

        if not file_exists or CAMPAIGNS_FILE.stat().st_size == 0:
            writer.writeheader()

        writer.writerow(campaign)


# ----------------------------------
# GENERATE QR CODE FUNCTION
# ----------------------------------

def generate_qr_code(url):

    qr = qrcode.QRCode(
        box_size=8,
        border=2
    )

    qr.add_data(url)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()


# ----------------------------------
# PAGE HEADER
# ----------------------------------

st.title("📢 Create Marketing Campaign")

st.write(
    "Create marketing campaigns and automatically "
    "generate tracking links, promo codes, and QR codes."
)

st.divider()


# ----------------------------------
# CAMPAIGN CREATION FORM
# ----------------------------------

st.subheader("Campaign Details")

with st.form("create_campaign_form"):

    campaign_name = st.text_input(
        "Campaign Name",
        placeholder="Fall Farmers Market Promotion"
    )

    channel = st.selectbox(
        "Marketing Channel",
        [
            "Paid Social",
            "Influencer",
            "Farmers Market",
            "Pop-up Event"
        ]
    )

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date.today()
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=date.today()
        )

    budget = st.number_input(
        "Campaign Budget ($)",
        min_value=0.0,
        value=50.0,
        step=10.0
    )

    create_button = st.form_submit_button(
        "🚀 Create Campaign",
        use_container_width=True
    )


# ----------------------------------
# CREATE CAMPAIGN
# ----------------------------------

if create_button:

    if not campaign_name.strip():

        st.error("Please enter a campaign name.")

    elif end_date < start_date:

        st.error("End date cannot be before start date.")

    else:

        campaign_id = (
            "CMP-" + uuid.uuid4().hex[:8].upper()
        )

        source_mapping = {
            "Paid Social": "paid_social",
            "Influencer": "influencer",
            "Farmers Market": "farmers_market",
            "Pop-up Event": "popup_event"
        }

        medium_mapping = {
            "Paid Social": "paid_social",
            "Influencer": "influencer",
            "Farmers Market": "qr",
            "Pop-up Event": "qr"
        }

        utm_source = source_mapping[channel]
        utm_medium = medium_mapping[channel]

        utm_campaign = (
            campaign_name.strip()
            .lower()
            .replace(" ", "_")
        )

        promo_code = (
            "HOT" + uuid.uuid4().hex[:6].upper()
        )

        tracking_params = {
            "campaign_id": campaign_id,
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign
        }

        tracking_url = (
            STORE_URL + "?" + urlencode(tracking_params)
        )

        campaign = {
            "campaign_id": campaign_id,
            "campaign_name": campaign_name.strip(),
            "channel": channel,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "budget": round(budget, 2),
            "utm_source": utm_source,
            "utm_medium": utm_medium,
            "utm_campaign": utm_campaign,
            "tracking_url": tracking_url,
            "promo_code": promo_code,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        save_campaign(campaign)

        st.session_state.last_campaign = campaign

        st.success("Campaign created successfully!")


# ----------------------------------
# GENERATED TRACKING ASSETS
# ----------------------------------

if "last_campaign" in st.session_state:

    campaign = st.session_state.last_campaign

    st.divider()

    st.subheader("Generated Campaign Assets")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**Campaign ID**")
        st.code(campaign["campaign_id"])

        st.write("**Tracking URL**")
        st.code(
            campaign["tracking_url"],
            language=None
        )

        st.write("**Promo Code**")
        st.code(campaign["promo_code"])

        st.link_button(
            "🌶️ Open Store with Tracking",
            campaign["tracking_url"]
        )

    with col2:

        st.write("**Campaign QR Code**")

        qr_bytes = generate_qr_code(
            campaign["tracking_url"]
        )

        st.image(
            qr_bytes,
            width=220
        )

        st.download_button(
            "⬇️ Download QR Code",
            data=qr_bytes,
            file_name=campaign["campaign_id"] + ".png",
            mime="image/png"
        )



# ----------------------------------
# SAVED CAMPAIGNS - LIST VIEW
# ----------------------------------

st.divider()
st.subheader("📋 Saved Campaigns")

if CAMPAIGNS_FILE.exists():

    with open(
        CAMPAIGNS_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        campaigns = list(csv.DictReader(file))

    if campaigns:

        st.caption(f"{len(campaigns)} campaigns created")

        # Column headings
        h1, h2, h3, h4, h5 = st.columns(
            [3, 2, 1.5, 1.5, 1.5]
        )

        h1.write("**Campaign Name**")
        h2.write("**Channel**")
        h3.write("**Budget**")
        h4.write("**Campaign ID**")
        h5.write("**Actions**")

        st.divider()

        # One row per campaign
        for campaign in campaigns:

            campaign_id = campaign["campaign_id"]
            tracking_url = campaign["tracking_url"]

            col1, col2, col3, col4, col5 = st.columns(
                [3, 2, 1.5, 1.5, 1.5]
            )

            col1.write(campaign["campaign_name"])
            col2.write(campaign["channel"])
            col3.write(f"${campaign['budget']}")
            col4.write(campaign_id)

            with col5:
                if st.button(
                    "View Options",
                    key=f"view_{campaign_id}"
                ):
                    current = st.session_state.get(
                        "selected_campaign"
                    )

                    st.session_state.selected_campaign = (
                        None
                        if current == campaign_id
                        else campaign_id
                    )

            # Show options only for selected campaign
            if st.session_state.get(
                "selected_campaign"
            ) == campaign_id:

                with st.container(border=True):

                    st.write(
                        f"**{campaign['campaign_name']}**"
                    )

                    st.write(
                        f"Promo Code: {campaign['promo_code']}"
                    )

                    st.write("**Tracking Link**")

                    st.code(
                        tracking_url,
                        language=None
                    )

                    st.caption(
                        "Use the copy icon in the code box "
                        "to copy the tracking link."
                    )

                    st.link_button(
                        "🌶️ Open Store",
                        tracking_url
                    )

                    st.write("**QR Code**")

                    qr_bytes = generate_qr_code(
                        tracking_url
                    )

                    st.image(
                        qr_bytes,
                        width=180
                    )

                    st.download_button(
                        "⬇️ Download QR Code",
                        data=qr_bytes,
                        file_name=f"{campaign_id}.png",
                        mime="image/png",
                        key=f"download_{campaign_id}"
                    )

            st.divider()

    else:
        st.info("No campaigns created yet.")

else:
    st.info("No campaigns created yet.")
