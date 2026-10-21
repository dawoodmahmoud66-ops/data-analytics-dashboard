import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ---------------------------------------------------------
# 1. إعدادات الصفحة والتصميم
# ---------------------------------------------------------
st.set_page_config(
    page_title="داشبورد تحليل محفظة العقود والتوريق 2026",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #071e33; color: #ffffff; direction: rtl; text-align: right; }
    
    .kpi-card { 
        background-color: #0b2847; 
        border-radius: 12px; 
        padding: 18px; 
        border-right: 5px solid #00c4cc; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
        margin-bottom: 15px;
    }
    .kpi-title { color: #90caf9; font-size: 13px; font-weight: bold; }
    .kpi-value { color: #00c4cc; font-size: 21px; font-weight: bold; margin-top: 5px; }
    .kpi-sub { color: #b0bec5; font-size: 11px; margin-top: 3px; }
    
    .card-header { 
        background-color: #0b2847; 
        color: #ffffff; 
        padding: 10px 15px; 
        font-weight: bold; 
        font-size: 16px; 
        border-radius: 6px; 
        margin-bottom: 15px; 
        border-right: 3px solid #00c4cc; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 نظام تحليل محفظة العقود والماليات والسنوات (2026)")
st.caption("تحليل تلقائي لمبالغ Formal AR وتحليل التراكمات المالية بحسب الشهر والسنة")
st.markdown("---")

# ---------------------------------------------------------
# 2. القائمة الجانبية لرفع شيت الإكسيل
# ---------------------------------------------------------
st.sidebar.header("📁 رفع بيانات الإكسيل")
uploaded_file = st.sidebar.file_uploader(
    "قم برفع ملف Excel (.xlsx)", 
    type=["xlsx", "xls"]
)

# ---------------------------------------------------------
# 3. معالجة وتوليد التقرير المباشر
# ---------------------------------------------------------
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        st.sidebar.success(f"تم تحميل الملف بنجاح: {uploaded_file.name}")
        
        # --- أ) التعرف التلقائي على الأعمدة ---
        status_col = None
        ar_col = None
        principal_col = None
        interest_col = None
        date_col = None
        
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
            elif "date" in c_str or "تاريخ" in c_str or "printed" in c_str or "شريحة" in c_str or "سنة" in c_str:
                date_col = col

        # التعيين الإفتراضي
        if not status_col:
            status_col = "الحاله" if "الحاله" in df.columns else df.columns[2]
        if not ar_col:
            ar_col = "AR" if "AR" in df.columns else (df.columns[7] if len(df.columns) > 7 else df.columns[-1])
        if not principal_col:
            principal_col = "totalprinc_asoff" if "totalprinc_asoff" in df.columns else df.columns[8]
        if not interest_col:
            interest_col = "totalinterest_asoff" if "totalinterest_asoff" in df.columns else df.columns[9]
            
        # --- ب) حساب كروت KPIs ---
        total_records = len(df)
        sum_ar = df[ar_col].sum() if ar_col in df.columns else 0
        sum_principal = df[principal_col].sum() if principal_col in df.columns else 0
        sum_interest = df[interest_col].sum() if interest_col in df.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي عدد العقود</div><div class="kpi-value">{total_records:,}</div><div class="kpi-sub">عقد مسجل</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي (Formal AR)</div><div class="kpi-value">{sum_ar:,.2f}</div><div class="kpi-sub">ج.م (القيمة المستحقة)</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي (Formal Principal)</div><div class="kpi-value">{sum_principal:,.2f}</div><div class="kpi-sub">ج.م (أصل الدين)</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">إجمالي (Formal Interest)</div><div class="kpi-value">{sum_interest:,.2f}</div><div class="kpi-sub">ج.م (إجمالي الفوائد)</div></div>', unsafe_allow_html=True)

        st.write("")

        # --- ج) الرسم البياني يقرأ من مبلغ Formal AR وموزع بالحالة ---
        st.markdown(f'<div class="card-header">📈 توزيع مبالغ (Formal AR) بحسب ({status_col})</div>', unsafe_allow_html=True)
        
        df_grouped_status = df.groupby(status_col, as_index=False)[ar_col].sum()

        fig = px.bar(
            df_grouped_status, 
            x=status_col, 
            y=ar_col,
            text_auto='.3s',
            title=f"توزيع إجمالي Formal AR بحسب {status_col}",
            color_discrete_sequence=['#00c4cc']
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color='#ffffff',
            xaxis_title=str(status_col),
            yaxis_title="Formal AR (جنيه مصري)",
            xaxis={'categoryorder': 'total descending'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- د) تحليلات التراكم بالشهر والسنة (Monthly & Yearly Accumulation) ---
        st.markdown('<div class="card-header">🗓️ جدول تحليل التراكمات المالية بحسب الشهر والسنة (أعلى كميات متراكمة)</div>', unsafe_allow_html=True)

        # معالجة عمود التواريخ لاستخراج السنة والشهر
        if date_col and date_col in df.columns:
            df['تاريخ_المعاملة'] = pd.to_datetime(df[date_col], errors='coerce')
            df['السنة'] = df['تاريخ_المعاملة'].dt.year.fillna(2026).astype(int)
            df['الشهر'] = df['تاريخ_المعاملة'].dt.strftime('%B / %m').fillna('Jan / 01')
        else:
            df['السنة'] = 2026
            df['الشهر'] = 'يناير (Jan)'

        # جدول التجميع حسب السنة والشهر
        df_accum = df.groupby(['السنة', 'الشهر'], as_index=False).agg({
            ar_col: 'sum',
            principal_col: 'sum',
            interest_col: 'sum',
            status_col: 'count'
        }).rename(columns={status_col: 'عدد العقود', ar_col: 'Formal AR المتراكم'})

        # فرز لمعرفة أضخم التراكمات
        df_accum = df_accum.sort_values(by='Formal AR المتراكم', ascending=False)

        # عرض التنبيه بأضخم سنة وشهر متراكم
        top_row = df_accum.iloc[0] if len(df_accum) > 0 else None
        if top_row is not None:
            st.info(f"🔥 **أكبر كمية متراكمة في المحفظة:** سنة **{top_row['السنة']}** - شهر **{top_row['الشهر']}** إجمالي متراكم **{top_row['Formal AR المتراكم']:,.2f} ج.م** بـ **{top_row['عدد العقود']:,} عقد**.")

        st.dataframe(df_accum, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة البيانات: {e}")

else:
    # --- العرض الافتراضي ---
    st.info("💡 قم برفع ملف الإكسيل لمشاهدة تحليل Formal AR وتراكمات السنوات والأشهر تلقائياً.")
    
    df_demo = pd.DataFrame({
        'الحاله': ['كارت امان', 'كارت اسلامي', 'نورمال اسلامي', 'زيادة الحد الائتماني', 'نورمال', 'B2E'],
        'AR': [89165737, 477430445, 752773409, 12171344, 34844098, 3549054],
        'totalprinc_asoff': [65736465, 350502583, 448755291, 9727388, 21804801, 2763485],
        'totalinterest_asoff': [23429272, 126927862, 304018118, 2443956, 13039298, 785569]
    })

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">عدد العقود</div><div class="kpi-value">20,578</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Formal AR</div><div class="kpi-value">{df_demo["AR"].sum():,.2f} ج.م</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Formal Principal</div><div class="kpi-value">{df_demo["totalprinc_asoff"].sum():,.2f} ج.م</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Formal Interest</div><div class="kpi-value">{df_demo["totalinterest_asoff"].sum():,.2f} ج.م</div></div>', unsafe_allow_html=True)

    st.write("")
    fig = px.bar(df_demo, x='الحاله', y='AR', text_auto='.3s', title="توزيع Formal AR بحسب الحالة (عرض افتراضي)", color_discrete_sequence=['#00c4cc'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#ffffff')
    st.plotly_chart(fig, use_container_width=True)
