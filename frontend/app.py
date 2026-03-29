import streamlit as st
import pandas as pd
import requests
import plotly.express as px

API_BASE_URL = "http://52.66.34.73:8000"

st.set_page_config(page_title="CustomerPulse AI", layout="wide")

st.title("CustomerPulse AI Dashboard")
st.markdown("AI-powered insights for customer support tickets")

# ---------------- FETCH DATA ----------------
def fetch_insights():
    try:
        res = requests.get(f"{API_BASE_URL}/insights")
        if res.status_code == 200:
            return res.json()
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


# ---------------- SIDEBAR UPLOAD ----------------
st.sidebar.header("Upload Data")

uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv", "xlsx"])

if uploaded_file:
    if st.sidebar.button("Process CSV"):
        with st.spinner("Processing..."):
            res = requests.post(
            f"{API_BASE_URL}/upload",
            files={"file": uploaded_file}
            )

            if res.status_code == 200:
                st.sidebar.success("Uploaded & Processed!")
                st.rerun()
            else:
                st.sidebar.error(res.text)


# ---------------- FETCH INSIGHTS ----------------
data = fetch_insights()

if data and data.get("total_tickets", 0) > 0:

    st.markdown("---")

    # ---------------- METRICS ----------------
    col1, col2, col3 = st.columns(3)

    total = data.get("total_tickets", 0)
    sentiments = data.get("sentiment_distribution", {})
    categories = data.get("category_distribution", [])

    negative_count = sentiments.get("Negative", 0)

    col1.metric("Total Tickets", total)
    col2.metric("Negative Tickets", negative_count)
    col3.metric("Categories", len(categories))

    st.markdown("---")
    col4, col5 = st.columns(2)
    
    neg_percent = (negative_count / total) * 100 if total else 0
    col4.metric("Negative %", f"{neg_percent:.2f}%")
    
    top_cat = max(categories, key=lambda x: x["count"]) if categories else {}
    col5.metric("Top Issue", top_cat.get("category", "-"))
    
    
    st.markdown("---")

    # ---------------- CHARTS ----------------
    c1, c2 = st.columns(2)

    # CATEGORY CHART
    with c1:
        st.subheader(" Category Distribution")

        if categories:
            df_cat = pd.DataFrame(categories)
            fig = px.bar(df_cat, x="category", y="count", color="category")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No category data")

    # SENTIMENT CHART
    with c2:
        st.subheader(" Sentiment Distribution")

        if sentiments:
            df_sent = pd.DataFrame(
                [{"sentiment": k, "count": v} for k, v in sentiments.items()]
            )
            fig = px.pie(df_sent, names="sentiment", values="count")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sentiment data")

    st.markdown("---")
    
    fig = px.bar(df_cat, y="category", x="count", orientation="h")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

    # ---------------- LLM SUMMARY ----------------
    st.subheader("AI Business Insight")

    summary = data.get("summary", "")
    if summary:
        st.success(summary)
    else:
        st.warning("No summary available")

    st.markdown("---")

    # ---------------- SAMPLE TICKETS ----------------
    st.subheader("Recent Tickets")

    tickets = data.get("sample_tickets", [])

    if tickets:
        df = pd.DataFrame(tickets)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No tickets available")

    st.markdown("---")

    # ---------------- ADD SINGLE TICKET ----------------
    st.subheader("Add New Ticket")

    with st.form("ticket_form"):
        msg = st.text_area("Enter customer issue")
        submitted = st.form_submit_button("Analyze")

        if submitted and msg:
            with st.spinner("Analyzing..."):
                res = requests.post(
                    f"{API_BASE_URL}/tickets",
                    json={"message": msg}
                )

                if res.status_code == 200:
                    result = res.json()

                    st.success("Processed!")

                    st.write("**Category:**", result.get("category"))
                    st.write("**Sentiment:**", result.get("sentiment"))
                    st.write("**Suggested Reply:**", result.get("suggested_reply"))

                else:
                    st.error(res.text)

else:
    st.info("Upload data to see insights")
