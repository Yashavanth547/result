import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="College Result System", page_icon="📊")

# -------------------------
# Database Setup
# -------------------------
def init_db():
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            roll_no TEXT PRIMARY KEY,
            name TEXT,
            marks TEXT,
            total INTEGER,
            average REAL,
            grade TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_result(roll_no, name, marks, total, avg, grade):
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO results VALUES (?, ?, ?, ?, ?, ?)",
              (roll_no, name, marks, total, avg, grade))
    conn.commit()
    conn.close()

def get_result(roll_no):
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("SELECT * FROM results WHERE roll_no=?", (roll_no,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_results():
    conn = sqlite3.connect("results.db")
    df = pd.read_sql("SELECT * FROM results", conn)
    conn.close()
    return df

def delete_result(roll_no):
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("DELETE FROM results WHERE roll_no=?", (roll_no,))
    conn.commit()
    conn.close()

# -------------------------
# Helper function for grading
# -------------------------
def calculate_grade(avg):
    if avg >= 75:
        return "Distinction"
    elif avg >= 60:
        return "First Class"
    elif avg >= 35:
        return "Pass"
    else:
        return "Fail"

# -------------------------
# Initialize DB
# -------------------------
init_db()

# -------------------------
# Student Section (No Login)
# -------------------------
st.title("🏫 College Student Result Portal")

st.subheader("🔹 Student Result Check")
roll = st.text_input("Enter Roll Number")

if st.button("Check Result"):
    row = get_result(roll)
    if row:
        st.success(f"✅ Result Found for {row[1]}")
        st.write(f"📌 Total Marks: {row[3]}")
        st.write(f"📌 Average: {row[4]:.2f}")
        st.write(f"📌 Grade: {row[5]}")
    else:
        st.error("❌ Result not found. Contact admin.")

# -------------------------
# Admin Login
# -------------------------
st.sidebar.title("🔐 Admin Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_btn = st.sidebar.button("Login")

if login_btn:
    if username == "admin" and password == "1234":
        st.sidebar.success("✅ Logged in as Admin")

        st.header("📊 Admin Panel: Manage Student Results")

        # Add new result
        with st.sidebar.expander("➕ Add / Update Student Result"):
            roll_no = st.sidebar.text_input("Roll Number")
            name = st.sidebar.text_input("Student Name")
            marks = st.sidebar.text_area("Enter Marks (comma separated)")

            if st.button("Save Result"):
                try:
                    marks_list = list(map(int, marks.split(",")))
                    total = sum(marks_list)
                    avg = total / len(marks_list)
                    grade = calculate_grade(avg)

                    add_result(roll_no, name, marks, total, avg, grade)
                    st.success(f"✅ Result saved for {name}")

                except:
                    st.error("Invalid marks entered!")

        # View all results
        st.subheader("📋 All Student Results")
        df = get_all_results()
        st.dataframe(df)

        # Delete result
        with st.expander("❌ Delete Student Result"):
            del_roll = st.text_input("Enter Roll Number to Delete")
            if st.button("Delete Result"):
                delete_result(del_roll)
                st.warning(f"⚠️ Result deleted for Roll No: {del_roll}")

        # Download option
        if not df.empty:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Results (CSV)", data=csv, file_name="results.csv", mime="text/csv")

    else:
        st.sidebar.error("❌ Invalid login credentials (Hint: admin / 1234)")

