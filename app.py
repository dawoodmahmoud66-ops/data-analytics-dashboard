import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# ---------------------------------------------------------
# 1. إعدادات الصفحة الهيكلية والتصميم الأنيق (Theme Aman/Cyan)
# ---------------------------------------------------------
st.set_page_config(
    page_title="داشبورد تحليل محفظة التوريق والتخصيم 2026",
    page_icon="📊",
    layout="wide"
)

# تطبيق ألوان وتنسيقات واجهة AMAN
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
    }
    
    .stApp {
        background-color: #F0FAFA;
        color: #0A3D3A;
        direction: rtl;
        text-align: right;
    }
    
    /* الهيدر العلوي الأنيق */
    .custom-header {
        background: linear-gradient(105deg, #00B9C3, #008C96);
        border-radius: 16px;
        padding: 20px 24px;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 185, 195, 0.2);
    }
    .custom-header .logo {
        font-weight: 900;
        font-size: 24px;
        background: rgba(255, 255, 255, 0.2);
        padding: 6px 18px;
        border-radius: 12px;
    }
    
    /* بطاقات KPI العلوية */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-bottom: 20px;
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
        font-size: 22px;
        font-weight: 900;
        color: #008C96;
    }
    .kpi-card-custom .lbl {
        font-size: 12px;
        color: #5A7A7A;
        font-weight: 700;
        margin-top: 4px;
    }
    
    /* عناوين الأقسام */
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
    
    /* تنسيق الجداول */
    .dataframe {
        border-collapse: collapse !important;
        width: 100% !important;
        font-size: 13px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. الهيدر العلوي المميز
# ---------------------------------------------------------
st.markdown("""
    <div class="custom-header">
        <div class="logo">aman</div>
        <div style="text-align:center">
            <div style="font-weight:800; font-size:20px">الملخص السنوي لمحفظة التوريق 2026</div>
            <div style="font-size:13px; opacity:.9">تحليل شامل ومفصل لمبالغ Formal AR + Principal + Interest بحسب الحالة</div>
        </div>
        <div style="font-size:12px; opacity:.9">داشبورد العرض المالي</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. القائمة الجانبية لرفع الملف
# ---------------------------------------------------------
st.sidebar.header("📁 رفع بيانات الإكسيل")
uploaded_file = st.sidebar.file_uploader(
    "رفع ملف Excel (.xlsx)", 
    type=["xlsx", "xls"]
)

# ---------------------------------------------------------
# 4. دالة معالجة واستخراج البيانات
# ---------------------------------------------------------
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success(f"تم تحميل الملف بنجاح: {uploaded_file.name}")
        
        # التعرف الآلي على الأعمدة
        status_col = None
        ar_col = None
        principal_col = None
        interest_col = None
        credit_col = None
        
        for col in df.columns:
            c_str = str(col).lower()
            if "حاله" in c_str or "الحاله" in str(col):
                status_col = col
            elif "formal ar" in c_str or "ar" in c_str:
                ar_col = col
            elif "formal principal" in c_str or "princ" in c_str:
                principal_col = col
            elif "formal interest" in c_str or "interest" in c_str:
                interest_col = col
            elif "credit" in c_str or "مبلغ" in c_str:
                credit_col = col

        # تعيين الافتراضيات في حالة تغير الأسماء
        if not status_col:
            status_col = "الحاله" if "الحاله" in df.columns else df.columns[2]
        if not ar_col:
            ar_col = "AR" if "AR" in df.columns else (df.columns[7] if len(df.columns) > 7 else df.columns[-1])
        if not principal_col:
            principal_col = "totalprinc_asoff" if "totalprinc_asoff" in df.columns else df.columns[8]
        if not interest_col:
            interest_col = "totalinterest_asoff" if "totalinterest_asoff" in df.columns else df.columns[9]

        # أ) حساب أرقام الـ KPIs العلوية
        total_contracts = len(df)
        sum_ar = df[ar_col].sum() if ar_col in df.columns else 0
        sum_principal = df[principal_col].sum() if principal_col in df.columns else 0
        sum_interest = df[interest_col].sum() if interest_col in df.columns else 0

        # عرض الكروت العلوية الأربعة
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="kpi-card-custom"><div class="val">{total_contracts:,}</div><div class="lbl">إجمالي العقود</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#10B981"><div class="val" style="color:#10B981">{sum_ar:,.2f} ج.م</div><div class="lbl">إجمالي Formal AR</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#00B9C3"><div class="val" style="color:#008C96">{sum_principal:,.2f} ج.م</div><div class="lbl">إجمالي Formal Principal</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#F59E0B"><div class="val" style="color:#F59E0B">{sum_interest:,.2f} ج.م</div><div class="lbl">إجمالي Formal Interest</div></div>', unsafe_allow_html=True)

        st.write("")

        # ب) تجميع البيانات وتفنيدها بحسب "الحاله"
        df_grouped = df.groupby(status_col, as_index=False).agg({
            status_col: 'count',
            ar_col: 'sum',
            principal_col: 'sum',
            interest_col: 'sum'
        }).rename(columns={
            status_col: 'الحالة',
            status_col: 'عدد العقود',
            ar_col: 'Formal AR',
            principal_col: 'Formal Principal',
            interest_col: 'Formal Interest'
        })

        # ج) قسم الرسوم البيانية التفاعلية (Chart.js Style)
        st.markdown('<div class="section-title">📊 الرسوم البيانية التفاعلية للمحفظة</div>', unsafe_allow_html=True)
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_bar = px.bar(
                df_grouped, 
                x='عدد العقود', 
                y='الحالة', 
                orientation='h',
                text_auto=',',
                title="توزيع عدد العقود بحسب الحالة",
                color_discrete_sequence=['#00B9C3']
            )
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            fig_pie = px.pie(
                df_grouped, 
                names='الحالة', 
                values='Formal AR',
                title="نسب المبالغ المستحقة (Formal AR) بحسب الحالة",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4
            )
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
            st.plotly_chart(fig_pie, use_container_width=True)

        # د) الجدول التفصيلي للنتائج التجميعية (Aman Design Table)
        st.markdown('<div class="section-title">📋 تفنيد المحفظة الشامل بحسب (الحالة)</div>', unsafe_allow_html=True)
        
        # إضافة صف الإجمالي العام (Grand Total Row)
        df_display = df_grouped.copy()
        total_row = pd.DataFrame({
            'الحالة': ['الإجمالي العام (Grand Total)'],
            'عدد العقود': [df_display['عدد العقود'].sum()],
            'Formal AR': [df_display['Formal AR'].sum()],
            'Formal Principal': [df_display['Formal Principal'].sum()],
            'Formal Interest': [df_display['Formal Interest'].sum()]
        })
        df_display = pd.concat([df_display, total_row], ignore_index=True)

        st.dataframe(
            df_display.style.format({
                'عدد العقود': '{:,}',
                'Formal AR': '{:,.2f} ج.م',
                'Formal Principal': '{:,.2f} ج.م',
                'Formal Interest': '{:,.2f} ج.م'
            }), 
            use_container_width=True
        )

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحليل البيانات: {e}")

else:
    # --- العرض الافتراضي في حالة عدم رفع ملف ---
    st.info("💡 قم برفع ملف الإكسيل لعرض تفنيد Formal AR و Principal و Interest بحسب الحالة تلقائياً.")
    
    df_demo = pd.DataFrame({
        'الحالة': ['كارت إسلامي', 'نورمال إسلامي', 'كارت أمان', 'زيادة الحد الائتماني', 'نورمال', 'B2E'],
        'عدد العقود': [12372, 4224, 2893, 555, 349, 179],
        'Formal AR': [477430445.0, 752773409.0, 89165737.0, 12171344.0, 34844098.0, 3549054.0],
        'Formal Principal': [350502583.0, 448755291.0, 65736465.0, 9727388.0, 21804801.0, 2763485.0],
        'Formal Interest': [126927862.0, 304018118.0, 23429272.0, 2443956.0, 13039298.0, 785569.0]
    })

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card-custom"><div class="val">{df_demo["عدد العقود"].sum():,}</div><div class="lbl">إجمالي العقود</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#10B981"><div class="val" style="color:#10B981">{df_demo["Formal AR"].sum():,.2f} ج.م</div><div class="lbl">إجمالي Formal AR</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#00B9C3"><div class="val" style="color:#008C96">{df_demo["Formal Principal"].sum():,.2f} ج.م</div><div class="lbl">إجمالي Formal Principal</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#F59E0B"><div class="val" style="color:#F59E0B">{df_demo["Formal Interest"].sum():,.2f} ج.م</div><div class="lbl">إجمالي Formal Interest</div></div>', unsafe_allow_html=True)

    st.write("")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_bar = px.bar(df_demo, x='عدد العقود', y='الحالة', orientation='h', text_auto=',', title="توزيع عدد العقود بحسب الحالة", color_discrete_sequence=['#00B9C3'])
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        fig_pie = px.pie(df_demo, names='الحالة', values='Formal AR', title="نسب المبالغ المستحقة (Formal AR) بحسب الحالة", color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="section-title">📋 تفنيد المحفظة الشامل بحسب (الحالة)</div>', unsafe_allow_html=True)
    st.dataframe(df_demo, use_container_width=True)
