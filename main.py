# Import libraries and modules
import sqlite3
import os
import sys
import time
from tabulate import tabulate


# Variables
DATABASE = "DATA/ebookstore.db"
WAIT = 1
VERSION = 0.2


# Main menu of Book Manager
def main_menu():
    while True:

        loading_screen()

        clear()

        option = input(f"""
Book Manager v{VERSION} (CLI)
-----------------------
Choose an option from below:
----------------------------
1 - Enter a book
2 - Update a book
3 - Delete a book
4 - Search books
5 - View all books

0 - Exit
: """)

        if option == "1":
            clear()
            enter_book()

        elif option == "2":
            clear()
            update_book()

        elif option == "3":
            clear()
            delete_book()

        elif option == "4":
            clear()
            search_book()

        elif option == "5":
            clear()
            view_all("yes")

        elif option == "0":
            clear()
            print("\n--- Thank you for using Book Manager ---")
            print("\n--- Exiting application. Goodbye. ---\n")
            exit()

        else:
            clear()
            print("""
--- Invalid Selection. Enter an option between 1 - 5 or 0 to Exit ---""")
            time.sleep(WAIT * 1.5)


# Call to enter a new book
def enter_book():
    print("\n------- Enter Book -------\n")
    try:
        # Connect to database, create cursor object and check if ID exists
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        while True:
            print("Enter the following information of the new book or" +
                  "\n0 to return to the Main Menu:\n")

            id_code = input("ID (eg.1234): ")
            if id_code == '0':
                print("\n--- Returning to Main Menu ---")
                return

            # Verify ID
            cursor.execute("SELECT id FROM book WHERE id = ?", (id_code,))
            existing_id = cursor.fetchone()

            if existing_id:
                print("\n--- ID Code already exists. Try again. ---\n")
                continue

            # Check that user's ID is a number with 4-digits
            while not id_code.isdigit() or len(id_code) != 4:
                id_code = input("""
--- ID Code needs to consist of 4 whole numbers. Try again. ---

ID (eg.1234): """)

            # Check that user inputs is not empty
            title = input("\nTitle: ").title()
            while not title.strip():
                title = input("""
--- Title cannot be 'empty'. Enter a valid input. ---

Title: """).title()

            author = input("\nAuthor: ").title()
            while not author.strip():
                author = input("""
--- Author cannot be 'empty'. Enter a valid input. ----

Author: """).title()

            # Check if title and author is the same, might be duplicate entry
            cursor.execute(
                "SELECT * FROM book WHERE title = ? AND author = ?",
                (title, author))
            existing_book = cursor.fetchone()
            if existing_book:
                print("\n--- A book with the same Title and Author" +
                      " already exists. Try again. ---\n")
                continue

            # Check that user input is positive number
            quantity = input("\nQuantity: ")
            while not quantity.isdigit() or int(quantity) < 0:
                quantity = input("""
--- Quantity needs to be a positive whole number. Enter a valid input. ---

Quantity: """)

            # Connect to database, create cursor object and insert data
            connection = sqlite3.connect(DATABASE)
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO book (id, title, author, qty) VALUES (?, ?, ?, ?)
            """, (id_code, title, author, quantity))

            # Commit changes and close cursor object and connection
            connection.commit()
            cursor.close()
            connection.close()
            print("\n--- Book added successfully. ---\n")
            time.sleep(WAIT * .7)
            return

    except sqlite3.Error as sqe:
        print(f"\n--- Error occurred while adding the book: {sqe} ---")
        connection.rollback()
        return

    except Exception as e:
        print(f"\n--- Error: {e} ---")
        return


# Call to update an existing book
def update_book():
    print("\n------- Update Book -------")
    try:
        # Connect to database and create cursor object
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        view_all("no")

        # Verify ID and fetch record with ID
        while True:
            id_code = input(
                "\nEnter a book ID to update or 0 to return to Main Menu: ")
            if id_code == "0" or id_code.strip() == "":
                print("\n--- Returning to Main Menu ---")
                return

            # Search record with ID
            cursor.execute("SELECT * FROM book WHERE id = ?", (id_code,))
            book = cursor.fetchone()

            if not book:
                print(f"\n--- Book with ID '{id_code}' does not exist. "
                      "Please enter a valid ID. ---")
                continue

            clear()
            print("\nSelected Record:\n----------------\n")
            record = [list(book)]
            print(tabulate(record, headers=['ID', 'Title', 'Author',
                                            'Quantity'], tablefmt='presto'))
            while True:
                option = input("""
Choose an option to update:
---------------------------
1 - Title
2 - Author
3 - Quantity

0 - Return to Main Menu
: """)
                if option == "1":
                    clear()
                    title = input(f"""
