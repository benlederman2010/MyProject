import IsEnglish
from hack_simple_subtitution import is_english


#צריך בדיקות קצה.
def encrypt_climbing_key(text, initial_key):
    encrypted_text = ""
    position = 1


    for char in text:
        # בודקים אם התו הוא אות באנגלית (כדי לא להצפין רווחים או סימני פיסוק)
        if char.isalpha():
            shift = initial_key + position
            if char.isupper():
                # 65 זה הערך של האות A
                new_char_ascii = (ord(char) - 65 + shift) % 26 + 65
                encrypted_text += chr(new_char_ascii)
            elif char.islower():
                new_char_ascii = (ord(char) - 97 + shift) % 26 + 97
                encrypted_text += chr(new_char_ascii)

            # מקדמים את המיקום רק אם זו הייתה אות
            position += 1
        else:
            encrypted_text += char

    return encrypted_text

def decrypt_climbing_key(text, initial_key):
    decrypted_text = ""
    position = 1

    for char in text:
        if char.isalpha():
            shift = initial_key + position
            if char.isupper():
                new_char_ascii = (ord(char) - 65 - shift) % 26 + 65
                decrypted_text += chr(new_char_ascii)
            elif char.islower():
                new_char_ascii = (ord(char) - 97 - shift) % 26 + 97
                decrypted_text += chr(new_char_ascii)
            position += 1
        else:
            decrypted_text += char

    return decrypted_text


def crack_climbing_key(encrypted_text):

    try:
        dictionary = IsEnglish.load_dictionary("dictionary.txt")
    except FileNotFoundError:
        raise FileNotFoundError("Dictionary not found.")

    # מנסים את כל 26 האפשרויות למפתח
    for key in range(1, 26 + 1):
        attempt = decrypt_climbing_key(encrypted_text, key)
        if IsEnglish.is_english(attempt, dictionary, 50):
            return attempt

    return "Failed to crack"
# --- בדיקת פענוח ופריצה ---
if __name__ == "__main__":
    original_text = "Hello, my name is Ben and I love Python"
    initial_key = 3

    encrypted_text = encrypt_climbing_key(original_text, initial_key)
    decrypted_text = decrypt_climbing_key(encrypted_text, initial_key)
    print(f"Original Text: {original_text}")
    print(f"Encrypted Text: {encrypted_text}")
    print(f"Decrypted Text: {decrypted_text}")

    cracked_text = crack_climbing_key(encrypted_text)
    print(f"Cracked Text: {cracked_text}")