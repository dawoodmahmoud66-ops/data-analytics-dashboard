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

st.title("📊 لوحة تحكم إدارة مرجعة المستندات والتوريق - 2026")

# ---------------------------------------------------------
# رفع الملف من القائمة الجانبية
# ---------------------------------------------------------
st.sidebar.header("📁 رفع بيانات جديدة")
uploaded_file = st.sidebar.file_uploader("قم برفع ملف Excel أو CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df_scan = pd.read_csv(uploaded_file)
        else:
            df_scan = pd.read_excel(uploaded_file)
            
        # إزالة الفراغات الزائدة من أسماء الأعمدة
        df_scan.columns = df_scan.columns.astype(str).str.strip()
        st.sidebar.success("تم تحميل الملف بنجاح!")
    except Exception as e:
        st.sidebar.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        df_scan = None
else:
    # البيانات الافتراضية
    df_scan = pd.DataFrame({
        'نوع الملف': ['كارت الحد الائتماني (كارت جديد)', 'عقود زيادة الحد الائتماني', 'عقود الطلب العادي (نورمال)', 'عقود السيارات'],
        'العدد': [70225, 24448, 8156, 1647]
    })

if df_scan is not None:
    # قائمة الأعمدة لاختيار العمود الخاص بالأرقام والعمود الخاص بالأنواع
    columns = list(df_scan.columns)
    
    # محاولة التحديد التلقائي
    default_num_col = 'العدد' if 'العدد' in columns else columns[-1]
    default_text_col = 'نوع الملف' if 'نوع الملف' in columns else columns[0]
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ إعدادات الأعمدة")
    col_text = st.sidebar.selectbox("اختر عمود (نوع الملف/البيان):", columns, index=columns.index(default_text_col) if default_text_col in columns else 0)
    col_num = st.sidebar.selectbox("اختر عمود (العدد/القيمة الرقمية):", columns, index=columns.index(default_num_col) if default_num_col in columns else 0)

    # تحويل البيانات إلى أرقام لتفادي الأخطاء
    df_scan[col_num] = pd.to_numeric(df_scan[col_num], errors='coerce').fillna(0)
    total_scanned = int(df_scan[col_num].sum())

    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">إجمالي العدد / القيمة ({col_num})</div>
            <div class="kpi-value">{total_scanned:,}</div>
        </div>
    """, unsafe_allow_html=True)

    st.write("")

    c1, c2 = st.columns([1.2, 1])

    with c1:
        fig_scan = px.bar(
            df_scan, x=col_num, y=col_text, orientation='h',
            text_auto=',d', title=f"توزيع البيانات حسب {col_text}",
            color_discrete_sequence=['#00c4cc']
        )
        fig_scan.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
        st.plotly_chart(fig_scan, use_container_width=True)

    with c2:
        st.subheader("📋 جدول البيانات الحالي")
        st.dataframe(df_scan, use_container_width=True, hide_index=True)
