import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="داشبورد تحليل محفظة العقود والتوريق 2026",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #071e33; color: #ffffff; direction: rtl; text-align: right; }
    
    .kpi-card { 
        background-color: #0b2847; 
        border-radius: 12px; 
        padding: 18px; 
        border-right: 5px solid #00c4cc; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
        margin-bottom: 15px;
    }
    .kpi-title { color: #90caf9; font-size: 13px; font-weight: bold; }
    .kpi-value { color: #00c4cc; font-size: 21px; font-weight: bold; margin-top: 5px; }
    .kpi-sub { color: #b0bec5; font-size: 11px; margin-top: 3px; }
    
    .card-header { 
        background-color: #0b2847; 
        color: #ffffff; 
        padding: 10px 15px; 
        font-weight: bold; 
        font-size: 16px; 
        border-radius: 6px; 
        margin-bottom: 15px; 
        border-right: 3px solid #00c4cc; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 نظام تحليل محفظة العقود والماليات (2026)")
st.caption("تحليل تلقائي دقيق للمبالغ المالية (Formal AR, Formal Principal, Formal Interest) وتوزيع الحالة")
st.markdown("---")

# ---------------------------------------------------------
# 2. القائمة الجانبية لرفع شيت الإكسيل
# ---------------------------------------------------------
st.sidebar.header("📁 رفع بيانات الإكسيل")
uploaded_file = st.sidebar.file_uploader(
    "قم برفع ملف Excel (.xlsx)", 
    type=["xlsx", "xls"]
)

# ---------------------------------------------------------
# 3. معالجة وتوليد التقرير المباشر
# ---------------------------------------------------------
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success(f"تم تحميل الملف بنجاح: {uploaded_file.name}")
        
        # --- أ) اكتشاف الأعمدة الرئيسية تلقائياً ---
        status_col = None
        credit_col = None
        ar_col = None
        principal_col = None
        interest_col = None
        
        for col in df.columns:
            c_str = str(col).lower()
            if "حاله" in c_str or "الحاله" in str(col):
                status_col = col
            elif "creditamount" in c_str or "مبلغ" in str(col):
                credit_col = col
            elif "formal ar" in c_str or "ar" in c_str:
                ar_col = col
            elif "formal principal" in c_str or "princ" in c_str:
                principal_col = col
            elif "formal interest" in c_str or "interest" in c_str:
                interest_col = col

        # التعيين الإفتراضي في حال تباين أسماء الأعمدة
        if not status_col:
            status_col = "الحاله" if "الحاله" in df.columns else df.columns[2]
        if not ar_col:
            ar_col = "AR" if "AR" in df.columns else (df.columns[7] if len(df.columns) > 7 else df.columns[-1])
        if not principal_col:
            principal_col = "totalprinc_asoff" if "totalprinc_asoff" in df.columns else df.columns[8]
        if not interest_col:
            interest_col = "totalinterest_asoff" if "totalinterest_asoff" in df.columns else df.columns[9]
            
        # --- ب) حساب قيم المؤشرات الكلية (KPIs) ---
        total_records = len(df)
        sum_ar = df[ar_col].sum() if ar_col in df.columns else 0
        sum_principal = df[principal_col].sum() if principal_col in df.columns else 0
        sum_interest = df[interest_col].sum() if interest_col in df.columns else 0

        # --- ج) عرض كروت المؤشرات الكلية المعدلة ---
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            st.markdown(f'''
                <div class="kpi-card">
                    <div class="kpi-title">إجمالي عدد السجلات / العقود</div>
                    <div class="kpi-value">{total_records:,}</div>
                    <div class="kpi-sub">عقد مسجل</div>
                </div>
            ''', unsafe_allow_html=True)
            
        with c2:
            st.markdown(f'''
                <div class="kpi-card">
                    <div class="kpi-title">إجمالي (Formal AR)</div>
                    <div class="kpi-value">{sum_ar:,.2f}</div>
                    <div class="kpi-sub">ج.م (القيمة المستحقة)</div>
                </div>
            ''', unsafe_allow_html=True)

        with c3:
            st.markdown(f'''
                <div class="kpi-card">
                    <div class="kpi-title">إجمالي (Formal Principal)</div>
                    <div class="kpi-value">{sum_principal:,.2f}</div>
                    <div class="kpi-sub">ج.م (أصل الدين)</div>
                </div>
            ''', unsafe_allow_html=True)

        with c4:
            st.markdown(f'''
                <div class="kpi-card">
                    <div class="kpi-title">إجمالي (Formal Interest)</div>
                    <div class="kpi-value">{sum_interest:,.2f}</div>
                    <div class="kpi-sub">ج.م (إجمالي الفوائد)</div>
                </div>
            ''', unsafe_allow_html=True)

        st.write("")

        # --- د) الرسم البياني المخصص لعمود "الحاله" ---
        st.markdown(f'<div class="card-header">📈 توزيع المبالغ بحسب ({status_col})</div>', unsafe_allow_html=True)
        
        # تجميع البيانات حسب الحالة
        metric_for_chart = credit_col if credit_col in df.columns else ar_col
        df_grouped = df.groupby(status_col, as_index=False)[metric_for_chart].sum()

        fig = px.bar(
            df_grouped, 
            x=status_col, 
            y=metric_for_chart,
            text_auto='.3s',
            title=f"توزيع إجمالي {metric_for_chart} بحسب {status_col}",
            color_discrete_sequence=['#00c4cc']
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color='#ffffff',
            xaxis_title=str(status_col),
            yaxis_title=str(metric_for_chart),
            xaxis={'categoryorder': 'total descending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # --- هـ) عرض جدول البيانات التفصيلي ---
        st.markdown('<div class="card-header">📋 جدول التفاصيل الكامل للبيانات</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")

else:
    # --- 4. العرض الافتراضي في حالة عدم رفع ملف ---
    st.info("💡 قم برفع ملف الإكسيل لعرض تحليل Formal AR و Formal Principal و Formal Interest ومخطط الحالة تلقائياً.")
    
    df_demo = pd.DataFrame({
        'الحاله': ['كارت امان', 'كارت اسلامي', 'نورمال اسلامي', 'زيادة الحد الائتماني', 'نورمال', 'B2E'],
        'CreditAmount': [123892778, 542027243, 470097341, 20425350, 40772122, 4862150],
        'AR': [89165737, 477430445, 752773409, 12171344, 34844098, 3549054],
        'totalprinc_asoff': [65736465, 350502583, 448755291, 9727388, 21804801, 2763485],
        'totalinterest_asoff': [23429272, 126927862, 304018118, 2443956, 13039298, 785569]
    })

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">عدد العقود</div><div class="kpi-value">20,578</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Formal AR</div><div class="kpi-value">{df_demo["AR"].sum():,.2f} ج.م</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Formal Principal</div><div class="kpi-value">{df_demo["totalprinc_asoff"].sum():,.2f} ج.م</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Formal Interest</div><div class="kpi-value">{df_demo["totalinterest_asoff"].sum():,.2f} ج.م</div></div>', unsafe_allow_html=True)

    st.write("")
    fig = px.bar(df_demo, x='الحاله', y='CreditAmount', text_auto='.3s', title="توزيع CreditAmount بحسب الحالة (عرض افتراضي)", color_discrete_sequence=['#00c4cc'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
    st.plotly_chart(fig, use_container_width=True)
