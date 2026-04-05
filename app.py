import streamlit as st
import pandas as pd
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="💰 My Finance Tracker", layout="wide")

# =========================================================
# 📂 ส่วนที่ 1 : ระบบฐานข้อมูลผ่าน Google Sheets
# =========================================================
# สร้างการเชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ⚠️ ลิงก์สมุดบัญชี Google Sheets ของคุณ (เอาลิงก์มาวางในเครื่องหมายคำพูด)
SHEET_URL = "ลิงก์_URL_ของ_Sheets_ของคุณ_ใส่ตรงนี้" 

# ฟังก์ชันโหลดข้อมูลจาก Google Sheets
def load_data():
    try:
        # ดึงข้อมูลจากชีตที่ชื่อว่า "Sheet1" (ชีตแรกสุด)
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Sheet1")
        # ถ้าชีตเพิ่งสร้างใหม่และยังว่างเปล่า ให้สร้างหัวตารางเตรียมไว้
        if df.empty or 'วันที่' not in df.columns:
            return pd.DataFrame(columns=["วันที่", "ประเภท", "หมวดหมู่", "จำนวนเงิน", "บันทึกช่วยจำ"])
        return df.dropna(how='all') # ลบแถวที่ว่างเปล่าออก
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return pd.DataFrame(columns=["วันที่", "ประเภท", "หมวดหมู่", "จำนวนเงิน", "บันทึกช่วยจำ"])

# ฟังก์ชันบันทึกข้อมูลทับลงไปใน Google Sheets
def save_data(df_to_save):
    # อัปเดตข้อมูลทับกลับไปที่ชีต
    conn.update(spreadsheet=SHEET_URL, worksheet="Sheet1", data=df_to_save)
    st.cache_data.clear() # เคลียร์ความจำแคชเพื่อให้เว็บดึงข้อมูลใหม่สุด

# =========================================================
# ⚙️ ตั้งค่าหมวดหมู่
# =========================================================
# ในเวอร์ชันนี้ เราจะใช้หมวดหมู่คงที่ในโค้ดไปก่อน เพื่อความเสถียร
expense_categories = [
    "🏠 ค่าที่อยู่อาศัย (ค่าเช่า, ผ่อนบ้าน)",
    "💡 ค่าสาธารณูปโภค (ค่าน้ำ, ค่าไฟ, เน็ต)",
    "🚗 ค่าเดินทาง (น้ำมัน, รถสาธารณะ)",
    "🍜 ค่าอาหาร (จำเป็น)",
    "🏥 ค่าสุขภาพ (ประกัน, หาหมอ)",
    "💳 ค่าผ่อนชำระ (ผ่อนรถ, หนี้สิน)",
    "🛍️ ช็อปปิ้ง (เสื้อผ้า, เครื่องสำอาง)",
    "🎬 ความบันเทิง (ดูหนัง, ท่องเที่ยว, Netflix)",
    "🧴 ของใช้ส่วนตัว",
    "🙏 ทำบุญ / ให้ครอบครัว",
    "➕ อื่นๆ"
]

# =========================================================
# 🧮 ส่วนที่ 2 : ฟังก์ชันคำนวณยอดเงิน
# =========================================================
def calculate_balance():
    df = load_data()
    if df.empty:
        return 0, 0, 0, 0
    
    total_income = pd.to_numeric(df[df['ประเภท'] == '🟢 รายรับ']['จำนวนเงิน'], errors='coerce').sum()
    total_expense = pd.to_numeric(df[df['ประเภท'] == '🔴 รายจ่าย']['จำนวนเงิน'], errors='coerce').sum()
    total_savings = pd.to_numeric(df[df['ประเภท'] == '🐷 เงินเก็บ']['จำนวนเงิน'], errors='coerce').sum()
    
    current_balance = total_income - total_expense - total_savings
    return total_income, total_expense, total_savings, current_balance

# =========================================================
# 🧭 ส่วนที่ 3 : เมนูและการนำทาง
# =========================================================
st.sidebar.title("💰 Finance Tracker (Pro)")
st.sidebar.caption("เชื่อมต่อข้อมูลปลอดภัยด้วย Google Sheets")

page = st.sidebar.radio("เลือกเมนูการใช้งาน:", [
    "📝 บันทึกรับ-จ่าย", 
    "📊 สรุปยอดสถิติ", 
    "⚙️ จัดการข้อมูล (แก้ไข/ลบ)"
])

