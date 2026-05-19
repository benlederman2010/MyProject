import gradio as gr
import bcrypt
import json
import os

import reversed_substitution
import climbing_key

# ---- ניהול משתמשים ----

USERS_FILE = "users_db.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        default_users = {
            "alice": bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode('utf-8'),
            "bob": bcrypt.hashpw(b"qwerty", bcrypt.gensalt()).decode('utf-8'),
        }
        save_users(default_users)
        return {k: v.encode('utf-8') for k, v in default_users.items()}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {k: v.encode('utf-8') for k, v in data.items()}


def save_users(users_dict):
    serializable = {k: (v.decode('utf-8') if isinstance(v, bytes) else v) for k, v in users_dict.items()}
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=4, ensure_ascii=False)


USERS = load_users()

css_code = """
/* הגדרת כיוון כללי לימין לכל האפליקציה */
.gradio-container { 
    direction: rtl !important; 
    text-align: right !important;
    background-color: #f7f7f7; /* רקע אפור בהיר ונעים לעין */
}

/* העברת הכותרות (Labels) אל מעל תיבות הטקסט ויישורן לימין */
.label-wrap, label, .gr-label {
    display: block !important;
    margin-bottom: 8px !important;
    text-align: right !important;
    width: 100% !important;
    font-weight: bold;
}

/* יישור הטקסט בתוך תיבות הקלט (Input) */
input, textarea, .type-text, .scroll-hide {
    direction: rtl !important;
    text-align: right !important;
}

/* עיצוב תיבות הקלט שיהיו לבנות ונקיות */
.contain, .gr-box, .gr-panel {
    background-color: white !important;
    border-radius: 10px;
    border: 1px solid #ddd !important;
}

/* יישור כפתורים */
.gr-button {
    direction: rtl !important;
}
"""


# ---- פונקציות הזדהות ----

def open_register():
    return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)


def register(username, password):
    if not username or not password:
        return gr.update(visible=True, value="❌ נא להזין שם וסיסמה"), gr.update(), gr.update()
    if len(password) < 6:
        return gr.update(visible=True, value="❌ הסיסמה חייבת להכיל לפחות 6 תווים"), gr.update(), gr.update()
    if username in USERS:
        return gr.update(visible=True, value="❌ משתמש כבר קיים"), gr.update(visible=True), gr.update(visible=False)
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    USERS[username] = hashed_pw
    save_users(USERS)
    return gr.update(visible=True, value="✅ נרשמת בהצלחה! כעת ניתן להתחבר."), gr.update(visible=False), gr.update(visible=True)


def login(username, password):
    if not username or not password:
        return "", gr.update(visible=True), gr.update(visible=False), gr.update(visible=True, value="❌ נא למלא שם וסיסמה"), ""
    if username not in USERS:
        return "", gr.update(visible=True), gr.update(visible=False), gr.update(visible=True, value="❌ משתמש לא נמצא"), ""
    ok = bcrypt.checkpw(password.encode(), USERS[username])
    if ok:
        return username, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False, value=""), f"## ברוך הבא, {username}! 👋"
    return "", gr.update(visible=True), gr.update(visible=False), gr.update(visible=True, value="❌ סיסמה שגויה"), ""


def logout():
    return "", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False, value=""), "", "", ""


# ---- פונקציות Reversed Substitution ----

def rs_encrypt(plaintext, key):
    if not plaintext: return "❌ יש להזין טקסט."
    if not key: return "❌ יש להזין מפתח."
    if not key.isalpha():
        return "❌ שגיאה: המפתח חייב להכיל רק אותיות באנגלית."
    try:
        result = reversed_substitution.encrypt(plaintext, key)
        return f"✅ ההצפנה הושלמה בהצלחה!\n\n{result}"
    except Exception as e:
        return f"❌ שגיאה: {e}"


def rs_decrypt(ciphertext, key):
    if not ciphertext: return "❌ יש להזין טקסט."
    if not key: return "❌ יש להזין מפתח."
    if not key.isalpha():
        return "❌ שגיאה: המפתח חייב להכיל רק אותיות באנגלית."
    try:
        result = reversed_substitution.decrypt(ciphertext, key)
        return f"✅ הפיענוח הושלמה בהצלחה!\n\n{result}"
    except Exception as e:
        return f"❌ שגיאה: {e}"


def rs_crack(ciphertext):
    if not ciphertext: return "❌ יש להזין טקסט."
    try:
        result = reversed_substitution.crack(ciphertext)
        return result if result else "⚠️ לא נמצאה תוצאה. נסה טקסט ארוך יותר."
    except Exception as e:
        return f"❌ שגיאה: {e}"


