import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="لوحة تحكم إحصائيات 2026 - التحديث الجديد",
    page_icon="📊",
    layout="wide"
)

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
        padding: 18px;
        border-right: 5px solid #00c4cc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .kpi-title {
        color: #6c757d;
        font-size: 14px;
        font-weight: bold;
    }
    .kpi-value {
        color: #0b2847;
        font-size: 24px;
        font-weight: bold;
        margin-top: 5px;
    }
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

st.title("📊 لوحة تحكم إحصائيات المستندات والتوريق - 2026")
st.markdown("---")

# 1. إدخال البيانات المحدثة من شيت تحديث.xlsx
df_scan = pd.DataFrame({
    'نوع الملفات': ['كارت الحد الائتمانى ( كارت جديد )', 'عقود زيادة الحد الائتماني', 'عقود الطلب العادى ( نورمال )', 'عقود السيارات'],
    'العدد': [70225, 24448, 8156, 1647]
})

df_contracts = pd.DataFrame({
    'نوع العقد': ['كارت الحد الإئتمانى', 'زيادة الحد الائتماني', 'الطلب العادى', 'عقود السيارات', 'الشيكات ( تحصيل + ضمان )'],
    'العدد': [91822, 52697, 19698, 1647, 1545]
})

df_securitization = pd.DataFrame({
    'ملفات التوريق/التخصيم': ['عدد 10عملية توريق', 'جاري العمل عليها', 'عدد 10 عملية تخصيم ( شيكات)'],
    'البنوك': ['مصر - التنمية الصناعية - ايجي بنك - العربي الافريقي', 'EGBank', 'ايجي بنك-البنك التجاري الدولي-الاهلي الكويتي-تنمية الصادرات-التنمية الصناعية-العربي الافريقي-بنك نكست'],
    'العدد': [156963, 20577, 877],
    'قيمة توريقية (جنيه)': [4928042967.18, 1373612243.12, 1036640461.55]
})

# 2. عرض المؤشرات الرئيسية (KPIs)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي أعداد المسح الضوئي (Scanning)</div>
            <div class="kpi-value">{df_scan['العدد'].sum():,} ملف</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي أعداد العقود وسندات الضمان</div>
            <div class="kpi-value">{df_contracts['العدد'].sum():,} عقد/شيك</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card" style="border-right-color: #212529;">
            <div class="kpi-title">إجمالي قيمة التوريق والتخصيم</div>
            <div class="kpi-value">{df_securitization['قيمة توريقية (جنيه)'].sum():,.0f} ج.م</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")

# 3. عرض الرسوم البيانية التفاعلية
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="card-header">📂 توزيع أعداد ملفات المسح الضوئي</div>', unsafe_allow_html=True)
    fig_scan = px.bar(
        df_scan, x='العدد', y='نوع الملفات', orientation='h',
        text_auto=',d', color_discrete_sequence=['#00c4cc']
    )
    fig_scan.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_scan, use_container_width=True)

with c2:
    st.markdown('<div class="card-header">📑 توزيع أعداد العقود وسندات الضمان</div>', unsafe_allow_html=True)
    fig_contracts = px.pie(
        df_contracts, names='نوع العقد', values='العدد',
        hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_contracts.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_contracts, use_container_width=True)

# 4. جدول التوريق والتخصيم
st.markdown('<div class="card-header">🏦 أعداد ملفات عمليات التوريق المالي والتخصيم والبنوك المشاركة</div>', unsafe_allow_html=True)
st.dataframe(df_securitization, use_container_width=True, hide_index=True)
