import streamlit as st
import pandas as pd
import plotly.express as px
import docx
from pptx import Presentation

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="داشبورد التوريق والتخصيم 2026",
    page_icon="🏦",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #f4f6f8;
        color: #1a202c;
        direction: rtl;
        text-align: right;
    }
    
    /* بطاقات المخطط التوضيحي (Securitization Flow) */
    .flow-card {
        background-color: #fef08a;
        border: 2px solid #eab308;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .flow-title {
        font-weight: bold;
        font-size: 16px;
        color: #854d0e;
        margin-bottom: 8px;
    }
    .flow-body {
        font-size: 13px;
        color: #1e293b;
        text-align: right;
    }
    
    .arrow-box {
        background-color: #ea580c;
        color: white;
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        font-weight: bold;
        margin-top: 25px;
    }

    .kpi-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 18px;
        border-right: 5px solid #00c4cc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .kpi-title { color: #6c757d; font-size: 14px; font-weight: bold; }
    .kpi-value { color: #0b2847; font-size: 24px; font-weight: bold; margin-top: 5px; }
    
    .card-header {
        background-color: #0b2847;
        color: #ffffff;
        padding: 10px 15px;
        font-weight: bold;
        font-size: 16px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 لوحة تحكم إدارة التوريق والتخصيم - 2026")
st.markdown("---")

# ---------------------------------------------------------
# 2. القائمة الجانبية: رفع ملفات Word, Excel, PowerPoint
# ---------------------------------------------------------
st.sidebar.header("📁 رفع البيانات")
uploaded_file = st.sidebar.file_uploader(
    "قم برفع ملف Excel (.xlsx), Word (.docx) أو PowerPoint (.pptx)", 
    type=["xlsx", "csv", "docx", "pptx"]
)

uploaded_df = None
extracted_text_pptx = []

if uploaded_file is not None:
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    # 1. قراءة ملفات Excel / CSV
    if file_ext in ['xlsx', 'csv']:
        try:
            if file_ext == 'csv':
                uploaded_df = pd.read_csv(uploaded_file)
            else:
                uploaded_df = pd.read_excel(uploaded_file)
            st.sidebar.success("تم تحميل ملف Excel بنجاح!")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة ملف Excel: {e}")
            
    # 2. قراءة ملفات Word (.docx)
    elif file_ext == 'docx':
        try:
            doc = docx.Document(uploaded_file)
            tables_data = []
            for table in doc.tables:
                for row in table.rows:
                    tables_data.append([cell.text.strip() for cell in row.cells])
            
            if tables_data:
                uploaded_df = pd.DataFrame(tables_data[1:], columns=tables_data[0])
                st.sidebar.success("تم استخراج الجدول من ملف Word بنجاح!")
            else:
                st.sidebar.warning("لم يتم العثور على جداول داخل ملف Word.")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة ملف Word: {e}")

    # 3. قراءة ملفات PowerPoint (.pptx)
    elif file_ext == 'pptx':
        try:
            prs = Presentation(uploaded_file)
            tables_data = []
            
            for slide_num, slide in enumerate(prs.slides, 1):
                for shape in slide.shapes:
                    if shape.has_table:
                        table = shape.table
                        for row in table.rows:
                            tables_data.append([cell.text.strip() for cell in row.cells])
                    elif shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            if paragraph.text.strip():
                                extracted_text_pptx.append(f"• {paragraph.text.strip()}")
            
            if tables_data:
                uploaded_df = pd.DataFrame(tables_data[1:], columns=tables_data[0])
                st.sidebar.success("تم استخراج الجدول من ملف PowerPoint بنجاح!")
            elif extracted_text_pptx:
                st.sidebar.success("تم استخراج النصوص من شرائح PowerPoint بنجاح!")
            else:
                st.sidebar.warning("الملف لا يحتوي على نصوص أو جداول قابلة للقراءة.")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة ملف PowerPoint: {e}")

# ---------------------------------------------------------
# 3. مخطط "كيف تعمل عملية التوريق المالي" (Securitization Diagram)
# ---------------------------------------------------------
st.markdown("### 🔄 كيف تعمل عملية التوريق المالي (How Securitization Works)")

c1, c2, c3, c4, c5 = st.columns([1.2, 0.8, 1.5, 0.8, 1.2])

with c1:
    st.markdown("""
        <div class="flow-card" style="background-color: #dbeafe; border-color: #3b82f6;">
            <div class="flow-title" style="color: #1e40af;">🏦 مُنشئ الأصول (Asset Originator)</div>
            <div class="flow-body">الشركة أو البنك الذي يمتلك الحقوق المالية والعقود الأصلية.</div>
        </div>
        <div class="flow-card">
            <div class="flow-title">📋 الأصول المضمونة</div>
            <div class="flow-body">
                • محفظة المرجعية ("الضمانات")<br>
                • عقود سيارات / كروت / شيكات
            </div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
        <div class="arrow-box">
            1️⃣ تحويل الأصول
        </div>
        <div style="font-size: 11px; text-align: center; color: #475569; margin-top: 5px;">
            انتقال الملكية القانونية من المنشئ إلى الشركة التمويلية
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
        <div class="flow-card" style="background-color: #dbeafe; border-color: #3b82f6;">
            <div class="flow-title" style="color: #1e40af;">🏢 الجهة المصدرة (SPV)</div>
            <div class="flow-body">شركة التوريق ذات الغرض الخاص (Special Purpose Vehicle)</div>
        </div>
        <div class="flow-card">
            <div class="flow-title">🛡️ حماية الأصول والتصنيف</div>
            <div class="flow-body">
                • الأصول معزولة تماماً عن إفلاس المنشئ.<br>
                • لا يحتفظ المنشئ بأي حقوق قانونية في الأصول.<br>
                • يتم تقييمها بواسطة وكالات التصنيف الائتماني.
            </div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
        <div class="arrow-box">
            2️⃣ إصدار السندات
        </div>
        <div style="font-size: 11px; text-align: center; color: #475569; margin-top: 5px;">
            إصدار سندات وأوراق مالية مدعومة بالأصول للمستثمرين
        </div>
    """, unsafe_allow_html=True)

with c5:
    st.markdown("""
        <div class="flow-card" style="background-color: #dbeafe; border-color: #3b82f6;">
            <div class="flow-title" style="color: #1e40af;">📈 مستثمرو سوق المال</div>
            <div class="flow-body">البنوك والمؤسسات وصناديق الاستثمار</div>
        </div>
        <div class="flow-card">
            <div class="flow-title">📑 الشرائح التمويلية (Tranches)</div>
            <div class="flow-body">
                <b>• الشريحة الممتازة (Senior):</b> أقل مخاطرة وأعلى تصنيف.<br>
                <b>• الشريحة المتوسطة (Mezzanine):</b> مخاطرة وعائد متوسطان.<br>
                <b>• الشريحة المبتدئة (Junior):</b> أعلى عائد وأعلى مخاطرة.
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# 4. عرض المحتوى المرفوع (جداول أو نصوص PowerPoint)
# ---------------------------------------------------------
if uploaded_df is not None:
    st.markdown('<div class="card-header">📄 الجداول المستخرجة من الملف المرفوع</div>', unsafe_allow_html=True)
    st.dataframe(uploaded_df, use_container_width=True)

if extracted_text_pptx:
    st.markdown('<div class="card-header">📊 النصوص المستخرجة من عرض PowerPoint</div>', unsafe_allow_html=True)
    for line in extracted_text_pptx:
        st.write(line)

if uploaded_df is None and not extracted_text_pptx:
    # البيانات الافتراضية
    df_card_normal = pd.DataFrame({
        'البنك': ['ايجي بنك', 'العربي الافريقي', 'التنمية الصناعية'],
        'Total Count': [36375, 108278, 4076],
        'Total Formal AR': [3017689935.90, 2345331028.98, 147465079.45]
    })

    tot_count = df_card_normal['Total Count'].sum()
    tot_val = df_card_normal['Total Formal AR'].sum()

    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي عدد الملفات والعقود</div><div class="kpi-value">{tot_count:,} ملف</div></div>', unsafe_allow_html=True)
    with col_k2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي المحفظة المالية</div><div class="kpi-value">{tot_val:,.2f} ج.م</div></div>', unsafe_allow_html=True)

    st.write("")
    fig1 = px.bar(df_card_normal, x='Total Formal AR', y='البنك', orientation='h', text_auto='.3s',
                  title="توزيع القيمة المالية بحسب البنك", color_discrete_sequence=['#ea580c'])
    st.plotly_chart(fig1, use_container_width=True)