# ---- פונקציות Climbing Key ----

def ck_encrypt(plaintext, key):
    if not plaintext: return "❌ יש להזין טקסט."
    if key is None or not (1 <= key <= 25):
        return "❌ שגיאה: המפתח חייב להיות מספר בין 1 ל-25."
    try:
        result = climbing_key.encrypt_climbing_key(plaintext, int(key))
        return f"✅ ההצפנה הושלמה בהצלחה!\n\n{result}"
    except Exception as e:
        return f"❌ שגיאה: {e}"

def ck_decrypt(ciphertext, key):
    if not ciphertext: return "❌ יש להזין טקסט."
    if key is None or not (1 <= key <= 25):
        return "❌ שגיאה: המפתח חייב להיות מספר בין 1 ל-25."
    try:
        result = climbing_key.decrypt_climbing_key(ciphertext, int(key))
        return f"✅ הפענוח הושלם בהצלחה!\n\n{result}"
    except Exception as e:
        return f"❌ שגיאה: {e}"

def ck_crack(ciphertext):
    if not ciphertext: return "❌ יש להזין טקסט."
    try:
        return climbing_key.crack_climbing_key(ciphertext)
    except Exception as e:
        return f"❌ שגיאה: {e}"


# ---- ממשק ----

with gr.Blocks(title="מערכת הצפנה", css=css_code) as app:

    user_state = gr.State("")

    # מסך כניסה
    with gr.Column(visible=True) as login_panel:
        gr.Markdown("# 🔐 מערכת הצפנה")
        gr.Markdown("## מסך כניסה")
        username_input = gr.Textbox(label="שם משתמש")
        password_input = gr.Textbox(label="סיסמה", type="password")
        with gr.Row():
            login_btn = gr.Button("כניסה", variant="primary")
            reg_btn = gr.Button("רישום")
        err = gr.Textbox(label="הודעת מערכת", visible=False)

    # מסך רישום
    with gr.Column(visible=False) as register_panel:
        gr.Markdown("## מסך רישום")
        reg_username = gr.Textbox(label="שם משתמש חדש")
        reg_password = gr.Textbox(label="סיסמה חדשה (מינימום 6 תווים)", type="password")
        do_reg_btn = gr.Button("בצע רישום", variant="primary")
        reg_err = gr.Textbox(label="הודעת מערכת", visible=False)
        back_btn = gr.Button("חזור לכניסה", variant="secondary")

    # מסך ראשי - נראה רק אחרי התחברות
    with gr.Column(visible=False) as main_panel:
        welcome_msg = gr.Markdown()
        logout_btn = gr.Button("התנתק 👋", variant="stop")

        with gr.Tabs():

            # ---- Reversed Substitution ----
            with gr.Tab("🔠 Reversed Substitution"):
                gr.Markdown("## Reversed Substitution")
                gr.Markdown("צופן שמחליף כל אות לפי אלפבית שנבנה ממפתח מילה. המפתח הוא מילה באנגלית.")

                with gr.Tabs():
                    with gr.Tab("הצפנה"):
                        rs_enc_input = gr.Textbox(label="טקסט לא מוצפן", placeholder="הכנס טקסט...", lines=3)
                        rs_enc_key = gr.Textbox(label="מפתח (מילה באנגלית)", placeholder="לדוגמה: Hello")
                        rs_enc_btn = gr.Button("הצפן 🔐", variant="primary")
                        rs_enc_output = gr.Textbox(label="תוצאה", lines=3, interactive=False)
                        rs_enc_btn.click(rs_encrypt, inputs=[rs_enc_input, rs_enc_key], outputs=[rs_enc_output])

                    with gr.Tab("פענוח"):
                        rs_dec_input = gr.Textbox(label="טקסט מוצפן", placeholder="הכנס טקסט מוצפן...", lines=3)
                        rs_dec_key = gr.Textbox(label="מפתח (מילה באנגלית)", placeholder="לדוגמה: Hello")
                        rs_dec_btn = gr.Button("פענח 🔓", variant="primary")
                        rs_dec_output = gr.Textbox(label="תוצאה", lines=3, interactive=False)
                        rs_dec_btn.click(rs_decrypt, inputs=[rs_dec_input, rs_dec_key], outputs=[rs_dec_output])

                    with gr.Tab("פריצה"):
                        gr.Markdown("*ניסיון לפצח ללא מפתח — עובד טוב יותר על טקסט ארוך*")
                        rs_crack_input = gr.Textbox(label="טקסט מוצפן", placeholder="הכנס טקסט מוצפן...", lines=3)
                        rs_crack_btn = gr.Button("נסה לפרוץ 🔍", variant="primary")
                        rs_crack_output = gr.Textbox(label="תוצאה", lines=12, interactive=False)
                        rs_crack_btn.click(rs_crack, inputs=[rs_crack_input], outputs=[rs_crack_output])

            # ---- Climbing Key ----
            with gr.Tab("🧗 Climbing Key"):
                gr.Markdown("## Climbing Key")
                gr.Markdown("צופן שמזיז כל אות במספר עמדות שגדל בהדרגה. המפתח הוא מספר בין 1 ל-25.")

                with gr.Tabs():
                    with gr.Tab("הצפנה"):
                        ck_enc_input = gr.Textbox(label="טקסט לא מוצפן", placeholder="הכנס טקסט...", lines=3)
                        ck_enc_key = gr.Number(label="מפתח (מספר בין 1 ל-25)", value=3, precision=0)
                        ck_enc_btn = gr.Button("הצפן 🔐", variant="primary")
                        ck_enc_output = gr.Textbox(label="תוצאה", lines=3, interactive=False)
                        ck_enc_btn.click(ck_encrypt, inputs=[ck_enc_input, ck_enc_key], outputs=[ck_enc_output])

                    with gr.Tab("פענוח"):
                        ck_dec_input = gr.Textbox(label="טקסט מוצפן", placeholder="הכנס טקסט מוצפן...", lines=3)
                        ck_dec_key = gr.Number(label="מפתח (מספר בין 1 ל-25)", value=3, precision=0)
                        ck_dec_btn = gr.Button("פענח 🔓", variant="primary")
                        ck_dec_output = gr.Textbox(label="תוצאה", lines=3, interactive=False)
                        ck_dec_btn.click(ck_decrypt, inputs=[ck_dec_input, ck_dec_key], outputs=[ck_dec_output])

                    with gr.Tab("פריצה"):
                        gr.Markdown("*מנסה את כל 26 המפתחות האפשריים אוטומטית*")
                        ck_crack_input = gr.Textbox(label="טקסט מוצפן", placeholder="הכנס טקסט מוצפן...", lines=3)
                        ck_crack_btn = gr.Button("נסה לפרוץ 🔍", variant="primary")
                        ck_crack_output = gr.Textbox(label="תוצאה", lines=3, interactive=False)
                        ck_crack_btn.click(ck_crack, inputs=[ck_crack_input], outputs=[ck_crack_output])

            # ---- עזרה ----
            with gr.Tab("ℹ️ עזרה"):
                gr.Markdown("""
## אודות המערכת

---

## 🔠 Reversed Substitution

הצופן לוקח מפתח מילה, מסדר את אותיותיו בתחילת האלפבית, ואת יתר האותיות בסדר הפוך.
כל אות בהודעה מוחלפת באות המתאימה מהאלפבית החדש.

**דוגמה:** מפתח `HELLO` → האלפבית מתחיל ב־`H, E, L, O` ואחריו שאר האותיות הפוך.

**פריצה:** ניסוי כל מילה במילון כמפתח + בדיקה אם הפלט הוא אנגלית תקינה.

---

## 🧗 Climbing Key

הצופן מזיז כל אות בהודעה במספר עמדות שגדל בהדרגה.
האות הראשונה מוזזת ב־(מפתח+1), השנייה ב־(מפתח+2), וכן הלאה.

**דוגמה:** מפתח `3`, הודעה `HELLO` → H+4, E+5, L+6, L+7, O+8

**פריצה:** ניסוי כל 26 המפתחות האפשריים + בדיקת אנגלית.

---

## 📖 הוראות שימוש

1. בחר צופן מהטאבים למעלה
2. לחץ **הצפנה** — הכנס טקסט ומפתח
3. לחץ **פענוח** — הכנס טקסט מוצפן ואותו מפתח
4. לחץ **פריצה** — הכנס טקסט מוצפן בלי מפתח
                """)

    # חיבור כפתורים
    login_btn.click(fn=login, inputs=[username_input, password_input],
                    outputs=[user_state, login_panel, main_panel, err, welcome_msg])
    reg_btn.click(fn=open_register, outputs=[login_panel, register_panel, main_panel])
    do_reg_btn.click(fn=register, inputs=[reg_username, reg_password],
                     outputs=[reg_err, register_panel, login_panel])
    back_btn.click(fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
                   outputs=[login_panel, register_panel])
    logout_btn.click(fn=logout,
                     outputs=[user_state, login_panel, main_panel, err, welcome_msg, username_input, password_input])

if __name__ == "__main__":
    app.launch(share = True)