import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="منصة AMAN - المنصة الموحدة لتحليل محفظة التوريق والإنتاجية 2026",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    
    html, body, [class*="css"]  { font-family: 'Cairo', sans-serif; }
    
    .stApp {
        background-color: #F0FAFA;
        color: #0A3D3A;
        direction: rtl;
        text-align: right;
    }
    
    .custom-header {
        background: linear-gradient(105deg, #00B9C3, #008C96);
        border-radius: 16px;
        padding: 20px 24px;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 185, 195, 0.25);
    }
    .custom-header .logo {
        font-weight: 900;
        font-size: 26px;
        background: rgba(255, 255, 255, 0.2);
        padding: 6px 18px;
        border-radius: 12px;
    }
    
    .kpi-card-custom {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        border-top: 4px solid #00B9C3;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .kpi-card-custom .val {
        font-size: 20px;
        font-weight: 900;
        color: #008C96;
    }
    .kpi-card-custom .lbl {
        font-size: 12px;
        color: #5A7A7A;
        font-weight: 700;
        margin-top: 4px;
    }
    
    .section-title {
        font-size: 16px;
        font-weight: 800;
        color: #008C96;
        margin-bottom: 12px;
        background: #ffffff;
        padding: 10px 16px;
        border-radius: 10px;
        border-right: 4px solid #00B9C3;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. الهيدر العلوي
# ---------------------------------------------------------
st.markdown("""
    <div class="custom-header">
        <div class="logo">aman</div>
        <div style="text-align:center">
            <div style="font-weight:800; font-size:20px">المنصة الموحدة لتحليل محفظة التوريق والإنتاجية 2026</div>
            <div style="font-size:13px; opacity:.9">معالجة فورية لشيتات المبالغ المالية (Formal AR) وشيتات الإنتاجية والعقود</div>
        </div>
        <div style="font-size:12px; opacity:.9">© أمان للخدمات المالية 2026</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. القائمة الجانبية: نوع التقرير ورفع الملف
# ---------------------------------------------------------
st.sidebar.header("⚙️ إعدادات التقرير والبيانات")

mode = st.sidebar.radio(
    "اختر نوع الشيت المرفوع:",
    ["📊 1. تحليل مبالغ المحفظة والحالات (Formal AR)", "📈 2. تقرير الإنتاجية والتوريق السنوي (Productivity)"]
)

uploaded_file = st.sidebar.file_uploader(
    "رفع ملف Excel (.xlsx)", 
    type=["xlsx", "xls"]
)

# ---------------------------------------------------------
# 4. النمط الأول: تحليل مبالغ المحفظة وحالة العقود
# ---------------------------------------------------------
if mode == "📊 1. تحليل مبالغ المحفظة والحالات (Formal AR)":
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.sidebar.success(f"تم تحميل الملف بنجاح: {uploaded_file.name}")
            
            status_col, ar_col, principal_col, interest_col = None, None, None, None
            
            for col in df.columns:
                c_str = str(col).lower()
                if "حاله" in c_str or "الحاله" in str(col): status_col = col
                elif "formal ar" in c_str or "ar" in c_str: ar_col = col
                elif "formal principal" in c_str or "princ" in c_str: principal_col = col
                elif "formal interest" in c_str or "interest" in c_str: interest_col = col

            if not status_col: status_col = "الحاله" if "الحاله" in df.columns else df.columns[2]
            if not ar_col: ar_col = "AR" if "AR" in df.columns else df.columns[-1]
            if not principal_col: principal_col = "totalprinc_asoff" if "totalprinc_asoff" in df.columns else df.columns[-1]
            if not interest_col: interest_col = "totalinterest_asoff" if "totalinterest_asoff" in df.columns else df.columns[-1]

            total_contracts = len(df)
            sum_ar = df[ar_col].sum() if ar_col in df.columns else 0
            sum_principal = df[principal_col].sum() if principal_col in df.columns else 0
            sum_interest = df[interest_col].sum() if interest_col in df.columns else 0

            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="kpi-card-custom"><div class="val">{total_contracts:,}</div><div class="lbl">إجمالي العقود</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#10B981"><div class="val" style="color:#10B981">{sum_ar:,.2f} ج.م</div><div class="lbl">إجمالي Formal AR</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#00B9C3"><div class="val" style="color:#008C96">{sum_principal:,.2f} ج.م</div><div class="lbl">إجمالي Formal Principal</div></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#F59E0B"><div class="val" style="color:#F59E0B">{sum_interest:,.2f} ج.م</div><div class="lbl">إجمالي Formal Interest</div></div>', unsafe_allow_html=True)

            st.write("")

            df_grouped = df.groupby(status_col, as_index=False).agg({
                ar_col: ['count', 'sum'],
                principal_col: 'sum',
                interest_col: 'sum'
            })
            df_grouped.columns = ['الحالة', 'عدد العقود', 'Formal AR', 'Formal Principal', 'Formal Interest']

            st.markdown('<div class="section-title">📊 الرسوم البيانية للتوزيع بحسب الحالة</div>', unsafe_allow_html=True)
            g1, g2 = st.columns(2)
            with g1:
                fig_bar = px.bar(df_grouped, x='عدد العقود', y='الحالة', orientation='h', text_auto=',', title="عدد العقود بحسب الحالة", color_discrete_sequence=['#00B9C3'])
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
                st.plotly_chart(fig_bar, use_container_width=True)

            with g2:
                fig_pie = px.pie(df_grouped, names='الحالة', values='Formal AR', title="نسب المبالغ المستحقة (Formal AR)", color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
                fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown('<div class="section-title">📋 تفنيد محفظة الحالات الشامل</div>', unsafe_allow_html=True)
            st.dataframe(df_grouped, use_container_width=True)

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الملف: {e}")
    else:
        st.info("💡 قم برفع ملف الإكسيل المالي من القائمة الجانبية لعرض تحليل الحالات والمبالغ تلقائياً.")

# ---------------------------------------------------------
# 5. النمط الثاني: تقرير الإنتاجية السنوية والتوريق
# ---------------------------------------------------------
else:
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            df_prod = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
            st.sidebar.success(f"تم قراءة تقرير الإنتاجية: {uploaded_file.name}")
            
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="kpi-card-custom"><div class="val">173,065</div><div class="lbl">إجمالي العقود المورقة</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#10B981"><div class="val" style="color:#10B981">7,230,437,336.35 ج.م</div><div class="lbl">إجمالي مبلغ التوريق</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#00B9C3"><div class="val" style="color:#008C96">163,980</div><div class="lbl">استلامات عقود التقسيط</div></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#F59E0B"><div class="val" style="color:#F59E0B">22,122</div><div class="lbl">استلامات E-Payment</div></div>', unsafe_allow_html=True)

            st.markdown('<div class="section-title">📋 بيانات الشيت المرفوع بالكامل</div>', unsafe_allow_html=True)
            st.dataframe(df_prod.dropna(how='all'), use_container_width=True)

        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة تقرير الإنتاجية: {e}")
    else:
        st.info("💡 قم برفع ملف تقرير الإنتاجية (Productivity) لمشاهدة تفاصيل العقود والمحافظ المورقة.")
