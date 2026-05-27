import json
import os

# 1. Classes and Objects
class Contact:
    """Represents a single contact."""
    def __init__(self, name, phone, email):
        self.name = name
        self.phone = phone
        self.email = email

    def to_dict(self):
        """Converts the object to a dictionary for JSON serialization."""
        return {"name": self.name, "phone": self.phone, "email": self.email}

class ContactBook:
    """Manages a collection of contacts and handles File I/O."""
    def __init__(self, filename="contacts.json"):
        self.filename = filename
        self.contacts = []
        self.load_contacts()

    def add_contact(self, contact):
        self.contacts.append(contact)
        print(f"Contact '{contact.name}' added successfully!")
        self.save_contacts()

    # 2. File I/O & 3. Exception Handling (try/except/finally)
    def save_contacts(self):
        """Saves the list of contacts to a JSON file."""
        try:
            # Using 'with' is best practice, but we add try/except/finally to demonstrate robust handling
            with open(self.filename, 'w') as file:
                data = [contact.to_dict() for contact in self.contacts]
                json.dump(data, file, indent=4)
        except IOError as e:
            print(f"File System Error: Could not save contacts. Details: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during saving: {e}")
        finally:
            print("[System] Save operation concluded.")

    def load_contacts(self):
        """Loads contacts from a JSON file."""
        try:
            with open(self.filename, 'r') as file:
                data = json.load(file)
                self.contacts = [Contact(**item) for item in data]
                print(f"Successfully loaded {len(self.contacts)} contacts.")
        except FileNotFoundError:
            print("Notice: 'contacts.json' not found. Starting with an empty contact book.")
        except json.JSONDecodeError:
            print("Error: 'contacts.json' is corrupted. Starting fresh.")
            self.contacts = []
        finally:
            print("[System] Load operation concluded.")

    def display_contacts(self):
        """Displays all saved contacts."""
        if not self.contacts:
            print("Your contact book is currently empty.")
        else:
            print("\n--- Current Contacts ---")
            for idx, contact in enumerate(self.contacts, 1):
                print(f"{idx}. {contact.name} | Phone: {contact.phone} | Email: {contact.email}")
            print("------------------------\n")

# --- Main Execution ---
if __name__ == "__main__":
    # Initialize the Contact Book (This will trigger load_contacts)
    my_book = ContactBook()
    
    # Simulating data entry
    c1 = Contact("Ayush Turak", "9876543210", "ayush@example.com")
    c2 = Contact("Minal Patil", "0123456789", "minal.patil@example.com")
    
    # Adding contacts (This will trigger save_contacts)
    print("\nAdding new contacts...")
    my_book.add_contact(c1)
    my_book.add_contact(c2)
    
    # Displaying the final result
    my_book.display_contacts()