Enter new 'Title' or press Enter to leave unchanged:
--------------------------------------------------
Title    : {book[1]}
New Title: """)

                    if title.strip() == "":
                        print("\n--- Book Title unchanged. ---")
                        return

                    else:
                        # Update the book in the database
                        cursor.execute("""
                            UPDATE book SET title=?, author=?, qty=?
                            WHERE id=?""", (title, book[2], book[3], id_code))

                        # Commit changes, close cursor and connection
                        connection.commit()
                        cursor.close()
                        connection.close()
                        print("\n--- Book successfully updated. ---")
                        return

                elif option == "2":
                    clear()
                    author = input(f"""
Enter new 'Author' or press Enter to leave unchanged:
-----------------------------------------------------
Author    : {book[2]}
New Author: """)

                    if author.strip() == "":
                        print("\n--- Book Author unchanged. ---")
                        return

                    else:
                        # Update the book in the database
                        cursor.execute("""
                            UPDATE book SET title=?, author=?, qty=?
                            WHERE id=?""", (book[1], author, book[3], id_code))

                        # Commit changes, close cursor and connection
                        connection.commit()
                        cursor.close()
                        connection.close()
                        print("\n--- Book successfully updated. ---")
                        return

                elif option == "3":
                    while True:
                        clear()
                        quantity = input(f"""
Enter the new 'Quantity' or press Enter to leave unchanged:
-----------------------------------------------------------
Quantity    : {book[3]}
New Quantity: """)
                        # Check if quantity must be remain the same
                        if quantity.strip() == "":
                            print("\n--- Book quantity unchanged. ---")
                            return

                        # Check if quantity is valid number
                        elif quantity.isdigit() is False or int(quantity) < 0:
                            print("""
--- Quantity needs to be a positive number. Please try again. ---""")
                            time.sleep(WAIT * 2)
                            continue

                        else:
                            # Update the book in the database
                            cursor.execute("""
                                UPDATE book SET title=?, author=?, qty=?
                                WHERE id=?""", (book[1], book[2], quantity,
                                                id_code))

                            # Commit changes, close cursor and connection
                            connection.commit()
                            cursor.close()
                            connection.close()
                            print("\n--- Book successfully updated. ---")
                            return

                elif option == "0":
                    print("\n--- Returning to Main Menu ---")
                    return

                else:
                    print("\n--- Invalid Option. Try Again. ---")

    except sqlite3.Error as sqe:
        print(f"\n--- Error occurred while updating the book: {sqe} ---")
        connection.rollback()
        return

    except Exception as e:
        print(f"\n --- Error: {e} ---")
        return


# Call to delete an existing book
def delete_book():
    print("\n------- Delete Book -------")
    try:
        # Connect to database, create cursor object and get all books
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        view_all("no")

        # Valid ID and delete record
        while True:
            id_code = input("\nEnter the ID of the book to delete or "
                            "Enter 0 to return to the Main Menu: ")
            if id_code == "0":
                print("\n--- Returning to Main Menu ---")
                return
            cursor.execute("SELECT * FROM book WHERE id=?", (id_code,))
            book = cursor.fetchone()

            if not book:
                print("\n--- No book found with the given ID. ---")
            else:
                break

        clear()
        print("\nSelected Record:\n----------------\n")
        record = [list(book)]
        print(tabulate(record, headers=['ID', 'Title', 'Author', 'Quantity'],
                       tablefmt='presto'))

        while True:
            # Confirm deletion
            confirm = input("""
Are you sure you want to delete:
--------------------------------
(Yes/ No): """).lower()

            # If invalid inputs are received
            if confirm not in ["no", "n", "yes", "y"]:
                print("\n--- Invalid input. Try again. ---")
                continue

            # Cancel deletion
            if confirm in ["no", "n"]:
                cursor.close()
                connection.close()
                print("\n--- Deletion cancelled. Returning to Main Menu ---")
                return

            # Delete record from database
            elif confirm in ["yes", "y"]:
                cursor.execute("""
                    DELETE FROM book WHERE id=?
                """, (id_code,))

                # Commit changes, close cursor and connection
                connection.commit()
                cursor.close()
                connection.close()
                print("\n--- Book record deleted successfully. ---")
                return

    except sqlite3.Error as sqe:
        print(f"\n--- Error occurred while deleting the book: {sqe}---")
        connection.rollback()
        return

    except Exception as e:
        print(f"\n--- Error: {e} ---")
        return


# Call to search for a book
def search_book():
    print("\n------- Search Book -------")

    view_all("no")

    while True:
        option = input("""
Search books by:
----------------
1 - ID
2 - Title
3 - Author

