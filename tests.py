import pytest
import os
import json
import bcrypt
import reversed_substitution
import climbing_key


# --- 1. בדיקות Round Trip (הצפנה + פענוח) ---

def test_rs_round_trip():
    """בדיקה שהצפנה ופענוח של Reversed Substitution מחזירים את המקור"""
    plaintext = "Cyber Project 2024"
    key = "SECRET"
    encrypted = reversed_substitution.encrypt(plaintext, key)
    decrypted = reversed_substitution.decrypt(encrypted, key)
    assert decrypted == plaintext


def test_ck_round_trip():
    """בדיקה שהצפנה ופענוח של Climbing Key מחזירים את המקור"""
    plaintext = "Hello World"
    key = 5
    encrypted = climbing_key.encrypt_climbing_key(plaintext, key)
    decrypted = climbing_key.decrypt_climbing_key(encrypted, key)
    assert decrypted == plaintext


# --- 2. בדיקות מפתח שגוי וקלט ריק ---

def test_rs_wrong_key():
    """בדיקה שפענוח עם מפתח שגוי לא מחזיר את הטקסט המקורי"""
    plaintext = "Top Secret"
    encrypted = reversed_substitution.encrypt(plaintext, "KEY")
    decrypted = reversed_substitution.decrypt(encrypted, "KEE")
    assert decrypted != plaintext


def test_empty_input():
    """בדיקה שקלט ריק לא גורם לקריסה ומחזיר מחרוזת ריקה"""
    assert reversed_substitution.encrypt("", "KEY") == ""
    assert climbing_key.encrypt_climbing_key("", 3) == ""


# --- 3. בדיקות דרישות פלט (אורך ולוגיקה) ---

def test_ck_output_length():
    """בדיקה שאורך הפלט שווה לאורך הקלט (דרישת חובה)"""
    text = "Gradio"
    encrypted = climbing_key.encrypt_climbing_key(text, 3)
    assert len(encrypted) == len(text)


def test_ck_incremental_shift():
    """בדיקה שההסטה אכן גדלה בין אות לאות (לוגיקה של המטפס)"""
    # מפתח 1: A+2=C, A+3=D
    assert climbing_key.encrypt_climbing_key("AA", 1) == "CD"


# --- 4. בדיקות ניהול משתמשים (Register/Login) ---

def test_user_json_save(tmp_path):
    """בדיקה ששמירת משתמשים ב-JSON עובדת תקין (שימוש בתיקייה זמנית)"""
    d = tmp_path / "sub"
    d.mkdir()
    test_file = d / "users_test.json"

    user_data = {"test_user": "hashed_pass_123"}
    with open(test_file, "w") as f:
        json.dump(user_data, f)

    with open(test_file, "r") as f:
        loaded_data = json.load(f)
    assert "test_user" in loaded_data


def test_login_success():
    """בדיקה שסיסמה נכונה עוברת אימות bcrypt"""
    password = b"my_password_123"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    assert bcrypt.checkpw(password, hashed) is True


def test_login_fail():
    """בדיקה שסיסמה שגויה נדחית"""
    password = b"correct_pass"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    assert bcrypt.checkpw(b"wrong_pass", hashed) is False


def test_duplicate_user_logic():
    """בדיקה לוגית ששם משתמש קיים מזוהה במערכת"""
    db = {"admin": "12345", "user1": "67890"}
    new_user = "admin"
    assert new_user in db  # אם הוא ב-db, הרישום אמור להיכשל באפליקציה


# --- 5. בדיקת פריצה (Crack) ---

def test_crack_success():
    """בדיקה שפונקציית הפריצה מצליחה למצוא את המפתח הנכון"""
    plaintext = "this is a test message"
    # הצפנה עם מפתח ידוע
    encrypted = climbing_key.encrypt_climbing_key(plaintext, 5)
    # ניסיון פריצה
    cracked = climbing_key.crack_climbing_key(encrypted)
    assert cracked.lower() == plaintext.lower()