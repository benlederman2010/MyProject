import gradio as gr
import bcrypt
import json
import os

# נתיב לקובץ המשתמשים
USERS_FILE = "users_db.json"


def load_users():
    """טעינת משתמשים מקובץ JSON והמרת הסיסמאות חזרה ל-bytes"""
    if not os.path.exists(USERS_FILE):
        # אם הקובץ לא קיים, ניצור ברירת מחדל ראשונית
        default_users = {
            "alice": bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode('utf-8'),
            "bob": bcrypt.hashpw(b"qwerty", bcrypt.gensalt()).decode('utf-8'),
        }
        save_users(default_users)
        return {k: v.encode('utf-8') for k, v in default_users.items()}

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        # המרה חזרה מ-string ל-bytes עבור bcrypt
        return {k: v.encode('utf-8') for k, v in data.items()}


def save_users(users_dict):
    """שמירת המילון לקובץ JSON תוך המרת ה-bytes ל-string"""
    # המרה לפורמט שניתן לשמור ב-JSON
    serializable_users = {k: (v.decode('utf-8') if isinstance(v, bytes) else v)
                          for k, v in users_dict.items()}
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_users, f, indent=4, ensure_ascii=False)


# טעינת המשתמשים בעת הפעלת האפליקציה
USERS = load_users()

# עיצוב CSS להצמדה לימין (RTL)
css_code = """
.gradio-container { direction: rtl; text-align: right; }
input, textarea { direction: rtl !important; text-align: right !important; }
.label-wrap { justify-content: flex-end !important; }
"""


def open_register():
    return (gr.update(visible=False), gr.update(visible=True), gr.update(visible=False))


def register(username, password):
    if not username or not password:
        return gr.update(visible=True, value="❌ נא להזין שם וסיסמה"), gr.update(), gr.update()

    if username in USERS:
        return (gr.update(visible=True, value="❌ משתמש כבר קיים"), gr.update(visible=True), gr.update(visible=False))

    # הצפנה ושמירה במילון
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    USERS[username] = hashed_pw

    # שמירה פיזית לקובץ JSON
    save_users(USERS)

    return (gr.update(visible=False, value=""), gr.update(visible=True), gr.update(visible=False))


def login(username, password):
    if username not in USERS:
        return ("", gr.update(visible=True), gr.update(visible=False), gr.update(visible=True, value="❌ משתמש לא נמצא"),
                "")

    # בדיקת הסיסמה מול ה-bytes שבמילון
    ok = bcrypt.checkpw(password.encode(), USERS[username])
    if ok:
        return (username, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False, value=""),
                f"## ברוך הבא, {username}! ")

    return ("", gr.update(visible=True), gr.update(visible=False), gr.update(visible=True, value="❌ סיסמה שגויה"), "")


def logout():
    return ("", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False, value=""), "", "", "")


with gr.Blocks() as app:
    user_state = gr.State("")

    with gr.Column(visible=True) as login_panel:
        gr.Markdown("## מסך כניסה")
        username_input = gr.Textbox(label="שם משתמש")
        password_input = gr.Textbox(label="סיסמה", type="password")
        with gr.Row():
            login_btn = gr.Button("כניסה", variant="primary")
            reg_btn = gr.Button("רישום")
        err = gr.Textbox(label="הודעת מערכת", visible=False)

    with gr.Column(visible=False) as register_panel:
        gr.Markdown("## מסך רישום")
        reg_username = gr.Textbox(label="שם משתמש חדש")
        reg_password = gr.Textbox(label="סיסמה חדשה", type="password")
        do_reg_btn = gr.Button("בצע רישום", variant="primary")
        reg_err = gr.Textbox(label="שגיאת רישום", visible=False)
        back_btn = gr.Button("חזור", variant="secondary")

    with gr.Column(visible=False) as main_panel:
        gr.Markdown("## מסך ראשי")
        welcome_msg = gr.Markdown()
        logout_btn = gr.Button("התנתק", variant="primary")

    login_btn.click(fn=login, inputs=[username_input, password_input],
                    outputs=[user_state, login_panel, main_panel, err, welcome_msg])
    reg_btn.click(fn=open_register, outputs=[login_panel, register_panel, main_panel])
    do_reg_btn.click(fn=register, inputs=[reg_username, reg_password], outputs=[reg_err, login_panel, register_panel])
    back_btn.click(fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
                   outputs=[login_panel, register_panel])
    logout_btn.click(fn=logout, outputs=[user_state, login_panel, main_panel, err, welcome_msg, username_input, password_input])

if __name__ == "__main__":
    app.launch(css=css_code)