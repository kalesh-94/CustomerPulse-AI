import re
import pandas as pd

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def standardize_columns(df):
    """
    Map dataset columns to standard schema
    """

    column_mapping = {
        "Ticket Description": "message",
        "Product Purchased": "product",
        "Ticket ID": "ticket_id",
        "Ticket Type": "ticket_type",
        "Ticket Subject": "subject"
    }

    df = df.rename(columns=column_mapping)

    return df


def clean_dataframe(df):
    df = standardize_columns(df)

    if "message" not in df.columns:
        raise ValueError(" 'message' column not found after mapping")

    df = df.dropna(subset=["message"])

    df["cleaned_text"] = df["message"].apply(clean_text)

    return df