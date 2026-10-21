import streamlit as st
import pandas as pd
import plotly.express as px
import docx
from docx import Document
from pptx import Presentation
from pptx.util import Inches
import io
import os

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="لوحة تحكم ومحول ملفات التوريق والتخصيم 2026",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #071e33; color: #ffffff; direction: rtl; text-align: right; }
    .kpi-card { background-color: #0b2847; border-radius: 12px; padding: 20px; border-right: 5px solid #00c4cc; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .kpi-title { color: #90caf9; font-size: 14px; font-weight: bold; }
    .kpi-value { color: #00c4cc; font-size: 24px; font-weight: bold; margin-top: 5px; }
    .card-header { background-color: #0b2847; color: #ffffff; padding: 10px 15px; font-weight: bold; font-size: 16px; border-radius: 6px; margin-bottom: 15px; border-right: 3px solid #00c4cc; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 لوحة تحكم التخصيم والتوريق ومحول الملفات - 2026")
st.markdown("---")

# ---------------------------------------------------------
# 2. دوال تحويل الجداول بين الصيغ (Excel / Word / PowerPoint)
# ---------------------------------------------------------
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

def convert_df_to_word(df, title="جدول البيانات المستخرج"):
    doc = Document()
    doc.add_heading(title, level=1)
    table = doc.add_table(rows=df.shape[0] + 1, cols=df.shape[1])
    table.style = 'Table Grid'
    for j, col_name in enumerate(df.columns):
        table.cell(0, j).text = str(col_name)
    for i, row in enumerate(df.values):
        for j, val in enumerate(row):
            table.cell(i + 1, j).text = str(val) if pd.notna(val) else ""
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()

def convert_df_to_pptx(df):
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
# 3. القائمة الجانبية: رفع الملفات لقراءتها وتحويلها
# ---------------------------------------------------------
st.sidebar.header("📁 رفع بيانات جديدة وتحويلها")
uploaded_file = st.sidebar.file_uploader(
    "قم برفع ملف (Excel, Word, PowerPoint)", 
    type=["xlsx", "xls", "csv", "docx", "pptx"]
)

uploaded_df = None
extracted_text_pptx = []

if uploaded_file is not None:
    file_name = uploaded_file.name
    file_ext = os.path.splitext(file_name)[1].lower()

    # أ) ملفات Excel
    if file_ext in ['.xlsx', '.xls', '.csv']:
        try:
            uploaded_df = pd.read_csv(uploaded_file) if file_ext == '.csv' else pd.read_excel(uploaded_file)
            st.sidebar.success(f"تم تحميل الملف: {file_name}")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة Excel: {e}")

    # ب) ملفات Word
    elif file_ext == '.docx':
        try:
            doc = Document(uploaded_file)
            tables_data = []
            for table in doc.tables:
                for row in table.rows:
                    tables_data.append([cell.text.strip() for cell in row.cells])
            if len(tables_data) > 1:
                uploaded_df = pd.DataFrame(tables_data[1:], columns=tables_data[0])
                st.sidebar.success(f"تم تحميل الجدول من Word: {file_name}")
            else:
                st.sidebar.warning("لم يتم العثور على جداول في ملف Word.")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة Word: {e}")

    # ج) ملفات PowerPoint
    elif file_ext == '.pptx':
        try:
            prs = Presentation(uploaded_file)
            tables_data = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if shape.has_table:
                        for row in shape.table.rows:
                            tables_data.append([cell.text.strip() for cell in row.cells])
                    elif shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            if paragraph.text.strip():
                                extracted_text_pptx.append(paragraph.text.strip())
            if len(tables_data) > 1:
                uploaded_df = pd.DataFrame(tables_data[1:], columns=tables_data[0])
                st.sidebar.success(f"تم تحميل الجدول من PowerPoint: {file_name}")
            elif extracted_text_pptx:
                st.sidebar.success(f"تم استخراج النصوص من PowerPoint: {file_name}")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة PowerPoint: {e}")

# ---------------------------------------------------------
# 4. عرض خيارات التحويل والتحميل إذا تم رفع ملف
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
    st.subheader("📋 معاينة البيانات المستخرجة:")
    st.dataframe(uploaded_df, use_container_width=True)

if extracted_text_pptx and uploaded_df is None:
    st.markdown('<div class="card-header">📊 النصوص المستخرجة من PowerPoint</div>', unsafe_allow_html=True)
    for line in extracted_text_pptx:
        st.write(f"• {line}")

# ---------------------------------------------------------
# 5. عرض الداشبورد والبيانات المالية الأصلية لـ 2026
# ---------------------------------------------------------
st.markdown("---")

df_card_normal = pd.DataFrame({
    'البنك': ['ايجي بنك', 'العربي الافريقي', 'التنمية الصناعية'],
    'Total Count': [36375, 108278, 4076],
    'Total Formal AR': [3017689935.90, 2345331028.98, 147465079.45]
})

df_auto = pd.DataFrame({
    'البنك': ['بنك العربي الافريقي', 'بنك التنمية الصناعية', 'بنك التنمية الصادرات', 'بنك نكست', 'الاهلي الكويتي', 'EG Bank', 'CIB'],
    'Total Count': [399, 242, 70, 52, 60, 47, 7],
    'Total Formal AR': [378159243.14, 286656298.62, 132228120.50, 97596271.76, 72711290.00, 44886737.53, 24402500.00]
})

df_sec = pd.DataFrame({
    'المحفظة / البنك': ['Sce 13 (بنك مصر)'],
    'Total Count': [23459],
    'Total Sum of AR': [683310830.35]
})

tot_count = df_card_normal['Total Count'].sum() + df_auto['Total Count'].sum() + df_sec['Total Count'].sum()
tot_val = df_card_normal['Total Formal AR'].sum() + df_auto['Total Formal AR'].sum() + df_sec['Total Sum of AR'].sum()

# المؤشرات
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي عدد الملفات والعقود</div><div class="kpi-value">{tot_count:,} ملف</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي المحفظة المالية</div><div class="kpi-value">{tot_val:,.2f} ج.م</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">عدد البنوك والمؤسسات المشاركة</div><div class="kpi-value">8 بنوك</div></div>', unsafe_allow_html=True)

st.write("")

# التبويبات والرسوم البيانية
tab1, tab2, tab3 = st.tabs(["💳 الكروت والطلب العادي", "🚗 عقود السيارات (Auto)", "🏦 التوريق (Securitization)"])

with tab1:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        fig1 = px.bar(df_card_normal, x='Total Formal AR', y='البنك', orientation='h', text_auto='.3s',
                      title="القيمة المالية بحسب البنك (جنيه مصري)", color_discrete_sequence=['#00c4cc'])
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.dataframe(df_card_normal, use_container_width=True, hide_index=True)

with tab2:
    col1, col2 = st.columns([1.2, 1])
    with col1:
        fig2 = px.bar(df_auto, x='Total Formal AR', y='البنك', orientation='h', text_auto='.3s',
                      title="توزيع قيم عقود السيارات بالبنوك", color_discrete_sequence=['#26c6da'])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.dataframe(df_auto, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("محفظة التوريق - بنك مصر")
    st.dataframe(df_sec, use_container_width=True, hide_index=True)