0 - Return to Main Menu
: """)

        # ID option
        if option == '1':
            id_code = input("\nEnter the ID or partial ID of the book or"
                            " '-1' to return: ")
            if id_code == '-1':
                continue
            search_books("id", id_code)

        # Title option
        elif option == '2':
            title = input(
                "\nEnter the Title or keyword of the book or '-1' to return: ")
            if title == '-1':
                continue
            search_books("title", title)

        # Author option
        elif option == '3':
            author = input(
                "\nEnter the Author or keyword of the book or \
                '-1' to return: ")
            if author == '-1':
                continue
            search_books("author", author)

        elif option == '0':
            print("\n--- Returning to Main Menu ---")
            return

        else:
            print("""\n--- Invalid option. Please enter a number" + \
                    " between 1 - 3 or 0 to return to Main Menu ---""")


# Call to search user given criteria
def search_books(criteria, value):
    try:
        # Connect to database and create cursor object
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        # Search for books based on the given criteria
        cursor.execute(f"SELECT * FROM book WHERE {criteria} LIKE ?",
                       (f"%{value}%",))
        books = cursor.fetchall()

        # Check if keyword are valid and print books
        if not books:
            print("\n--- No books found matching the search criteria. ---")
        else:
            books_formatted = \
                [(book[0], book[1], book[2], book[3]) for book in books]
            print("\nBook(s) found:\n--------------\n")
            print(tabulate(
                books_formatted, headers=['ID', 'Title', 'Author', 'Quantity'],
                tablefmt='presto'))

    except sqlite3.Error as sqe:
        print(f"\n--- Error: {sqe}---")
        connection.rollback()
        return

    finally:
        # Close cursor, connection and return to main menu
        cursor.close()
        connection.close()
        return


def view_all(menu_option):
    try:
        # Connect to database and create cursor object
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        # Get all books
        cursor.execute("SELECT * FROM book")
        books = cursor.fetchall()

        # Check if books is not empty
        if not books:
            print("\n--- No books available to view. ---")
            return

        # Show all books
        print("\nAll book records:\n-----------------\n")
        print(tabulate(books, headers=['ID', 'Title', 'Author', 'Quantity'],
                       tablefmt="presto"))

    except sqlite3.Error as sqe:
        print(f"\n--- Error: {sqe} ---")
        connection.rollback()
        return

    finally:
        cursor.close()
        connection.close()

        if menu_option == "yes":
            input("\nPress Enter to return to Main Menu. ")
            print("\n--- Returning to Main Menu ---")
            main_menu()


# Call to initialize database
def initialize():
    try:
        # Create folder for database
        if not os.path.isdir("DATA"):
            os.mkdir("DATA")

        # Check if database exists otherwise create it
        if not os.path.exists(DATABASE):
            # Connect to database and create cursor object
            connection = sqlite3.connect(DATABASE)
            cursor = connection.cursor()

            # Create book table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS book
                (id INTEGER(4) PRIMARY KEY,
                 title TEXT,
                 author TEXT,
                 qty INTEGER)
            """)

            # Insert data into book table
            cursor.executemany(
                """
                INSERT INTO book (id, title, author, qty)
                VALUES(?, ?, ?, ?)
                """,
                [
                    (3001, "A Tale Of Two Cities", "Charles Dickens", 30),
                    (3002, "Harry Potter and the Philosopher's Stone", "J.K." +
                     " Rowling", 40),
                    (3003, "The Lion, the Witch and the Wardrobe", "C.S." +
                     "Lewis", 25),
                    (3004, "The Lord of the Rings", "J.R.R. Tolkien", 37),
                    (3005, "Alice in Wonderland", "Lewis Carroll", 12)
                ]
            )

            # Commit changes, close cursor and connection
            connection.commit()
            cursor.close()
            connection.close()
            print("\n--- Database initialized successfully. ---")
            return

    except sqlite3.Error as sqe:
        print(f"\n--- Error: {sqe} ---")
        connection.rollback()
        return

    except Exception as e:
        print(f"\n--- Error: {e} ---")
        return


# Call to clear terminal
def clear():
    os.system("cls" if os.name == "nt" else "clear")


# Call to load screen
def loading_screen(animation_speed=0.05):
    print()
    chars = "/—\|"
    # Calculate number of iterations per character
    num_iterations = int(1 / (len(chars) * animation_speed))
    for i in range(num_iterations):
        for char in chars:
            sys.stdout.write(f"\r{char} ")
            sys.stdout.flush()
            time.sleep(animation_speed)
    sys.stdout.write("\r")
    sys.stdout.flush()


if __name__ == "__main__":
    initialize()
    main_menu()


# References:
# https://pypi.org/project/tabulate/
# https://stackoverflow.com/questions/8933237/how-do-i-check-if-a-directory-exists-in-python
# https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-fetchall.html
# https://stackoverflow.com/questions/6470428/how-to-catch-multiple-exceptions-in-one-line-in-the-except-block
# https://stackoverflow.com/questions/5504340/python-mysqldb-connection-close-vs-cursor-close
# https://stackoverflow.com/questions/28059975/sqlite-select-from-where-column-contains-string
# https://stackoverflow.com/questions/517970/how-can-i-clear-the-interpreter-console
# https://stackoverflow.com/questions/22029562/python-how-to-make-simple-animated-loading-while-process-is-running
