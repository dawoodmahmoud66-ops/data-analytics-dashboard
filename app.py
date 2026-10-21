import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="تحليل التخصيم والتوريق - 2026",
    page_icon="📊",
    layout="wide"
)

# تنسيق المظهر الداكن والأنيق
st.markdown("""
    <style>
    .stApp { background-color: #071e33; color: #ffffff; direction: rtl; text-align: right; }
    .kpi-card { background-color: #0b2847; border-radius: 12px; padding: 20px; border-right: 5px solid #00c4cc; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .kpi-title { color: #90caf9; font-size: 14px; font-weight: bold; }
    .kpi-value { color: #00c4cc; font-size: 24px; font-weight: bold; margin-top: 5px; }
    .card-header { background-color: #0b2847; color: #ffffff; padding: 10px 15px; font-weight: bold; font-size: 16px; border-radius: 6px; margin-bottom: 15px; border-right: 3px solid #00c4cc; }
    </style>
""", unsafe_allow_html=True)

st.title("Analysis)")
st.markdown("---")

# 1. تجهيز البيانات من الشيتات الثلاثة
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

# 2. أرقام المؤشرات الرئيسية
tot_count = df_card_normal['Total Count'].sum() + df_auto['Total Count'].sum() + df_sec['Total Count'].sum()
tot_val = df_card_normal['Total Formal AR'].sum() + df_auto['Total Formal AR'].sum() + df_sec['Total Sum of AR'].sum()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي عدد الملفات والعقود</div><div class="kpi-value">{tot_count:,} ملف</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي المحفظة المالية</div><div class="kpi-value">{tot_val:,.2f} ج.م</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">عدد البنوك والمؤسسات المشاركة</div><div class="kpi-value">8 بنوك</div></div>', unsafe_allow_html=True)

st.write("")

# 3. التبويبات حسب الشيتات
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
