import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="تحليل بيانات التوريق والمسح الضوئي 2026",
    page_icon="📈",
    layout="wide"
)

# تطبيق CSS للتنسيق
st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
        direction: rtl;
        text-align: right;
    }
    .kpi-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        border-right: 5px solid #e63946;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .kpi-title {
        color: #6c757d;
        font-size: 14px;
        font-weight: bold;
    }
    .kpi-value {
        color: #212529;
        font-size: 22px;
        font-weight: bold;
        margin-top: 5px;
    }
    .card-header {
        background-color: #212529;
        color: #ffffff;
        padding: 8px 15px;
        font-weight: bold;
        font-size: 16px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 لوحة تحليل بيانات إدارة مرجعة المستندات والتوريق - 2026")
st.markdown("---")

# 2. تجهيز البيانات القادمة من شيت 2026.xlsx
df_scan = pd.DataFrame({
    'نوع الملفات': ['عقود الطلب العادى ( نورمال )', 'كارت الحد الائتمانى ( كارت جديد )', 'عقود زيادة الحد الائتماني', 'عقود السيارات'],
    'العدد': [8156, 70225, 24448, 1647]
})

df_contracts = pd.DataFrame({
    'نوع العقد': ['كارت الحد الإئتمانى', 'زيادة الحد الائتماني', 'الطلب العادى', 'عقود السيارات', 'الشيكات ( تحصيل + ضمان )'],
    'العدد': [91822, 52697, 19698, 1647, 1545],
    'TotalAmount': [3818870346.13, 0, 0, 2156218389.00, 2101064331.00]
})

df_securitization = pd.DataFrame({
    'ملفات التوريق/التخصيم': ['عدد 10عملية توريق', 'جاري العمل عليها (توريق)', 'عدد 10 عملية تخصيم'],
    'البنوك': ['مصر - التنمية الصناعية - ايجي بنك - العربي الافريقي', 'EGBank', 'ايجي بنك - CIB - الاهلي الكويتي - تنمية الصادرات - التنمية الصناعية - العربي الافريقي - بنك نكست'],
    'العدد': [156963, 20577, 877],
    'قيمة توريقية': [4928042967.18, 1373612243.12, 1036640461.55]
})

# 3. عرض بطاقات المؤشرات (KPI Cards)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي المسح الضوئي</div>
            <div class="kpi-value">{df_scan['العدد'].sum():,} ملف</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي العقود والضمانات</div>
            <div class="kpi-value">{df_contracts['TotalAmount'].sum():,.0f} ج.م</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي محفظة التوريق والتخصيم</div>
            <div class="kpi-value">{df_securitization['قيمة توريقية'].sum():,.0f} ج.م</div>
        </div>
    """, unsafe_allow_html=True)

with c4:
    grand_total = df_contracts['TotalAmount'].sum() + df_securitization['قيمة توريقية'].sum()
    st.markdown(f"""
        <div class="kpi-card" style="border-right-color: #212529;">
            <div class="kpi-title">إجمالي المحفظة الكلية</div>
            <div class="kpi-value">{grand_total:,.0f} ج.م</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")

# 4. عرض الرسوم البيانية التفاعلية
col_left, col_right = st.columns([1.2, 1])

with col_left:
    st.markdown('<div class="card-header">📊 توزيع ملفات المسح الضوئي (Scanning)</div>', unsafe_allow_html=True)
    fig_scan = px.bar(
        df_scan, y='نوع الملفات', x='العدد', orientation='h',
        text_auto=',d', color_discrete_sequence=['#e63946']
    )
    fig_scan.update_layout(height=350, margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scan, use_container_width=True)

with col_right:
    st.markdown('<div class="card-header">💰 القيمة المالية للعقود والضمانات</div>', unsafe_allow_html=True)
    df_contracts_val = df_contracts[df_contracts['TotalAmount'] > 0]
    fig_val = px.bar(
        df_contracts_val, x='نوع العقد', y='TotalAmount',
        text_auto='.3s', color_discrete_sequence=['#212529']
    )
    fig_val.update_layout(height=350, margin=dict(l=20, r=20, t=10, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_val, use_container_width=True)

# 5. جدول عمليات التوريق
st.markdown('<div class="card-header">🏦 تفاصيل عمليات التوريق المالي والتخصيم بحسب البنوك</div>', unsafe_allow_html=True)
st.dataframe(df_securitization, use_container_width=True, hide_index=True)
