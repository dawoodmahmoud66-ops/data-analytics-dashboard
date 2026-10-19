import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="لوحة تحكم إحصائيات 2026", page_icon="📊", layout="wide")

# CSS للتنسيق الداكن
st.markdown("""
    <style>
    .stApp { background-color: #071e33; color: #ffffff; direction: rtl; text-align: right; }
    .kpi-card { background-color: #0b2847; border-radius: 12px; padding: 20px; border-right: 5px solid #00c4cc; }
    .kpi-title { color: #90caf9; font-size: 14px; font-weight: bold; }
    .kpi-value { color: #00c4cc; font-size: 24px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# رفع الملف من القائمة الجانبية
# ---------------------------------------------------------
st.sidebar.header("📁 رفع بيانات جديدة")
uploaded_file = st.sidebar.file_uploader("قم برفع ملف Excel أو CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    # قراءة الملف المرفوع
    if uploaded_file.name.endswith('.csv'):
        df_scan = pd.read_csv(uploaded_file)
    else:
        # قراءة أول شيت أو شيت معينة
        df_scan = pd.read_excel(uploaded_file)
    st.sidebar.success("تم تحميل الملف بنجاح!")
else:
    # البيانات الافتراضية في حال عدم رفع ملف
    df_scan = pd.DataFrame({
        'نوع الملف': ['كارت الحد الائتماني (كارت جديد)', 'عقود زيادة الحد الائتماني', 'عقود الطلب العادي (نورمال)', 'عقود السيارات'],
        'العدد': [70225, 24448, 8156, 1647]
    })

# ---------------------------------------------------------
# عرض البيانات والرسوم البيانية
# ---------------------------------------------------------
st.title("📊 لوحة تحكم إدارة مرجعة المستندات والتوريق - 2026")

total_scanned = df_scan['العدد'].sum()

st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">إجمالي الملفات الممسوحة ضوئياً</div>
        <div class="kpi-value">{total_scanned:,} ملف</div>
    </div>
""", unsafe_allow_html=True)

st.write("")

c1, c2 = st.columns([1.2, 1])

with c1:
    fig_scan = px.bar(
        df_scan, x='العدد', y='نوع الملف', orientation='h',
        text_auto=',d', title="توزيع ملفات المسح الضوئي",
        color_discrete_sequence=['#00c4cc']
    )
    fig_scan.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
    st.plotly_chart(fig_scan, use_container_width=True)

with c2:
    st.subheader("📋 جدول البيانات الحالي")
    st.dataframe(df_scan, use_container_width=True, hide_index=True)
