
import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile
from io import BytesIO
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="💿 Data Sweeper", layout="wide")

# Dark Mode Toggle
dark_mode = st.toggle("🌙 Dark Mode", value=True)

def set_theme():
    return "plotly_dark" if dark_mode else "plotly_white"

st.title("💿 Data Sweeper")
st.write("**Transform & Enhance Your CSV and Excel Files Instantly!**")

# File uploader
uploaded_files = st.file_uploader("📤 Upload your CSV or Excel files:", type=["csv", "xlsx"], accept_multiple_files=True)

# Process uploaded files
processed_files = []
if uploaded_files:
    for file in uploaded_files:
        file_name = file.name
        file_ext = os.path.splitext(file_name)[-1].lower()
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine='openpyxl')
            else:
                st.error(f"❌ Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"❌ Error reading the file: {e}")
            continue

            st.subheader(f"📂 {file_name}")
            st.write(f"**File Size:** {file.size / 1024:.2f} KB")
            
            # Data Preview
            with st.expander("🔍 Preview Data"):
                st.dataframe(df.head())

            # Data Cleaning Options
            st.subheader("🛠 Data Cleaning Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"🗑 Remove Duplicates - {file_name}"):
                    df.drop_duplicates(inplace=True)
                    st.success("Duplicates removed!")

            with col2:
                if st.button(f"📌 Fill Missing Values - {file_name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("Missing values filled!")
            
            with col3:
                if st.button(f"🚮 Drop Empty Columns - {file_name}"):
                    df.dropna(axis=1, how='all', inplace=True)
                    st.success("Empty columns removed!")
            
            # Text Standardization
            if st.checkbox(f"🔠 Convert Text to Lowercase - {file_name}"):
                text_cols = df.select_dtypes(include=['object']).columns
                df[text_cols] = df[text_cols].astype(str).apply(lambda x: x.str.lower())
                st.success("Text converted to lowercase!")

            # Data Visualization
            st.subheader("📊 Data Visualization")
            numeric_columns = df.select_dtypes(include=['number']).columns
            if len(numeric_columns) >= 2:
                chart_type = st.selectbox("Choose chart type:", ["Bar Chart", "Pie Chart", "Line Chart"], key=file_name)
                x_col = st.selectbox("Select X-axis:", numeric_columns, key=f"x_{file_name}")
                y_col = st.selectbox("Select Y-axis:", numeric_columns, key=f"y_{file_name}")
                
                if chart_type == "Bar Chart":
                    fig = px.bar(df, x=x_col, y=y_col, title="Bar Chart", template=set_theme())
                elif chart_type == "Pie Chart":
                    fig = px.pie(df, names=x_col, values=y_col, title="Pie Chart", template=set_theme())
                elif chart_type == "Line Chart":
                    fig = px.line(df, x=x_col, y=y_col, title="Line Chart", template=set_theme())
                
                st.plotly_chart(fig)
            
            # File Conversion Options
            st.subheader("📁 Convert & Download")
            conversion_type = st.radio("Convert to:", ["CSV", "Excel"], key=f"convert_{file_name}")
            buffer = BytesIO()
            new_file_name = file_name.replace(file_ext, ".csv" if conversion_type == "CSV" else ".xlsx")
            
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False, engine='openpyxl')
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            buffer.seek(0)
            processed_files.append((new_file_name, buffer, mime_type))

            # Download Button
            st.download_button(
                label=f"⬇️ Download {new_file_name}",
                data=buffer,
                file_name=new_file_name,
                mime=mime_type,
            )

# Download all processed files as a ZIP
if processed_files:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
        with zipfile.ZipFile(tmp_zip, 'w') as zipf:
            for file_name, buffer, _ in processed_files:
                zipf.writestr(file_name, buffer.getvalue())
        
    with open(tmp_zip.name, "rb") as f:
        st.download_button(
            label="⬇️ Download All Processed Files as ZIP",
            data=f,
            file_name="processed_files.zip",
            mime="application/zip",
        )

st.success("🎉 Processing Completed!")
