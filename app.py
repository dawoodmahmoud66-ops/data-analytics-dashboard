import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم العالي الجودة
# ---------------------------------------------------------
st.set_page_config(
    page_title="منصة العرض التفاعلية لملفات الإكسيل 2026",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# نمط تصميم داكن وفاخر للبرزنتيشن
st.markdown("""
    <style>
    .stApp { background-color: #0b132b; color: #ffffff; direction: rtl; text-align: right; }
    
    /* بطاقات KPIs الرئيسية */
    .kpi-card {
        background: linear-gradient(135deg, #1c2541 0%, #0b132b 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #3a506b;
        border-right: 6px solid #48cae4;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        transition: transform 0.2s ease-in-out;
    }
    .kpi-title { color: #90e0ef; font-size: 14px; font-weight: 600; margin-bottom: 8px; }
    .kpi-value { color: #ffffff; font-size: 26px; font-weight: bold; }
    .kpi-sub { color: #48cae4; font-size: 12px; margin-top: 5px; }

    /* رأس الأقسام */
    .section-header {
        background-color: #1c2541;
        color: #00b4d8;
        padding: 12px 20px;
        font-weight: bold;
        font-size: 18px;
        border-radius: 8px;
        margin: 20px 0 15px 0;
        border-right: 4px solid #90e0ef;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 منصة العرض والتحليل التفاعلي لبيانات الإكسيل (Excel Presentation Hub)")
st.caption("عرض وسلاسة فائقة في تحليل الأرقام والبيانات المالية لعام 2026")
st.markdown("---")

# ---------------------------------------------------------
# 2. قراءة ملفات الإكسيل بأقصى سرعة (Fast Caching)
# ---------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner="جاري تحميل ومعالجة ملف الإكسيل بسرعة...")
def load_excel_file(file):
    try:
        # قراءة كافة الشيتات أو الشيت الأول
        xls = pd.ExcelFile(file)
        sheet_data = {}
        for sheet_name in xls.sheet_names:
            sheet_data[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
        return sheet_data
    except Exception as e:
        return None

# ---------------------------------------------------------
# 3. القائمة الجانبية: رفع الملف والفلاتر التفاعلية
# ---------------------------------------------------------
st.sidebar.header("📁 إدارة العرض والبيانات")

uploaded_file = st.sidebar.file_uploader(
    "رفع ملف Excel (.xlsx, .xls)", 
    type=["xlsx", "xls"]
)

sheet_data = None
selected_df = None

if uploaded_file is not None:
    sheet_data = load_excel_file(uploaded_file)
    if sheet_data:
        st.sidebar.success(f"تم تحميل الملف: {uploaded_file.name}")
        
        # اختيار ورقة العمل (Sheet)
        sheet_names = list(sheet_data.keys())
        selected_sheet = st.sidebar.selectbox("اختر الشيت للعرض:", sheet_names)
        selected_df = sheet_data[selected_sheet]
else:
    st.sidebar.info("💡 يمكنك رفع ملف إكسيل من القائمة للبدء أو استعراض العرض الافتراضي.")

# ---------------------------------------------------------
# 4. عرض البرزنتيشن والرسوم التفاعلية
# ---------------------------------------------------------
if selected_df is not None:
    st.markdown(f'<div class="section-header">📊 البيانات المستعرضة: {selected_sheet}</div>', unsafe_allow_html=True)
    
    # فلاتر تفاعلية للـ Columns الرقمية والنصية
    numeric_cols = selected_df.select_dtypes(include=['number']).columns.tolist()
    text_cols = selected_df.select_dtypes(include=['object', 'category']).columns.tolist()

    # أ) بطاقات KPI ديناميكية
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">إجمالي عدد السجلات</div>
                <div class="kpi-value">{len(selected_df):,}</div>
                <div class="kpi-sub">صف في الشيت</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        val_sum = selected_df[numeric_cols[0]].sum() if numeric_cols else 0
        col_label = numeric_cols[0] if numeric_cols else "لا يوجد"
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">إجمالي ({col_label})</div>
                <div class="kpi-value">{val_sum:,.2f}</div>
                <div class="kpi-sub">مجموع القيمة المالية</div>
            </div>
        ''', unsafe_allow_html=True)

    with col3:
        val_avg = selected_df[numeric_cols[0]].mean() if numeric_cols else 0
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">المتوسط الحسابي</div>
                <div class="kpi-value">{val_avg:,.2f}</div>
                <div class="kpi-sub">متوسط قيمة الصف</div>
            </div>
        ''', unsafe_allow_html=True)

    with col4:
        cols_count = len(selected_df.columns)
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">عدد الأعمدة</div>
                <div class="kpi-value">{cols_count}</div>
                <div class="kpi-sub">أعمدة البيانات</div>
            </div>
        ''', unsafe_allow_html=True)

    st.write("")

    # ب) رسوم بيانية تفاعلية سهلة الحركة
    if numeric_cols and text_cols:
        st.markdown('<div class="section-header">📉 الرسوم البيانية التفاعلية</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            fig_bar = px.bar(
                selected_df.head(20), 
                x=text_cols[0], 
                y=numeric_cols[0],
                color=text_cols[0],
                title=f"توزيع {numeric_cols[0]} حسب {text_cols[0]}",
                template="plotly_dark"
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            fig_pie = px.pie(
                selected_df.head(10), 
                names=text_cols[0], 
                values=numeric_cols[0],
                title=f"نسب الإسهام للـ 10 عناصر الأوائل",
                hole=0.4,
                template="plotly_dark"
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)

    # ج) جدول البيانات التفاعلي المباشر
    st.markdown('<div class="section-header">📋 جدول البيانات المفلتر (سريع الاستجابة)</div>', unsafe_allow_html=True)
    st.dataframe(selected_df, use_container_width=True)

else:
    # ---------------------------------------------------------
    # 5. العرض الافتراضي في حالة عدم رفع ملف بعد
    # ---------------------------------------------------------
    df_demo = pd.DataFrame({
        'البنك': ['ايجي بنك', 'العربي الافريقي', 'التنمية الصناعية', 'بنك مصر (توريق)', 'الأهلي الكويتي'],
        'عدد العقود': [36375, 108278, 4076, 23459, 60],
        'إجمالي القيمة المالية (جنيه)': [3017689935.90, 2345331028.98, 147465079.45, 683310830.35, 72711290.00]
    })

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي العقود</div><div class="kpi-value">{df_demo["عدد العقود"].sum():,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي قيمة المحفظة</div><div class="kpi-value">{df_demo["إجمالي القيمة المالية (جنيه)"].sum():,.2f} ج.م</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">عدد المؤسسات المصنفة</div><div class="kpi-value">5 مؤسسات</div></div>', unsafe_allow_html=True)

    st.write("")
    
    col_chart, col_tbl = st.columns([1.3, 1])
    with col_chart:
        fig = px.bar(df_demo, x='إجمالي القيمة المالية (جنيه)', y='البنك', orientation='h', 
                     text_auto='.3s', color='إجمالي القيمة المالية (جنيه)', template="plotly_dark",
                     title="توزيع قيم المحافظ بالبنوك 2026")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    with col_tbl:
        st.dataframe(df_demo, use_container_width=True, hide_index=True)
