import streamlit as st
import pandas as pd
import docx
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
import openpyxl
import io
import os

st.set_page_config(
    page_title="داشبورد التوريق ومحول الملفات",
    page_icon="🔄",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #071e33; color: #ffffff; direction: rtl; text-align: right; }
    .kpi-card { background-color: #0b2847; border-radius: 12px; padding: 20px; border-right: 5px solid #00c4cc; }
    .kpi-title { color: #90caf9; font-size: 14px; font-weight: bold; }
    .kpi-value { color: #00c4cc; font-size: 24px; font-weight: bold; }
    .card-header { background-color: #0b2847; color: #ffffff; padding: 10px 15px; font-weight: bold; font-size: 16px; border-radius: 6px; margin-bottom: 15px; border-right: 3px solid #00c4cc; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 لوحة التحكم ومحول الصيغ (Word / Excel / PowerPoint)")
st.markdown("---")

# ---------------------------------------------------------
# وظائف تحويل صيغ الملفات (Conversion Logic)
# ---------------------------------------------------------

def convert_df_to_excel(df):
    """تحويل الجدول إلى Excel"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

def convert_df_to_word(df, title="جدول البيانات المستخرج"):
    """تحويل الجدول إلى Word"""
    doc = Document()
    doc.add_heading(title, level=1)
    
    table = doc.add_table(rows=df.shape[0] + 1, cols=df.shape[1])
    table.style = 'Table Grid'
    
    # إضافة العناوين
    for j, col_name in enumerate(df.columns):
        table.cell(0, j).text = str(col_name)
        
    # إضافة البيانات
    for i, row in enumerate(df.values):
        for j, val in enumerate(row):
            table.cell(i + 1, j).text = str(val) if pd.notna(val) else ""
            
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

def convert_df_to_pptx(df, title="عرض البيانات"):
    """تحويل الجدول إلى PowerPoint"""
    prs = Presentation()
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)
    
    rows, cols = df.shape[0] + 1, df.shape[1]
    left, top, width, height = Inches(0.5), Inches(0.5), Inches(9), Inches(5)
    
    table_shape = slide.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    
    for j, col_name in enumerate(df.columns):
        table.cell(0, j).text = str(col_name)
        
    for i, row in enumerate(df.values):
        for j, val in enumerate(row):
            table.cell(i + 1, j).text = str(val) if pd.notna(val) else ""
            
    output = io.BytesIO()
    prs.save(output)
    return output.getvalue()

# ---------------------------------------------------------
# الشريط الجانبي: رفع الملف واختيار صيغة التحويل
# ---------------------------------------------------------
st.sidebar.header("📁 رفع وتحويل الملفات")

uploaded_file = st.sidebar.file_uploader(
    "رفع ملف (Excel, Word, PowerPoint)", 
    type=["xlsx", "xls", "csv", "docx", "pptx"]
)

uploaded_df = None

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # 1. قراءة Excel
    if file_ext in ['.xlsx', '.xls', '.csv']:
        try:
            uploaded_df = pd.read_csv(uploaded_file) if file_ext == '.csv' else pd.read_excel(uploaded_file)
            st.sidebar.success(file_name)
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة Excel: {e}")

    # 2. قراءة Word
    elif file_ext == '.docx':
        try:
            doc = Document(uploaded_file)
            tables_data = []
            for table in doc.tables:
                for row in table.rows:
                    tables_data.append([cell.text.strip() for cell in row.cells])
            if len(tables_data) > 1:
                uploaded_df = pd.DataFrame(tables_data[1:], columns=tables_data[0])
                st.sidebar.success(file_name)
            else:
                st.sidebar.warning("لم يتم العثور على جدول في Word.")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة Word: {e}")

    # 3. قراءة PowerPoint
    elif file_ext == '.pptx':
        try:
            prs = Presentation(uploaded_file)
            tables_data = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if shape.has_table:
                        for row in shape.table.rows:
                            tables_data.append([cell.text.strip() for cell in row.cells])
            if len(tables_data) > 1:
                uploaded_df = pd.DataFrame(tables_data[1:], columns=tables_data[0])
                st.sidebar.success(file_name)
            else:
                st.sidebar.warning("لم يتم العثور على جدول في PowerPoint.")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة PowerPoint: {e}")

# ---------------------------------------------------------
# خيارات التحويل والتحميل
# ---------------------------------------------------------
if uploaded_df is not None:
    st.markdown('<div class="card-header">🔄 تحويل صيغة الملف المرفوع وتحميله</div>', unsafe_allow_html=True)
    
    col_sel, col_btn = st.columns([2, 1])
    
    with col_sel:
        target_format = st.selectbox(
            "اختر الصيغة الجديدة لتحميل الملف بها:",
            ["PowerPoint (.pptx)", "Word (.docx)", "Excel (.xlsx)"]
        )
        
    with col_btn:
        st.write("")
        st.write("")
        if target_format == "Excel (.xlsx)":
            file_bytes = convert_df_to_excel(uploaded_df)
            st.download_button("📥 تحميل كـ Excel", file_bytes, file_name="Converted_Data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
        elif target_format == "Word (.docx)":
            file_bytes = convert_df_to_word(uploaded_df)
            st.download_button("📥 تحميل كـ Word", file_bytes, file_name="Converted_Data.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
        elif target_format == "PowerPoint (.pptx)":
            file_bytes = convert_df_to_pptx(uploaded_df)
            st.download_button("📥 تحميل كـ PowerPoint", file_bytes, file_name="Converted_Data.pptx", mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

    st.markdown("---")
    st.subheader("📋 معاينة البيانات المرفوعة:")
    st.dataframe(uploaded_df, use_container_width=True)

else:
    # البيانات الافتراضية للداشبورد في حالة عدم رفع ملف
    st.info("قم برفع ملف Excel أو Word أو PowerPoint من الشريط الجانبي لاستعراضه أو تحويله للصيغ الأخرى.")
