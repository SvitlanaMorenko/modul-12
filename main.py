from collections import UserDict
from datetime import datetime, timedelta
import pickle


class Field:
    def __init__(self, value):
        self._value = None
        self.value = value

    def __str__(self):
        return str(self.value)
    
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.validate(value)
        self._value = value

    def validate(self, value):
        pass


class Name(Field):
    pass


class Phone(Field):

    @Field.value.setter
    def value(self, value):
        super().value = value

    def validate(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError('Phone should be a 10-digit numeric string')
    
    
class Birthday(Field):
   
    @Field.value.setter
    def value(self, value: str):
        self._value = datetime.strptime(value, '%Y.%m.%d').date()


class Record:
   
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        if birthday:
            self.add_birthday(birthday)
            
    def __str__(self):
        phones_info = ', '.join(map(str, self.phones))
        birthday_info = f"Birthday: {self.birthday}, " if self.birthday else ""
        return f"Contact name: {self.name}, {birthday_info}phones: {phones_info}"
    
    def add_phone(self, phone_number: str):
        phone = Phone(phone_number)
        try:
            phone.validate(phone_number)
            if phone not in self.phones:
                self.phones.append(phone)
        except ValueError as e:
            print(f"Error adding phone {phone_number}: {e}")

    def find_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone

    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = self.find_phone(old_phone)
        if old_phone_obj:
            new_phone_obj = Phone(new_phone)
            new_phone_obj.validate(new_phone)
            if new_phone_obj not in self.phones:
                self.phones[self.phones.index(old_phone_obj)] = new_phone_obj
        else:
            raise ValueError('Phone not found')

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
        else:
            raise ValueError('Phone not found')

    def add_birthday(self, birthday):
        birthday_field = Birthday(birthday)
        self.birthday = birthday_field

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day)
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day)
            days_left = (next_birthday - today).days
            return days_left
        return None


class AddressBook(UserDict):
   
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        self.pop(name, None)

    def __iter__(self):
        return self.iterator()

    def iterator(self, n=1):
        records = list(self.data.values())
        total_records = len(records)
        num_batches = (total_records + n - 1) // n
        for batch_num in range(num_batches):
            start_idx = batch_num * n
            end_idx = (batch_num + 1) * n
            yield records[start_idx:end_idx]
            
    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print(f"File '{filename}' not found. Creating a new address book.")

    def search(self, query):
        results = []
        for record in self.data.values():
            if (
                query.lower() in record.name.value.lower()
                or any(query in phone.value for phone in record.phones)
            ):
                results.append(record)
        return results
     