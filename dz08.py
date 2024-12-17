import pickle
from datetime import datetime, timedelta
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def change_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                self.phones.remove(phone)
                self.phones.append(Phone(new_phone))
                return
        raise ValueError("Old phone number not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                days = record.days_to_birthday()
                if days is not None and 0 <= days <= 7:
                    next_birthday = today + timedelta(days=days)
                    if next_birthday.weekday() in [5, 6]:
                        next_birthday += timedelta(days=(7 - next_birthday.weekday()))
                    upcoming.append({"name": record.name.value, "birthday": next_birthday.strftime("%d.%m.%Y")})
        return upcoming

# Functions for serialization/deserialization
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Return a new address book if the file doesn't exist

# Decorator for error handling
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, IndexError) as e:
            return f"Error: {e}"
    return wrapper

# Handlers
@input_error
def add_birthday(args, book):
    name, birthday = args[0], args[1]
    if name in book:
        book[name].add_birthday(birthday)
        return f"Birthday for {name} added."
    return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    if name in book and book[name].birthday:
        return f"{name}'s birthday: {book[name].birthday.value.strftime('%d.%m.%Y')}"
    return "Birthday not found for this contact."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join([f"{entry['name']}: {entry['birthday']}" for entry in upcoming])

@input_error
def add_contact(args, book):
    name, phone = args[0], args[1]
    if name in book:
        book[name].add_phone(phone)
        return f"Phone number added to {name}."
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return f"Contact {name} added."

@input_error
def change_phone(args, book):
    name, old_phone, new_phone = args[0], args[1], args[2]
    if name in book:
        book[name].change_phone(old_phone, new_phone)
        return f"Phone number for {name} updated."
    return "Contact not found."

@input_error
def show_phone(args, book):
    name = args[0]
    if name in book:
        return f"{name}'s phones: {', '.join([phone.value for phone in book[name].phones])}"
    return "Contact not found."

def show_all(args, book):
    if not book:
        return "No contacts found."
    return "\n".join([f"{name}: {', '.join([phone.value for phone in record.phones])}" for name, record in book.items()])

def parse_input(user_input):
    parts = user_input.strip().split()
    command = parts[0]
    args = parts[1:]
    return command, args

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    commands = {
        "add": add_contact,
        "change": change_phone,
        "phone": show_phone,
        "all": show_all,
        "add-birthday": add_birthday,
        "show-birthday": show_birthday,
        "birthdays": birthdays,
    }

    try:
        while True:
            user_input = input("Enter a command: ")
            command, args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break
            elif command == "hello":
                print("How can I help you?")
            elif command in commands:
                print(commands[command](args, book))
            else:
                print("Invalid command.")
    finally:
        save_data(book)

if __name__ == "__main__":
    main()
