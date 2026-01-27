from io import BytesIO
import pandas as pd


def actions_to_xlsx_bytes(actions_df: pd.DataFrame, sheet_name: str = "Acciones") -> bytes:
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        actions_df.to_excel(writer, index=False, sheet_name=sheet_name)
    return bio.getvalue()

