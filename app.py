import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم الفاخر (Aman Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="منصة AMAN - المحلل الذكي الشامل (AI Powered)",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    
    .stApp { background-color: #F0FAFA; color: #0A3D3A; direction: rtl; text-align: right; }
    
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
        font-weight: 900; font-size: 26px;
        background: rgba(255, 255, 255, 0.2);
        padding: 6px 18px; border-radius: 12px;
    }
    .kpi-card-custom {
        background: #ffffff; border-radius: 12px; padding: 16px;
        text-align: center; border-top: 4px solid #00B9C3;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 10px;
    }
    .kpi-card-custom .val { font-size: 20px; font-weight: 900; color: #008C96; }
    .kpi-card-custom .lbl { font-size: 12px; color: #5A7A7A; font-weight: 700; margin-top: 4px; }
    
    .section-title {
        font-size: 16px; font-weight: 800; color: #008C96; margin-bottom: 12px;
        background: #ffffff; padding: 10px 16px; border-radius: 10px;
        border-right: 4px solid #00B9C3; box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .ai-box {
        background: #ffffff; border-radius: 12px; padding: 18px;
        border: 2px solid #00B9C3; box-shadow: 0 4px 12px rgba(0,185,195,0.15);
        line-height: 1.8; color: #0A3D3A; margin-bottom: 20px;
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
            <div style="font-weight:800; font-size:20px">المحلل التلقائي والذكاء الاصطناعي الشامل</div>
            <div style="font-size:13px; opacity:.9">تحليل كافة الشيتات واستخراج الملخصات المالية والتوصيات الذكية</div>
        </div>
        <div style="font-size:12px; opacity:.9">© أمان للخدمات المالية</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. القائمة الجانبية وربط الـ API Key
# ---------------------------------------------------------
st.sidebar.header("🔑 مفتاح الذكاء الاصطناعي (Gemini)")

DEFAULT_API_KEY = "AQ.Ab8RN6L_9ONwW0-Tj4WyPEovCjGmqyOkOlIXLzLRNZFLQAJ6EQ"

api_key = st.sidebar.text_input("أدخل Gemini API Key:", value=DEFAULT_API_KEY, type="password")

if api_key:
    genai.configure(api_key=api_key)

st.sidebar.header("📁 رفع ملف الإكسيل")
uploaded_file = st.sidebar.file_uploader("اختر أي ملف Excel (.xlsx, .xls)", type=["xlsx", "xls"])

# ---------------------------------------------------------
# 4. معالجة وتوليد التحليل المالي والـ AI
# ---------------------------------------------------------
if uploaded_file is not None:
    try:
        xls = pd.ExcelFile(uploaded_file)
        selected_sheet = st.sidebar.selectbox("اختر الشيت المراد تحليله:", xls.sheet_names)
        
        df_raw = pd.read_excel(xls, sheet_name=selected_sheet)
        
        header_row = 0
        for idx in range(min(15, len(df_raw))):
            row_str = " ".join(df_raw.iloc[idx].dropna().astype(str).values)
            if any(k in row_str.lower() for k in ["row labels", "حاله", "الحاله", "count", "ar", "credit", "date"]):
                header_row = idx
                break
                
        df = pd.read_excel(xls, sheet_name=selected_sheet, header=header_row).dropna(how='all')
        
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # أ) الكروت الرقمية
        st.markdown(f'<div class="section-title">📊 الملخص الرقمي الرئيسي ({selected_sheet})</div>', unsafe_allow_html=True)
        kpi_cols = st.columns(min(4, max(1, len(num_cols) + 1)))
        
        with kpi_cols[0]:
            st.markdown(f'<div class="kpi-card-custom"><div class="val">{len(df):,}</div><div class="lbl">إجمالي عدد السجلات/العقود</div></div>', unsafe_allow_html=True)

        for i, col_name in enumerate(num_cols[:3]):
            col_sum = df[col_name].sum()
            with kpi_cols[i + 1]:
                st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#10B981"><div class="val">{col_sum:,.2f}</div><div class="lbl">مجموع ({col_name})</div></div>', unsafe_allow_html=True)

        st.write("")

        # ب) التحليل التنفيذي بواسطة الذكاء الاصطناعي (Gemini AI)
        st.markdown('<div class="section-title">🤖 التقرير والتحليل التنفيذي الذكي (AI Analysis)</div>', unsafe_allow_html=True)
        
        if api_key:
            if st.button("✨ توليد التقرير المالي بالذكاء الاصطناعي"):
                with st.spinner("جاري قراءة وتحليل بيانات الشيت بـ Gemini AI..."):
                    summary_stats = df.describe().to_string()
                    data_sample = df.head(10).to_string()
                    
                    prompt = f"""
                    أنت خبير ومحلل ماليات وتوريق في شركة أمان. قمت بقراءة ملف إكسيل يحتوي على البيانات التالية:
                    
                    عينة من الصفوف الأولى:
                    {data_sample}
                    
                    الإحصائيات المجمعة للأرقام:
                    {summary_stats}
                    
                    المطلوب:
                    1. قدم ملخصاً تنفذياً شاملاً ومختصراً بأسلوب احترافي لأهم أرقام ومؤشرات المحفظة.
                    2. حدد أين تتركز المبالغ الكبرى والأهمية المالية أو أي ملحوظات استثنائية.
                    3. ضع 3 توصيات مالية وقرارات سريعة لإدارة التوريق والمالية.
                    اكتب بأسلوب عربي أنيق وبنقاط واضحة.
                    """
                    
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    
                    st.markdown(f'<div class="ai-box">{response.text}</div>', unsafe_allow_html=True)
        else:
            st.warning("🔑 يرجى إلصاق مفتاح Gemini API Key في الشريط الجانبي لتفعيل محرك الـ AI.")

        # ج) الرسوم البيانية والتجميع الفوري
        st.markdown('<div class="section-title">⚙️ التجميع والرسوم البيانية المخصصة لجميع الأعمدة</div>', unsafe_allow_html=True)
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1: group_by_col = st.selectbox("اختر عمود التجميع (X-Axis):", text_cols if text_cols else df.columns.tolist())
        with c_sel2: val_col = st.selectbox("اختر العمود المالي (Y-Axis):", num_cols if num_cols else df.columns.tolist())

        df_grouped = df.groupby(group_by_col, as_index=False)[val_col].sum().sort_values(by=val_col, ascending=False)

        g1, g2 = st.columns(2)
        with g1:
            fig_bar = px.bar(df_grouped.head(15), x=group_by_col, y=val_col, text_auto='.3s', title=f"مجموع {val_col} بحسب {group_by_col}", color_discrete_sequence=['#00B9C3'])
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
            st.plotly_chart(fig_bar, use_container_width=True)

        with g2:
            fig_pie = px.pie(df_grouped.head(10), names=group_by_col, values=val_col, title=f"نسب التوزيع بحسب {group_by_col}", color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
            st.plotly_chart(fig_pie, use_container_width=True)

        # د) عرض الجداول
        st.markdown(f'<div class="section-title">📋 تفنيد البيانات المجمعة بحسب ({group_by_col})</div>', unsafe_allow_html=True)
        st.dataframe(df_grouped, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحليل الشيت: {e}")

else:
    st.info("👈 قم برفع أي ملف إكسيل من الشريط الجانبي للبدء في تحليله بالذكاء الاصطناعي.")
