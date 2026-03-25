import streamlit as st
import pandas as pd
from datetime import date
import os
import streamlit.components.v1 as components
from streamlit_calendar import calendar

# =========================================================
# 🔐 ส่วนที่ 1 : ตั้งค่ารายชื่อผู้ใช้งานและรหัสผ่าน
# =========================================================
# คุณสามารถเปลี่ยนชื่อและรหัสผ่านตรงนี้ได้ตามใจชอบเลยครับ!
USERS = {
    "suphaoat": "1234",   # บัญชีของคุณ (เปลี่ยนรหัสได้)
    "tomatogisss": "1234"      # บัญชีของแฟน (เปลี่ยนชื่อและรหัสได้)
}

# ตั้งค่าความจำของเว็บ (Session State) เพื่อจำว่าใครล็อกอินอยู่
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# =========================================================
# 🚪 ส่วนที่ 2 : หน้าต่าง Login (ด่านหน้า)
# =========================================================
def login_page():
    # จัดหน้าตาให้อยู่ตรงกลางสวยๆ
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.write("")
        st.title("🔐 เข้าสู่ระบบ")
        st.write("My Daily Habit Tracker & Planner")
        
        with st.container(border=True):
            input_user = st.text_input("👤 ชื่อผู้ใช้งาน (Username)")
            input_pass = st.text_input("🔑 รหัสผ่าน (Password)", type="password") # type=password ทำให้พิมพ์แล้วเป็นจุดดำๆ
            
            if st.button("เข้าสู่ระบบ", use_container_width=True, type="primary"):
                if input_user in USERS and USERS[input_user] == input_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = input_user
                    st.success("เข้าสู่ระบบสำเร็จ! กำลังพาท่านเข้าสู่แอป...")
                    st.rerun() # รีเฟรชหน้าเว็บเพื่อเปลี่ยนหน้า
                else:
                    st.error("❌ ชื่อผู้ใช้งานหรือรหัสผ่านไม่ถูกต้อง!")

