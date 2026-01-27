from io import BytesIO
import pandas as pd


def to_xlsx_multiple_sheets(sheets: dict) -> bytes:
    """
    sheets: {"NombreHoja": dataframe}
    """
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=name[:31])  # Excel max 31 chars
    return bio.getvalue()
