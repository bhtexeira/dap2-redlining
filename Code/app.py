import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Data Center Impact on Illinois",
    layout="wide"
)

# -----------------------------
# Sidebar navigation
# -----------------------------
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select view",
    ["Welcome","plot 1", "plot 2", "comparison table"],
    index=0
)

# -----------------------------
# Placeholder data (replace later)
# -----------------------------
@st.cache_data
def load_data():
    np.random.seed(42)
    df = pd.DataFrame({
        "category": list("ABCDE"),
        "value": np.random.randint(10, 100, 5),
        "value2": np.random.randint(5, 80, 5)
    })
    return df

df = load_data()

# =============================
# Welcome Page
# =============================
if page == "Welcome":
    st.title("Data Center Impact on Illinois")

    st.markdown(
        """
        Welcome to the **Illinois Data Center Impact Dashboard**.

        This tool provides exploratory views of data center activity and
        associated impact metrics across Illinois.

        **Use the sidebar to navigate:**

        - **Plot 1** — Primary metric visualization  
        - **Plot 2** — Secondary relationship view  
        - **Comparison Table** — Underlying data inspection
        """
    )

    st.info("Select a view from the sidebar to begin.")

# -----------------------------
# Page: Plot 1
# -----------------------------
if page == "plot 1":
    st.subheader("Plot 1")

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("category:N", title="Category"),
            y=alt.Y("value:Q", title="Value"),
            tooltip=["category", "value"]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, width="stretch")

# -----------------------------
# Page: Plot 2
# -----------------------------
elif page == "plot 2":
    st.subheader("Plot 2")

    chart = (
        alt.Chart(df)
        .mark_circle(size=100)
        .encode(
            x=alt.X("value:Q", title="Value"),
            y=alt.Y("value2:Q", title="Value 2"),
            tooltip=["category", "value", "value2"]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, width="stretch")

# -----------------------------
# Page: Comparison Table
# -----------------------------
elif page == "comparison table":
    st.subheader("Comparison Table")
    st.dataframe(df, width="stretch")

# -----------------------------
# Footer (optional but useful)
# -----------------------------
st.caption("Let's update with real things!!!")