# =========================================================
# 🏠 ส่วนที่ 3 : หน้าต่างแอปหลัก (จะเห็นก็ต่อเมื่อล็อกอินผ่าน)
# =========================================================
def main_app():
    user = st.session_state.username
    
    # 🌟 ทีเด็ดอยู่ตรงนี้: ตั้งชื่อไฟล์ข้อมูลให้แยกตามชื่อคนล็อกอิน!
    DATA_FILE = f"habit_data_{user}.csv"
    HABIT_FILE = f"habits_list_{user}.txt"
    NOTES_FILE = f"notes_data_{user}.csv"

    # --- ระบบจัดการรายชื่อกิจกรรม ---
    default_habits = [
        "🏋️ ยกน้ำหนัก / ออกกำลังกาย",
        "🏸 ตีแบดมินตัน",
        "🔬 ศึกษา Thalassiosira / ทำแล็บ",
        "💻 เขียนโค้ด / วิเคราะห์ข้อมูล",
        "🎣 ตกปลา"
    ]

    if not os.path.exists(HABIT_FILE):
        with open(HABIT_FILE, "w", encoding="utf-8") as f:
            for h in default_habits:
                f.write(h + "\n")

    with open(HABIT_FILE, "r", encoding="utf-8") as f:
        habits = [line.strip() for line in f.readlines() if line.strip()]

    # --- เมนูด้านข้าง (Sidebar) ---
    with st.sidebar:
        st.title(f"👋 สวัสดี, {user}!")
        
        # ปุ่มออกจากระบบ
        if st.button("🚪 ออกจากระบบ (Logout)", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
            
        st.divider()

        # นาฬิกาธีมดำ
        clock_html = """
        <div id="clock" style="
            font-family: 'Segoe UI', sans-serif; font-size: 24px; font-weight: bold; 
            text-align: center; padding: 15px; background-color: #1E1E1E; 
            color: #00FFAA; border-radius: 10px; margin-bottom: 20px;
            border: 1px solid #333; box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        "></div>
        <script>
            function updateTime() {
                var now = new Date();
                var timeString = now.toLocaleTimeString('th-TH', { hour12: false });
                document.getElementById('clock').innerHTML = '⏰ ' + timeString;
            }
            setInterval(updateTime, 1000); updateTime(); 
        </script>
        """
        components.html(clock_html, height=80)
        
        page = st.radio("เลือกหน้าต่างที่คุณต้องการ:", ["✅ Habit Tracker", "📅 ปฏิทินแพลนเนอร์"])

    # --- หน้า Habit Tracker ---
    if page == "✅ Habit Tracker":
        st.title("✅ My Daily Habit Tracker")
        st.write(f"พื้นที่ส่วนตัวของคุณ **{user}**")

        with st.expander("⚙️ จัดการตัวเลือกกิจกรรม (เพิ่ม/ลบ)"):
            tab1, tab2 = st.tabs(["➕ เพิ่มกิจกรรมใหม่", "🗑️ ลบกิจกรรมออก"])
            
            with tab1:
                new_habit = st.text_input("พิมพ์ชื่อกิจกรรมที่ต้องการเพิ่ม:")
                if st.button("เพิ่มเข้าสู่ระบบ"):
                    if new_habit and new_habit not in habits:
                        with open(HABIT_FILE, "a", encoding="utf-8") as f:
                            f.write(new_habit + "\n")
                        st.success(f"เพิ่ม '{new_habit}' เรียบร้อยแล้ว!")
                        st.rerun() 
                    elif new_habit in habits:
                        st.warning("มีกิจกรรมนี้อยู่แล้วครับ!")
                        
            with tab2:
                if len(habits) > 0:
                    habit_to_delete = st.selectbox("เลือกกิจกรรมที่ต้องการลบออกชั่วคราว/ถาวร:", habits)
                    if st.button("ลบกิจกรรมนี้", type="primary"):
                        habits.remove(habit_to_delete)
                        with open(HABIT_FILE, "w", encoding="utf-8") as f:
                            for h in habits:
                                f.write(h + "\n")
                        st.success(f"ลบ '{habit_to_delete}' ออกจากตัวเลือกแล้ว!")
                        st.rerun()
                else:
                    st.info("ไม่มีกิจกรรมเหลือให้ลบแล้วครับ")

        st.divider()

        today = date.today().strftime("%Y-%m-%d")
        st.subheader(f"📅 วันที่: {today}")

        options = ['✅ ทำแล้ว (Done)', '❌ ไม่ได้ทำ (Skip)', '🚙 มีธุระ (Errand)']
        daily_results = {"วันที่": [today]}

        if len(habits) > 0:
            for habit in habits:
                choice = st.radio(habit, options, index=1, horizontal=True)
                daily_results[habit] = [choice]
        else:
            st.warning("⚠️ ตอนนี้ไม่มีกิจกรรมให้เลือกเลย ลองไปกดเพิ่มที่เมนูจัดการด้านบนดูนะครับ")

        col1, col2 = st.columns(2)

        with col1:
            if len(habits) > 0 and st.button("💾 บันทึกข้อมูลวันนี้", use_container_width=True):
                df_new = pd.DataFrame(daily_results)
                if os.path.exists(DATA_FILE):
                    df_existing = pd.read_csv(DATA_FILE)
                    if today in df_existing['วันที่'].values:
                        df_existing = df_existing[df_existing['วันที่'] != today]
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                    df_combined = df_combined.sort_values(by='วันที่')
                    df_combined.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                else:
                    df_new.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                st.success("🎉 บันทึกข้อมูลเรียบร้อยแล้ว!")

        with col2:
            if st.button("ลบข้อมูลของวันนี้ทิ้ง 🔄", use_container_width=True):
                if os.path.exists(DATA_FILE):
                    df_existing = pd.read_csv(DATA_FILE)
                    if today in df_existing['วันที่'].values:
                        df_existing = df_existing[df_existing['วันที่'] != today]
                        df_existing.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')
                        st.success("เคลียร์ข้อมูลของวันนี้ทิ้งแล้วครับ!")
                        st.rerun()

        st.divider()

        st.subheader("📊 ประวัติและสถิติการทำกิจกรรม")

        if os.path.exists(DATA_FILE):
            df_history = pd.read_csv(DATA_FILE)
            if not df_history.empty:
                with st.expander("📝 ดูตารางข้อมูลบันทึกรายวัน"):
                    st.dataframe(df_history)
                
                st.write("### 📈 เปอร์เซ็นต์ความสำเร็จ (แยกตามเดือน)")
                df_calc = df_history.copy()
                habit_cols = [col for col in df_calc.columns if col != 'วันที่']
                df_calc['เดือน'] = pd.to_datetime(df_calc['วันที่']).dt.strftime('%Y-%m')
                
                for col in habit_cols:
                    df_calc[col] = df_calc[col].apply(lambda x: 1 if str(x).startswith('✅') else 0)
                    
                monthly_stats = df_calc.groupby('เดือน')[habit_cols].mean() * 100
                st.write("ตารางสรุปเปอร์เซ็นต์ %")
                st.dataframe(monthly_stats.style.format("{:.1f}%"))
                st.line_chart(monthly_stats)
            else:
                 st.info("💡 ตารางว่างเปล่า ลองบันทึกข้อมูลด้านบนดูก่อนนะ!")
        else:
            st.info("💡 ยังไม่มีข้อมูลประวัติการบันทึกครับ")

    # --- หน้า ปฏิทินแพลนเนอร์ ---
    elif page == "📅 ปฏิทินแพลนเนอร์":
        st.title("📅 ปฏิทินแพลนเนอร์")
        st.write(f"สมุดนัดหมายส่วนตัวของ **{user}**")
        
        if os.path.exists(NOTES_FILE):
            df_notes = pd.read_csv(NOTES_FILE)
        else:
            df_notes = pd.DataFrame(columns=["วันที่", "รายละเอียด"])

        calendar_events = []
        for index, row in df_notes.iterrows():
            calendar_events.append({
                "title": row["รายละเอียด"], 
                "start": row["วันที่"], 
                "allDay": True, 
                "backgroundColor": "#00FFAA", 
                "borderColor": "#00FFAA",
                "textColor": "#000000"
            })

        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,dayGridWeek,dayGridDay"
            },
            "initialView": "dayGridMonth",
        }
        
        st.write("### 📅 ปฏิทินโน้ต")
        calendar(events=calendar_events, options=calendar_options)

        st.divider()
        
        with st.expander("➕ กดที่นี่เพื่อจดโน้ต/นัดหมายใหม่"):
            with st.container():
                st.write("✍️ พิมพ์รายละเอียดและเลือกวันที่:")
                new_note_text = st.text_input("พิมพ์รายละเอียดนัดหมาย:")
                new_note_date = st.date_input("เลือกวันที่:")
                
                if st.button("💾 บันทึกนัดหมายใหม่", type="primary"):
                    if new_note_text.strip() != "":
                        new_note_df = pd.DataFrame({"วันที่": [str(new_note_date)], "รายละเอียด": [new_note_text]})
                        if os.path.exists(NOTES_FILE):
                            df_notes_existing = pd.read_csv(NOTES_FILE)
                            df_notes_updated = pd.concat([df_notes_existing, new_note_df], ignore_index=True)
                            df_notes_updated = df_notes_updated.sort_values(by="วันที่")
                            df_notes_updated.to_csv(NOTES_FILE, index=False, encoding='utf-8-sig')
                        else:
                            new_note_df.to_csv(NOTES_FILE, index=False, encoding='utf-8-sig')
                        st.success(f"บันทึกโน้ตสำหรับวันที่ {new_note_date} เรียบร้อย!")
                        st.rerun() 
                    else:
                        st.warning("⚠️ อย่าลืมพิมพ์รายละเอียดก่อนกดบันทึกนะครับ!")

        st.divider()
        
        st.subheader("📌 จัดการโน้ตและนัดหมาย")
        if os.path.exists(NOTES_FILE):
            df_notes_all = pd.read_csv(NOTES_FILE)
            if not df_notes_all.empty:
                with st.expander("📝 ดูตารางข้อมูลนัดหมายทั้งหมด"):
                    st.dataframe(df_notes_all)
                    
                st.write("🗑️ เลือกโน้ตที่ต้องการลบ:")
                unique_dates = df_notes_all['วันที่'].unique()
                note_date_to_del = st.selectbox("เลือกวันที่:", unique_dates)
                
                note_text_to_del = df_notes_all[df_notes_all['วันที่'] == note_date_to_del]['รายละเอียด'].values[0]
                with st.chat_message("user", avatar="📅"):
                    st.write(f"**นัดหมายวันที่:** {note_date_to_del}")
                    st.write(note_text_to_del)

                if st.button("ลบโน้ตนี้", type="primary"):
                    df_notes_updated = df_notes_all[df_notes_all['วันที่'] != note_date_to_del]
                    df_notes_updated.to_csv(NOTES_FILE, index=False, encoding='utf-8-sig')
                    st.success("ลบโน้ตสำเร็จ!")
                    st.rerun()
            else:
                st.info("💡 ยังไม่มีข้อมูลนัดหมายครับ")
        else:
            st.info("💡 ยังไม่มีข้อมูลนัดหมายครับ")

# =========================================================
# 🚦 ตัวสลับหน้า (ถ้าล็อกอินแล้วให้เข้าแอป ถ้ายังให้แสดงหน้า Login)
# =========================================================
if st.session_state.logged_in:
    main_app()
else:
    login_page()