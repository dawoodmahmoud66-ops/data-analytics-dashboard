import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
import io

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم الفاخر المتقدم (Aman Theme)
# ---------------------------------------------------------
st.set_page_config(
    page_title="منصة AMAN - المحلل المالي الذكي والنظام الشامل",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; }
    
    .stApp { background-color: #F0FAFA; color: #0A3D3A; direction: rtl; text-align: right; }
    
    .custom-header {
        background: linear-gradient(110deg, #00B9C3 0%, #008C96 50%, #0A3D3A 100%);
        border-radius: 16px;
        padding: 24px 28px;
        color: #ffffff;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 20px rgba(0, 185, 195, 0.2);
    }
    .custom-header .logo {
        font-weight: 900; font-size: 32px;
        background: rgba(255, 255, 255, 0.2);
        padding: 6px 22px; border-radius: 14px;
        letter-spacing: 1px;
    }
    .kpi-card-custom {
        background: #ffffff; border-radius: 14px; padding: 18px;
        text-align: center; border-top: 5px solid #00B9C3;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-bottom: 12px;
        transition: transform 0.2s ease-in-out;
    }
    .kpi-card-custom:hover { transform: translateY(-3px); }
    .kpi-card-custom .val { font-size: 22px; font-weight: 900; color: #008C96; }
    .kpi-card-custom .lbl { font-size: 13px; color: #5A7A7A; font-weight: 700; margin-top: 4px; }
    
    .section-title {
        font-size: 17px; font-weight: 800; color: #008C96; margin-bottom: 14px;
        background: #ffffff; padding: 12px 18px; border-radius: 12px;
        border-right: 5px solid #00B9C3; box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .ai-box {
        background: #ffffff; border-radius: 14px; padding: 22px;
        border: 2px solid #00B9C3; box-shadow: 0 6px 16px rgba(0,185,195,0.12);
        line-height: 1.9; color: #0A3D3A; margin-bottom: 25px; font-size: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. الهيدر التفاعلي العلوي
# ---------------------------------------------------------
st.markdown("""
    <div class="custom-header">
        <div class="logo">aman</div>
        <div style="text-align:center">
            <div style="font-weight:900; font-size:22px">نظام التحليل المالي الذكي والتوريق المتقدم</div>
            <div style="font-size:13px; opacity:.95">معالجة شاملة للأعمدة • توليد مؤشرات أداء • محرك شات تفاعلي بالذكاء الاصطناعي</div>
        </div>
        <div style="font-size:12px; opacity:.9">© أمان للخدمات المالية</div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. الشريط الجانبي - الإعدادات والمفتاح
# ---------------------------------------------------------
st.sidebar.header("🔑 إعدادات الذكاء الاصطناعي (Gemini)")

DEFAULT_API_KEY = "AQ.Ab8RN6L_9ONwW0-Tj4WyPEovCjGmqyOkOlIXLzLRNZFLQAJ6EQ"

api_key = st.sidebar.text_input("Gemini API Key:", value=DEFAULT_API_KEY, type="password", help="أدخل مفتاح Gemini لتفعيل الشات والتقارير التلقائية")

if api_key:
    genai.configure(api_key=api_key)

st.sidebar.header("📁 إدارة الملفات والبيانات")
uploaded_file = st.sidebar.file_uploader("رفع ملف إكسيل (.xlsx, .xls)", type=["xlsx", "xls"])

# ---------------------------------------------------------
# 4. محرك المعالجة والتحليل الذكي
# ---------------------------------------------------------
if uploaded_file is not None:
    try:
        xls = pd.ExcelFile(uploaded_file)
        selected_sheet = st.sidebar.selectbox("اختر ورقة العمل (Sheet):", xls.sheet_names)
        
        df_raw = pd.read_excel(xls, sheet_name=selected_sheet)
        
        # اكتشاف ذكي لصف بداية البيانات
        header_row = 0
        for idx in range(min(15, len(df_raw))):
            row_str = " ".join(df_raw.iloc[idx].dropna().astype(str).values)
            if any(k in row_str.lower() for k in ["row labels", "حاله", "الحاله", "count", "ar", "credit", "date"]):
                header_row = idx
                break
                
        df = pd.read_excel(xls, sheet_name=selected_sheet, header=header_row).dropna(how='all')
        
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # أ) المؤشرات المالية الكلية (KPIs Dashboard)
        st.markdown(f'<div class="section-title">📊 الملخص التنفيذي ومؤشرات الأداء الرئيسية ({selected_sheet})</div>', unsafe_allow_html=True)
        
        kpi_cols = st.columns(min(4, max(1, len(num_cols) + 1)))
        
        with kpi_cols[0]:
            st.markdown(f'<div class="kpi-card-custom"><div class="val">{len(df):,}</div><div class="lbl">إجمالي عدد السجلات/العقود</div></div>', unsafe_allow_html=True)

        for i, col_name in enumerate(num_cols[:3]):
            col_sum = df[col_name].sum()
            with kpi_cols[i + 1]:
                st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#10B981"><div class="val">{col_sum:,.2f}</div><div class="lbl">مجموع ({col_name})</div></div>', unsafe_allow_html=True)

        st.write("")

        # ب) محرك التقرير التلقائي بالذكاء الاصطناعي (AI Analysis Engine)
        st.markdown('<div class="section-title">🤖 التقرير المالي المباشر بالذكاء الاصطناعي (AI Executive Summary)</div>', unsafe_allow_html=True)
        
        if api_key:
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                gen_btn = st.button("✨ توليد التقرير المالي", use_container_width=True)
            
            if gen_btn:
                with st.spinner("جاري تحليل الهيكل المالي ومؤشرات المحفظة بـ Gemini AI..."):
                    summary_stats = df.describe().to_string()
                    data_sample = df.head(10).to_string()
                    
                    prompt = f"""
                    أنت خبير ومحلل ماليات وتوريق أول في شركة أمان. قمت بقراءة وتدقيق ملف إكسيل ماليات بالبيانات التالية:
                    
                    عينة البيانات الأولى:
                    {data_sample}
                    
                    المؤشرات الإحصائية المجمعة:
                    {summary_stats}
                    
                    المطلوب تقديم تقرير تنفيذي متكامل يشمل:
                    1. ملخص تنفيذي رفيع المستوى لأهم الأرقام والنتائج.
                    2. تحليل أين تتركز المبالغ والمخاطر أو الترسبات المالية.
                    3. أبرز 3 قرارات مالية وتوصيات سريعة للقيادة التنفيذية.
                    اكتب بأسلوب عربي احترافي ومباشر وبنقاط واضحة.
                    """
                    
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt)
                    
                    st.markdown(f'<div class="ai-box">{response.text}</div>', unsafe_allow_html=True)
            
            # ج) ميزة الشات التفاعلي مع ملف الإكسيل (Ask AI about Excel)
            st.markdown('<div class="section-title">💬 اسأل الذكاء الاصطناعي عن أي تفاصيل في الشيت (Chat with Excel)</div>', unsafe_allow_html=True)
            user_query = st.text_input("أدخل سؤالك المالي حول بيانات الملف (مثال: ما هو أكبر بنك؟ أو ما إجمالي المستحقات؟):")
            
            if user_query:
                with st.spinner("جاري استخراج الإجابة من البيانات..."):
                    chat_prompt = f"""
                    بناءً على ملف البيانات المرفق أدناه:
                    {df.head(20).to_string()}
                    الإحصائيات:
                    {df.describe().to_string()}
                    
                    أجب بدقة وبشكل مختصر ومباشر باللغة العربية على السؤال التالي:
                    {user_query}
                    """
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    chat_res = model.generate_content(chat_prompt)
                    st.info(f"💡 **الإجابة:** {chat_res.text}")
        else:
            st.warning("🔑 يرجى وضع مفتاح Gemini API Key في الشريط الجانبي لتفعيل محرك التقرير التلقائي والشات الذكي.")

        # د) أدوات التحكم والتجميع الفوري والرسوم البيانية المتقدمة
        st.markdown('<div class="section-title">⚙️ التجميع الفوري والرسوم البيانية التفاعلية</div>', unsafe_allow_html=True)
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1: group_by_col = st.selectbox("اختر عمود التجميع (X-Axis):", text_cols if text_cols else df.columns.tolist())
        with c_sel2: val_col = st.selectbox("اختر العمود المالي/الرقمي (Y-Axis):", num_cols if num_cols else df.columns.tolist())

        df_grouped = df.groupby(group_by_col, as_index=False)[val_col].sum().sort_values(by=val_col, ascending=False)

        g1, g2 = st.columns(2)
        with g1:
            fig_bar = px.bar(df_grouped.head(15), x=group_by_col, y=val_col, text_auto='.3s', title=f"توزيع مجموع ({val_col}) بحسب ({group_by_col})", color_discrete_sequence=['#00B9C3'])
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
            st.plotly_chart(fig_bar, use_container_width=True)

        with g2:
            fig_pie = px.pie(df_grouped.head(10), names=group_by_col, values=val_col, title=f"نسبة التوزيع بحسب ({group_by_col})", color_discrete_sequence=px.colors.qualitative.Set3, hole=0.4)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#0A3D3A')
            st.plotly_chart(fig_pie, use_container_width=True)

        # هـ) عرض وتصدير الجداول التجميعية
        st.markdown(f'<div class="section-title">📋 الجدول التجميعي المفلتر ({group_by_col})</div>', unsafe_allow_html=True)
        st.dataframe(df_grouped, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحليل الشيت: {e}")

else:
    st.info("👈 قم برفع أي ملف إكسيل من الشريط الجانبي لبدء التحليل التلقائي والشات الذكي.")
