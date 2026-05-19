import os
import IsEnglish


def create_reversed_cipher_alphabet(keyword):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keyword = keyword.upper()

    # ניקוי המפתח מכפילויות
    clean_keyword = ""
    for char in keyword:
        if char in alphabet and char not in clean_keyword:
            clean_keyword += char

    # יצירת רשימת האותיות שנשארו והיפוכן
    remaining = ""
    for char in alphabet:
        if char not in clean_keyword:
            remaining += char

    cipher_alphabet = clean_keyword + remaining[::-1]

    # 3. יצירת המילון
    cipher_dict = {}
    for i in range(len(alphabet)):
        cipher_dict[alphabet[i]] = cipher_alphabet[i]

    return cipher_dict


def encrypt(plaintext, key):
    if not plaintext:
        return ""

    cipher_dict = create_reversed_cipher_alphabet(key)
    result = ""

    for char in plaintext:
        if char.isalpha():
            is_lower = char.islower()
            # מוצאים את האות המוצפנת (תמיד עובדים עם גדולות במילון)
            encrypted_char = cipher_dict[char.upper()]

            # אם המקור היה קטן, נהפוך את התוצאה לקטנה
            if is_lower:
                result += encrypted_char.lower()
            else:
                result += encrypted_char
        else:
            result += char

    return result


def decrypt(ciphertext, key):
    if not ciphertext:
        return ""

    # יוצרים מילון הפוך לפענוח
    forward_dict = create_reversed_cipher_alphabet(key)
    rev_dict = {}
    for k, v in forward_dict.items():
        rev_dict[v] = k

    result = ""

    for char in ciphertext:
        if char.isalpha():
            is_lower = char.islower()
            decrypted_char = rev_dict[char.upper()]

            if is_lower:
                result += decrypted_char.lower()
            else:
                result += decrypted_char
        else:
            result += char

    return result

def get_word_pattern(word):
    """הופכת מילה לתבנית מספרית (למשל HELLO -> 0-1-2-2-3)"""
    word = word.upper()
    pattern, seen, next_num = [], {}, 0
    for char in word:
        if char.isalpha():
            if char not in seen:
                seen[char] = str(next_num)
                next_num += 1
            pattern.append(seen[char])
    return "-".join(pattern)

import re


def crack(ciphertext):
    if not ciphertext:
        return "הטקסט ריק"

    dictionary = IsEnglish.load_dictionary("dictionary.txt")
    SHORT_WORDS = {"hi", "ok", "no", "go", "do", "my", "he", "me", "we", "is", "it", "in", "at", "to", "of", "or", "an",
                   "be", "by", "am"}
    dictionary = dictionary | SHORT_WORDS

    found_results = []
    seen_texts = set()

    for potential_key in dictionary:
        decrypted = decrypt(ciphertext, potential_key)

        # אם הטקסט נראה כמו אנגלית (לפחות 50% מהמילים במילון)
        if IsEnglish.is_english(decrypted, dictionary, 50):
            if decrypted not in seen_texts:
                found_results.append((potential_key, decrypted))
                seen_texts.add(decrypted)

        # עוצרים אחרי שמצאנו 4 אפשרויות כדי שהריצה לא תהיה ארוכה מדי
        if len(found_results) >= 4:
            break

    if not found_results:
        return " לא נמצאו התאמות במילון."

    # כאן הקסם - הופכים את הרשימה למחרוזת אחת יפה
    output = f" נמצאו {len(found_results)} אפשרויות פוטנציאליות:\n"
    output += "=" * 30 + "\n\n"

    for i, (key, text) in enumerate(found_results, 1):
        output += f"💡 אפשרות {i} (מפתח: {key}):\n"
        output += f"{text}\n"
        output += "-" * 30 + "\n"

    return output

if __name__ == "__main__":
    key = "Hello"
    encrypted_text = encrypt("Hello", key)
    print(crack(encrypted_text))