# อัปเดตยอดเงินแบบเรียลไทม์ไว้ที่ Sidebar
inc, exp, sav, bal = calculate_balance()
st.sidebar.divider()
st.sidebar.metric("💵 เงินคงเหลือ (พร้อมใช้)", f"฿ {bal:,.2f}")
st.sidebar.metric("🐷 เงินเก็บสะสมทั้งหมด", f"฿ {sav:,.2f}")

# =========================================================
# 📝 หน้าที่ 1 : บันทึกรับ-จ่าย และโอนเข้าเงินเก็บ
# =========================================================
if page == "📝 บันทึกรับ-จ่าย":
    st.title("📝 บันทึกรายรับ-รายจ่าย")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 รายรับรวม", f"฿ {inc:,.2f}")
    col2.metric("🔴 รายจ่ายรวม", f"฿ {exp:,.2f}")
    col3.metric("💵 เงินคงเหลือปัจจุบัน", f"฿ {bal:,.2f}")
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["🔴 บันทึกรายจ่าย", "🟢 บันทึกรายรับ", "🐷 เก็บเงินคงเหลือ"])
    
    with tab1:
        with st.form("expense_form", clear_on_submit=True):
            e_date = st.date_input("วันที่:", date.today())
            e_cat = st.selectbox("หมวดหมู่:", expense_categories)
            e_amt = st.number_input("จำนวนเงิน (บาท):", min_value=0.0, step=10.0)
            e_note = st.text_input("บันทึกช่วยจำ (เช่น ค่าข้าวผัด, ค่าเน็ต):")
            if st.form_submit_button("💾 บันทึกรายจ่าย", type="primary"):
                df_existing = load_data()
                new_row = pd.DataFrame([{"วันที่": str(e_date), "ประเภท": "🔴 รายจ่าย", "หมวดหมู่": e_cat, "จำนวนเงิน": e_amt, "บันทึกช่วยจำ": e_note}])
                df_updated = pd.concat([df_existing, new_row], ignore_index=True)
                save_data(df_updated)
                st.success("บันทึกรายจ่ายลง Google Sheets เรียบร้อย!")
                st.rerun()

    with tab2:
        with st.form("income_form", clear_on_submit=True):
            i_date = st.date_input("วันที่:", date.today())
            i_cat = st.selectbox("ที่มาของรายรับ:", ["เงินเดือน", "โบนัส", "รายได้เสริม", "อื่นๆ"])
            i_amt = st.number_input("จำนวนเงิน (บาท):", min_value=0.0, step=100.0)
            i_note = st.text_input("บันทึกช่วยจำ:")
            if st.form_submit_button("💾 บันทึกรายรับ", type="primary"):
                df_existing = load_data()
                new_row = pd.DataFrame([{"วันที่": str(i_date), "ประเภท": "🟢 รายรับ", "หมวดหมู่": i_cat, "จำนวนเงิน": i_amt, "บันทึกช่วยจำ": i_note}])
                df_updated = pd.concat([df_existing, new_row], ignore_index=True)
                save_data(df_updated)
                st.success("บันทึกรายรับลง Google Sheets เรียบร้อย!")
                st.rerun()
                
    with tab3:
        st.write("### 🐷 ตัดยอดเงินคงเหลือไปเป็นเงินเก็บ")
        st.write(f"ตอนนี้คุณมีเงินคงเหลือที่สามารถเก็บได้: **฿ {bal:,.2f}**")
        
        save_all = st.checkbox("โอนเงินคงเหลือทั้งหมดเข้ากระปุก")
        if save_all:
            s_amt = st.number_input("จำนวนเงินที่จะเก็บ (บาท):", value=float(bal), disabled=True)
            s_amt = float(bal)
        else:
            s_amt = st.number_input("พิมพ์จำนวนเงินที่ต้องการเก็บ (บาท):", min_value=0.0, max_value=float(bal) if bal > 0 else 0.0, step=100.0)
            
        s_date = st.date_input("วันที่โอนเข้ากระปุก:", date.today())
        s_note = st.text_input("เป้าหมายการเก็บเงิน (เช่น ทริปเที่ยว, ซื้อของ):")
        
        if st.button("💾 ยืนยันการเก็บเงิน", type="primary"):
            if s_amt > 0:
                df_existing = load_data()
                new_row = pd.DataFrame([{"วันที่": str(s_date), "ประเภท": "🐷 เงินเก็บ", "หมวดหมู่": "ออมเงิน", "จำนวนเงิน": s_amt, "บันทึกช่วยจำ": s_note}])
                df_updated = pd.concat([df_existing, new_row], ignore_index=True)
                save_data(df_updated)
                st.success(f"โอนเงิน ฿{s_amt:,.2f} เข้ากระปุกเรียบร้อยแล้ว! 🥳")
                st.rerun()
            else:
                st.warning("จำนวนเงินต้องมากกว่า 0 หรือคุณไม่มีเงินคงเหลือให้เก็บครับ")

