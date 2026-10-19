import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم (Power BI Dark Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="لوحة تحكم إحصائيات 2026",
    page_icon="📊",
    layout="wide"
)

# تطبيق CSS مخصص للتصميم الداكن واللغة العربية
st.markdown("""
    <style>
    /* خلفية الصفحة الأساسية */
    .stApp {
        background-color: #071e33;
        color: #ffffff;
        direction: rtl;
        text-align: right;
    }
    
    /* بطاقات المؤشرات (KPI Cards) */
    .kpi-card {
        background-color: #0b2847;
        border-radius: 12px;
        padding: 20px;
        border-right: 5px solid #00c4cc;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    .kpi-title {
        color: #90caf9;
        font-size: 14px;
        font-weight: bold;
    }
    .kpi-value {
        color: #00c4cc;
        font-size: 26px;
        font-weight: bold;
        margin-top: 5px;
    }

    /* تحسين إطارات الجداول والرسوم */
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. تجهيز البيانات (Data Processing)
# ---------------------------------------------------------

# أ. بيانات المسح الضوئي (Scanning)
df_scan = pd.DataFrame({
    'نوع الملف': ['كارت الحد الائتماني (كارت جديد)', 'عقود زيادة الحد الائتماني', 'عقود الطلب العادي (نورمال)', 'عقود السيارات'],
    'العدد': [70225, 24448, 8156, 1647]
})

# ب. بيانات العقود وسندات الضمان
df_contracts = pd.DataFrame({
    'نوع العقد': ['كارت الحد الإئتماني', 'زيادة الحد الائتماني', 'الطلب العادي', 'عقود السيارات', 'الشيكات (تحصيل + ضمان)'],
    'العدد': [91822, 52697, 19698, 1647, 1545],
    'المبلغ الإجمالي (جنيه)': [3818870346, 0, 0, 2156218389, 2101064331]
})

# جـ. بيانات التوريق والتخصيم
df_securitization = pd.DataFrame({
    'النوع': ['توريق (10 عمليات)', 'توريق (جاري العمل)', 'تخصيم شيكات (10 عمليات)'],
    'البنوك': ['مصر - التنمية الصناعية - ايجي بنك - العربي الافريقي', 'EGBank', 'ايجي بنك - CIB - الاهلي الكويتي - تنمية الصادرات - التنمية الصناعية - العربي الافريقي - بنك نكست'],
    'العدد': [156963, 20577, 877],
    'القيمة التوريقية (جنيه)': [4928042967, 1373612243, 1036640462]
})

# ---------------------------------------------------------
# 3. العرض الرئيسي (Header & KPI Cards)
# ---------------------------------------------------------
st.title("📊 لوحة تحكم إدارة مرجعة المستندات والتوريق - 2026")
st.markdown("---")

# حساب أرقام KPI الرئيسية
total_scanned = df_scan['العدد'].sum()
total_contracts_val = df_contracts['المبلغ الإجمالي (جنيه)'].sum()
total_securitization_val = df_securitization['القيمة التوريقية (جنيه)'].sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي الملفات الممسوحة ضوئياً</div>
            <div class="kpi-value">{total_scanned:,} ملف</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي قيمة العقود والضمانات</div>
            <div class="kpi-value">{total_contracts_val:,.0f} ج.م</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي محفظة التوريق والتخصيم</div>
            <div class="kpi-value">{total_securitization_val:,.0f} ج.م</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# 4. الرسوم البيانية التفاعلية (Power BI Style Charts)
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["📂 المسح الضوئي (Scanning)", "📑 العقود والضمانات", "🏦 التوريق والتخصيم"])

# --- التبوب الأول: المسح الضوئي ---
with tab1:
    c1, c2 = st.columns([1.2, 1])
    
    with c1:
        # رسم بياني شريطي بألوان السيان
        fig_scan = px.bar(
            df_scan, x='العدد', y='نوع الملف', orientation='h',
            text_auto=',d', title="توزيع ملفات المسح الضوئي حسب النوع",
            color_discrete_sequence=['#00c4cc']
        )
        fig_scan.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff', title_x=1, yaxis={'categoryorder':'total ascending'}
        )
        st.plotly_chart(fig_scan, use_container_width=True)
        
    with c2:
        st.subheader("📋 جدول بيانات المسح الضوئي")
        st.dataframe(df_scan, use_container_width=True, hide_index=True)

# --- التبويب الثاني: العقود وسندات الضمان ---
with tab2:
    c1, c2 = st.columns(2)
    
    with c1:
        # رسم دائري لتوزيع أعداد العقود
        fig_pie = px.pie(
            df_contracts, names='نوع العقد', values='العدد',
            title="نسب أعداد العقود وسندات الضمان",
            hole=0.4, color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', title_x=1)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        # رسم بياني للقيمة المالية
        df_val = df_contracts[df_contracts['المبلغ الإجمالي (جنيه)'] > 0]
        fig_val = px.bar(
            df_val, x='نوع العقد', y='المبلغ الإجمالي (جنيه)',
            text_auto='.3s', title="القيمة المالية للعقود (جنيه مصري)",
            color_discrete_sequence=['#00838f']
        )
        fig_val.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', title_x=1)
        st.plotly_chart(fig_val, use_container_width=True)

# --- التبويب الثالث: التوريق والتخصيم ---
with tab3:
    st.subheader("🏦 ميزانية عمليات التوريق والتخصيم بالبنوك")
    
    fig_sec = px.bar(
        df_securitization, x='النوع', y='القيمة التوريقية (جنيه)',
        color='النوع', text_auto='.3s',
        title="مقارنة القيم التوريقية والتخصيم",
        color_discrete_sequence=['#00c4cc', '#0288d1', '#26c6da']
    )
    fig_sec.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff', title_x=1)
    st.plotly_chart(fig_sec, use_container_width=True)
    
    st.markdown("### التفاصيل والمؤسسات المشاركة")
    st.dataframe(df_securitization, use_container_width=True, hide_index=True)
