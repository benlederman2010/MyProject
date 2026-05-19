import string

PUNCT = "(){}[];,\"'!?"


def load_dictionary(dict_file_name):
    """טוען מילון מקובץ ומחזיר סט מילים באנגלית"""
    try:
        with open(dict_file_name, "r", encoding="utf-8") as file:
            dictionary = {line.strip().lower() for line in file if line.strip()}
    except FileNotFoundError:
        raise FileNotFoundError("dictionary file not found")

    if not dictionary:
        raise ValueError("dictionary is empty")

    return dictionary


def is_english(message, dictionary, X):
    """בודק האם הודעה באנגלית לפי אחוז מילים מהמילון"""
    words = message.split()
    cleaned = []

    for word in words:
        word = word.strip(PUNCT).lower()
        if word:
            cleaned.append(word)

    if not cleaned:
        raise ValueError("message contains no valid words")

    total = len(cleaned)
    english = sum(1 for w in cleaned if w in dictionary) #בודק כמה מהמילים המנוקות הן במילון
    percent = (english / total) * 100

    print(f"Total words: {total}")
    print(f"English words: {english}")
    print(f"Percent: {percent:.2f}%")

    return percent >= X


def check_is_english_for_file_messages(files_list, dict_file_name, X):
    """בודק עבור רשימת קבצים אם הם באנגלית"""
    dictionary = load_dictionary(dict_file_name)

    for file_name in files_list:
        print(f"\nChecking file: {file_name}")

        try:
            with open(file_name, "r", encoding="utf-8") as file:
                message = file.read()
        except FileNotFoundError:
            # לפי ההנחיות — לא להדפיס, אלא לזרוק חריגה
            raise FileNotFoundError(f"message file '{file_name}' not found")

        result = is_english(message, dictionary, X)
        if result:
            print("=> This file IS in English.")
        else:
            print("=> This file is NOT in English.")

#בדיקות
if __name__ == "__main__":
    files = ["QuantumShield.txt", "QuantumShield1.txt", "QuantumShield2.txt"]
    X = 50 # בחירה לדוגמא באחוז המילים באנגלית המינימלי
    check_is_english_for_file_messages(files, "dictionary.txt", X)