import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google import genai
import io
import os

# مكتبات تصدير المستندات
from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt

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

secret_key = st.secrets.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input("Gemini API Key:", value=secret_key, type="password", help="يتم القراءة تلقائيًا من Streamlit Secrets إذا تم ضبطها")

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.sidebar.error(f"خطأ في تهيئة المفتاح: {e}")

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
        
        header_row = 0
        for idx in range(min(15, len(df_raw))):
            row_str = " ".join(df_raw.iloc[idx].dropna().astype(str).values)
            if any(k in row_str.lower() for k in ["row labels", "حاله", "الحاله", "count", "ar", "credit", "date"]):
                header_row = idx
                break
                
        df = pd.read_excel(xls, sheet_name=selected_sheet, header=header_row).dropna(how='all')
        
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        text_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        # تخصيص مؤشرات الأداء (KPIs)
        st.sidebar.header("📊 تخصيص مؤشرات الأداء (KPIs)")
        selected_kpi_cols = st.sidebar.multiselect(
            "اختر الأعمدة الماليّة للـ KPI:",
            options=num_cols,
            default=num_cols[:3] if num_cols else []
        )

        # أ) المؤشرات المالية الكلية (KPIs Dashboard)
        st.markdown(f'<div class="section-title">📊 الملخص التنفيذي ومؤشرات الأداء الرئيسية ({selected_sheet})</div>', unsafe_allow_html=True)
        
        total_kpis = len(selected_kpi_cols) + 1
        kpi_cols = st.columns(min(4, max(1, total_kpis)))
        
        with kpi_cols[0]:
            st.markdown(f'<div class="kpi-card-custom"><div class="val">{len(df):,}</div><div class="lbl">إجمالي عدد السجلات/العقود</div></div>', unsafe_allow_html=True)

        for i, col_name in enumerate(selected_kpi_cols):
            col_sum = df[col_name].sum()
            col_idx = (i + 1) % len(kpi_cols)
            with kpi_cols[col_idx]:
                st.markdown(f'<div class="kpi-card-custom" style="border-top-color:#10B981"><div class="val">{col_sum:,.2f}</div><div class="lbl">مجموع ({col_name})</div></div>', unsafe_allow_html=True)

        st.write("")

        # ب) محرك التقرير التلقائي بالذكاء الاصطناعي
        st.markdown('<div class="section-title">🤖 التقرير المالي المباشر بالذكاء الاصطناعي (AI Executive Summary)</div>', unsafe_allow_html=True)
        
        if client:
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                gen_btn = st.button("✨ توليد التقرير المالي", use_container_width=True)
            
            if gen_btn:
                summary_stats = df.describe().round(2).to_dict()
                total_rows = len(df)
                cols_names = list(df.columns)
                
                prompt = f"""
                أنت خبير ومحلل ماليات وتوريق في شركة أمان. ألقِ نظرة على الملخص التالي لشيت الإكسيل:
                - إجمالي السجلات: {total_rows}
                - الأعمدة المتاحة: {cols_names}
                - أهم المؤشرات الإحصائية للأرقام: {summary_stats}
                
                قدّم تقريراً تنفيذاً مالياً سريعاً ومختصراً جداً بأسلوب نقاط واضحة:
                1. ملخص تنفيذي سريعة لأهم الأرقام.
                2. تركز المبالغ والمخاطر.
                3. توصيتين ماليتين فوريتين للقيادة.
                """
                
                report_placeholder = st.empty()
                full_response = ""
                
                with st.spinner("جاري الكتابة المباشرة للتقرير..."):
                    response_stream = client.models.generate_content_stream(
                        model="gemini-3.8-flash",
                        contents=prompt
                    )
                    
                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            report_placeholder.markdown(f'<div class="ai-box">{full_response}▌</div>', unsafe_allow_html=True)
                
                report_placeholder.markdown(f'<div class="ai-box">{full_response}</div>', unsafe_allow_html=True)
                st.session_state['latest_report'] = full_response

            # ج) الشات التفاعلي مع الشيت
            st.markdown('<div class="section-title">💬 اسأل الذكاء الاصطناعي عن أي تفاصيل في الشيت (Chat with Excel)</div>', unsafe_allow_html=True)
            user_query = st.text_input("أدخل سؤالك المالي حول بيانات الملف (مثال: ما هو أكبر بنك؟ أو ما إجمالي المستحقات؟):")
            
            if user_query:
                chat_placeholder = st.empty()
                full_chat = ""
                with st.spinner("جاري استخراج الإجابة..."):
                    chat_prompt = f"""
                    بناءً على أول 10 صفوف والإحصائيات التالية للملف:
                    {df.head(10).to_string()}
                    الإحصائيات:
                    {df.describe().round(2).to_string()}
                    
                    أجب بدقة وبإيجاز شديد على هذا السؤال باللغة العربية: {user_query}
                    """
                    chat_stream = client.models.generate_content_stream(
                        model="gemini-3.8-flash",
                        contents=chat_prompt
                    )
                    for chunk in chat_stream:
                        if chunk.text:
                            full_chat += chunk.text
                            chat_placeholder.info(f"💡 **الإجابة:** {full_chat}▌")
                chat_placeholder.info(f"💡 **الإجابة:** {full_chat}")
        else:
            st.warning("🔑 يرجى وضع مفتاح Gemini API Key في الشريط الجانبي لتفعيل محرك التقرير التلقائي والشات الذكي.")

        # د) الرسوم البيانية والجداول
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

        # هـ) عرض وتصدير الجداول والتقرير متعدد الصيغ
        st.markdown(f'<div class="section-title">📋 تصدير التقرير والبيانات بالتنسيق المطلوب</div>', unsafe_allow_html=True)
        st.dataframe(df_grouped, use_container_width=True)

        st.markdown("### 📥 اختيار صيغة الملف لتصدير التقرير والبيانات:")
        export_format = st.radio(
            "اختر صيغة الملف المراد تنزيله:",
            options=["Excel (.xlsx)", "Word (.docx)", "PowerPoint (.pptx)"],
            horizontal=True
        )

        ai_report_text = st.session_state.get('latest_report', 'لم يتم توليد التقرير المالي بالذكاء الاصطناعي بعد.')

        if export_format == "Excel (.xlsx)":
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Raw_Data')
                df_grouped.to_excel(writer, index=False, sheet_name='Summary_Data')
                report_df = pd.DataFrame([{"AI_Financial_Report": ai_report_text}])
                report_df.to_excel(writer, index=False, sheet_name='AI_Report')
            
            st.download_button(
                label="📊 تحميل ملف Excel الشامل (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"AMAN_Full_Report_{group_by_col}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        elif export_format == "Word (.docx)":
            doc = Document()
            doc.add_heading('تقرير أمان للتحليل المالي الشامل', 0)
            
            doc.add_heading('1. التقرير المالي للذكاء الاصطناعي (AI Summary)', level=1)
            doc.add_paragraph(ai_report_text)
            
            doc.add_heading(f'2. جدول البيانات التجميعي ({group_by_col})', level=1)
            table = doc.add_table(rows=1, cols=len(df_grouped.columns))
            hdr_cells = table.rows[0].cells
            for col_idx, col_name in enumerate(df_grouped.columns):
                hdr_cells[col_idx].text = str(col_name)
            
            for _, row in df_grouped.head(30).iterrows():
                row_cells = table.add_row().cells
                for col_idx, value in enumerate(row):
                    row_cells[col_idx].text = str(value)

            doc_buffer = io.BytesIO()
            doc.save(doc_buffer)
            doc_buffer.seek(0)

            st.download_button(
                label="📄 تحميل مستند Word الشامل (.docx)",
                data=doc_buffer.getvalue(),
                file_name=f"AMAN_Financial_Report_{group_by_col}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

        elif export_format == "PowerPoint (.pptx)":
            prs = Presentation()
            
            # الشريحة الأولى: العنوان
            slide_layout = prs.slide_layouts[0]
            slide = prs.slides.add_slide(slide_layout)
            slide.shapes.title.text = "منصة AMAN للتحليل المالي"
            slide.placeholders[1].text = f"تقرير مالي شامل لورقة: {selected_sheet}"

            # الشريحة الثانية: تقرير الذكاء الاصطناعي
            slide_layout2 = prs.slide_layouts[1]
            slide2 = prs.slides.add_slide(slide_layout2)
            slide2.shapes.title.text = "الملخص التنفيذي بالذكاء الاصطناعي"
            slide2.placeholders[1].text = ai_report_text[:1000] + ("..." if len(ai_report_text) > 1000 else "")

            pptx_buffer = io.BytesIO()
            prs.save(pptx_buffer)
            pptx_buffer.seek(0)

            st.download_button(
                label="مستند PowerPoint التقديمي (.pptx)",
                data=pptx_buffer.getvalue(),
                file_name=f"AMAN_Presentation_{group_by_col}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"حدث خطأ أثناء تحليل الشيت: {e}")

else:
    st.info("👈 قم برفع أي ملف إكسيل من الشريط الجانبي لبدء التحليل التلقائي والشات الذكي.")