# =========================================================
# 📊 หน้าที่ 2 : สรุปยอดและกราฟ
# =========================================================
elif page == "📊 สรุปยอดสถิติ":
    st.title("📊 สรุปยอดและวิเคราะห์")
    df = load_data()
    
    if not df.empty:
        df['วันที่'] = pd.to_datetime(df['วันที่'])
        df['ปี'] = df['วันที่'].dt.year
        df['เดือน'] = df['วันที่'].dt.month
        df['ปี-เดือน'] = df['วันที่'].dt.strftime('%Y-%m')
        
        filter_type = st.radio("เลือกรูปแบบการสรุปยอด:", ["ภาพรวมทั้งหมด", "รายเดือน", "รายปี"], horizontal=True)
        
        filtered_df = df.copy()
        if filter_type == "รายเดือน":
            months = sorted(df['ปี-เดือน'].unique(), reverse=True)
            selected_month = st.selectbox("เลือกเดือน:", months)
            filtered_df = df[df['ปี-เดือน'] == selected_month]
        elif filter_type == "รายปี":
            years = sorted(df['ปี'].unique(), reverse=True)
            selected_year = st.selectbox("เลือกปี:", years)
            filtered_df = df[df['ปี'] == selected_year]
            
        f_inc = pd.to_numeric(filtered_df[filtered_df['ประเภท'] == '🟢 รายรับ']['จำนวนเงิน'], errors='coerce').sum()
        f_exp = pd.to_numeric(filtered_df[filtered_df['ประเภท'] == '🔴 รายจ่าย']['จำนวนเงิน'], errors='coerce').sum()
        f_sav = pd.to_numeric(filtered_df[filtered_df['ประเภท'] == '🐷 เงินเก็บ']['จำนวนเงิน'], errors='coerce').sum()
        
        st.write("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 รายรับรวม", f"฿ {f_inc:,.2f}")
        col2.metric("🔴 รายจ่ายรวม", f"฿ {f_exp:,.2f}")
        col3.metric("🐷 เงินเก็บ", f"฿ {f_sav:,.2f}")
        
        st.write("---")
        st.subheader("📉 รายจ่ายแยกตามหมวดหมู่")
        exp_df = filtered_df[filtered_df['ประเภท'] == '🔴 รายจ่าย']
        if not exp_df.empty:
            exp_df['จำนวนเงิน'] = pd.to_numeric(exp_df['จำนวนเงิน'], errors='coerce')
            cat_sum = exp_df.groupby('หมวดหมู่')['จำนวนเงิน'].sum().sort_values(ascending=False)
            st.bar_chart(cat_sum)
            with st.expander("ดูตารางรายจ่ายแยกหมวดหมู่"):
                st.dataframe(cat_sum.reset_index().style.format({"จำนวนเงิน": "฿ {:,.2f}"}))
        else:
            st.info("ไม่มีข้อมูลรายจ่ายในช่วงเวลานี้")
    else:
        st.info("💡 ยังไม่มีข้อมูลการบันทึกครับ")

# =========================================================
# ⚙️ หน้าที่ 3 : จัดการและลบข้อมูล
# =========================================================
elif page == "⚙️ จัดการข้อมูล (แก้ไข/ลบ)":
    st.title("⚙️ ลบประวัติการบันทึก")
    st.write("เลือกรายการที่ต้องการลบทิ้ง หากบันทึกผิดพลาด (ข้อมูลจะถูกลบออกจาก Google Sheets ด้วย)")
    
    df = load_data()
    if not df.empty:
        df_show = df.copy()
        df_show.insert(0, "รหัสอ้างอิง (ID)", df_show.index)
        st.dataframe(df_show, hide_index=True)
        
        del_id = st.selectbox("เลือก 'รหัสอ้างอิง (ID)' ของรายการที่ต้องการลบทิ้ง:", df_show['รหัสอ้างอิง (ID)'].tolist())
        if st.button("❌ ยืนยันการลบรายการนี้", type="primary"):
            df = df.drop(del_id)
            save_data(df)
            st.success("ลบข้อมูลสำเร็จ! ลบออกจาก Google Sheets แล้ว")
            st.rerun()
    else:
        st.info("ตารางว่างเปล่า ยังไม่มีรายการให้ลบครับ")
