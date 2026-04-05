import streamlit as st
import pandas as pd
from datetime import date
import streamlit.components.v1 as components
from streamlit_calendar import calendar
from streamlit_gsheets import GSheetsConnection

# =========================================================
# 🔐 ส่วนที่ 1 : ตั้งค่าแอปและการเชื่อมต่อ
# =========================================================
st.set_page_config(page_title="✅ My Planner & Tracker")

conn = st.connection("gsheets", type=GSheetsConnection)

# ⚠️ ผมใส่ลิงก์ Google Sheets ของคุณให้เรียบร้อยแล้วครับ!
SHEET_URL = "https://docs.google.com/spreadsheets/d/16e67op4_nymQ7lky9yolJ-IrFbWSLaNJcJTcsuua1LU/edit?gid=0#gid=0"

USERS = {
    "suphaoat": "1234",   
    "tomatogisss": "1234"      
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# =========================================================
# 🗂️ ฟังก์ชันจัดการฐานข้อมูล Google Sheets
# =========================================================
def load_data(tab_name):
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet=tab_name)
        return df.dropna(how='all') if not df.empty else pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ หาหน้ากระดาษไม่เจอ กรุณาสร้างแท็บชื่อ '{tab_name}' ใน Google Sheets ครับ")
        return pd.DataFrame()

def save_data(tab_name, df_to_save):
    conn.update(spreadsheet=SHEET_URL, worksheet=tab_name, data=df_to_save)
    st.cache_data.clear()

# =========================================================
# 🚪 ส่วนที่ 2 : หน้าต่าง Login
# =========================================================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.title("🔐 เข้าสู่ระบบ")
        st.write("My Daily Habit Tracker & Planner (Pro)")
        
        with st.container(border=True):
            input_user = st.text_input("👤 ชื่อผู้ใช้งาน (Username)")
            input_pass = st.text_input("🔑 รหัสผ่าน (Password)", type="password")
            if st.button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
                if input_user in USERS and USERS[input_user] == input_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    st.rerun() 
                else:
                    st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง!")

# =========================================================
# 🏠 ส่วนที่ 3 : หน้าต่างแอปหลัก
# =========================================================
def main_app():
    user = st.session_state.username
    
    # 💡 รายชื่อกิจกรรม
    my_habits = [
        "🏋️ ยกน้ำหนัก / ออกกำลังกาย",
        "🏸 ตีแบดมินตัน",
        "🔬 ศึกษา Thalassiosira / ทำแล็บ",
        "💻 เขียนโค้ด / วิเคราะห์ข้อมูล",
        "🎣 ตกปลา"
    ]

    with st.sidebar:
        st.title(f"👋 สวัสดี, {user}!")
        if st.button("🚪 ออกจากระบบ", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
            
        st.divider()
        page = st.radio("เลือกหน้าต่าง:", ["✅ Habit Tracker", "📅 ปฏิทินแพลนเนอร์"])

    # ---------------------------------------------------------
    # หน้าที่ 1 : Habit Tracker (เซฟลงแท็บ Habits)
    # ---------------------------------------------------------
    if page == "✅ Habit Tracker":
        st.title("✅ My Daily Habit Tracker")
        today = date.today().strftime("%Y-%m-%d")
        st.subheader(f"📅 บันทึกของวันที่: {today}")

        options = ['✅ ทำแล้ว (Done)', '❌ ไม่ได้ทำ (Skip)', '🚙 มีธุระ (Errand)']
        daily_results = {"วันที่": [today], "Username": [user]}

        for habit in my_habits:
            choice = st.radio(habit, options, index=1, horizontal=True)
            daily_results[habit] = [choice]

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 บันทึกข้อมูลวันนี้", use_container_width=True, type="primary"):
                df_new = pd.DataFrame(daily_results)
                df_all = load_data("Habits")
                
                if not df_all.empty and 'วันที่' in df_all.columns and 'Username' in df_all.columns:
                    # ลบของเก่าของวันนี้(ของคนๆนี้)ออกก่อน แล้วใส่ของใหม่ทับ
                    df_all = df_all[~((df_all['วันที่'] == today) & (df_all['Username'] == user))]
                    df_combined = pd.concat([df_all, df_new], ignore_index=True)
                else:
                    df_combined = df_new
                    
                save_data("Habits", df_combined)
                st.success("🎉 บันทึกลง Google Sheets สำเร็จ!")

        st.divider()
        st.subheader("📊 ประวัติกิจกรรมของคุณ")
        df_history = load_data("Habits")
        if not df_history.empty and 'Username' in df_history.columns:
            user_history = df_history[df_history['Username'] == user].drop(columns=['Username'])
            if not user_history.empty:
                st.dataframe(user_history)
            else:
                st.info("ยังไม่มีข้อมูลของคุณครับ")
        else:
            st.info("ตารางว่างเปล่า")

    # ---------------------------------------------------------
    # หน้าที่ 2 : Calendar Planner (เซฟลงแท็บ Planner)
    # ---------------------------------------------------------
    elif page == "📅 ปฏิทินแพลนเนอร์":
        st.title("📅 ปฏิทินแพลนเนอร์")
        
        df_notes = load_data("Planner")
        if not df_notes.empty and 'Username' in df_notes.columns:
            user_notes = df_notes[df_notes['Username'] == user]
        else:
            user_notes = pd.DataFrame(columns=["วันที่", "Username", "รายละเอียด"])

        calendar_events = []
        for index, row in user_notes.iterrows():
            calendar_events.append({
                "title": row["รายละเอียด"], "start": row["วันที่"], 
                "allDay": True, "backgroundColor": "#00FFAA", "textColor": "#000"
            })

        calendar(events=calendar_events, options={"initialView": "dayGridMonth"})

        st.divider()
        st.write("### ➕ จดนัดหมายใหม่")
        new_note_text = st.text_input("พิมพ์รายละเอียดนัดหมาย:")
        new_note_date = st.date_input("เลือกวันที่:")
        
        if st.button("💾 บันทึกนัดหมาย", type="primary"):
            if new_note_text:
                df_new = pd.DataFrame({"วันที่": [str(new_note_date)], "Username": [user], "รายละเอียด": [new_note_text]})
                df_combined = pd.concat([df_notes, df_new], ignore_index=True)
                save_data("Planner", df_combined)
                st.success("บันทึกนัดหมายลง Google Sheets สำเร็จ!")
                st.rerun() 
            else:
                st.warning("พิมพ์รายละเอียดก่อนกดบันทึกนะครับ")

if st.session_state.logged_in:
    main_app()
else:
    login_page()
