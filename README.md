# BOOKNOTES

### **Description:**
 Booknotes is a note-taking web app, specifically designed to take book notes.

### **Technologies used:**

Flask, Python, SQLite, HTML, CSS, JS, Bootstrap
 
### **Files:**
##### **application.py:**

This file controls what happends inside the app. Through the Flask framework, this file controls when and which HTML files are pulled up, as well as sends/pulls records to/from the database.

##### **booknotes.db:**

This file contains the database where the following tables are stores: users, books, and notes.

The users table contains usernames and passwords so that users can create accounts and login.

The books table contains the book titles, and connects to the user id from the users table.

The notes table contains all of the note entries. Each note entry connects to a book id from the books table.

##### **requirements.txt:**

This file contains the Python dependancies.

##### **templates:**

This folder contains all the HTML templates. There are two main layouts (layout.html and in-app-layout.html), which extends on all the other HTML files. The login and registration pages extend the layout.html, and all other pages extend the in-app-layout.html.

The login and registration forms were created using a Boostrap template.

##### **static:**

This folder contains the CSS and JS files, as well as all the image files used throughout the HTML pages.

### **User experience:**
##### **Step 1: Log in**

The user starts at the login screen (if they don't yet have an account, they can navigate directly to the registration page to create a new account). As all of the other pages (the in-app pages) do require a login, users must login before navigating anywhere else.

##### **Step 2: Start a new book**

Once the user logs in, they are now able to access the rest of the app. The first thing they will likely do is add a new book by clicking on "New Book". This will also prompt them to enter the first book entry. The user can create as many new books as they want.

##### **Step 3: View and add notes**

Once the user has officially created their first book entry, they are now able to see this entry by clicking on "Currently Reading", as their newly entered book has been added to the "Currently Reading" list. This is also the page where they can add multiple other entries for this same book, by clicking "Add Entry". All entries are stamped with the date and time it was made.

##### **Step 4: Complete a book**

Once the user has finished reading their book, they can move this book over to the "Completed" section by going to "Currently Reading" > "Complete a Book". The book as well as the entries made can now be viewed under the "Completed" section. This keeps all the books organized by completion status. A user can decide to revert a book back to "Currently Reading" at any time by going to "Completed" > "Revert a Book".

##### **Step 5: Start a wishlist**

There is also a section called "Want to Read" where the user can create a book wishlist (books that they wish to read). The user can add book titles to this list by going to "Want to Read" > "Add Book". The user can also decide to start any of these books at any time by going to "Want to Read" > "Start a Book". The user will then be prompted to add the first notes entry, and the book as well as the notes will now be accessible under "Currently Reading".

##### **Step 6: Organize and cleanup**

If at any point the user wants to delete any books for any reason, they can do so by accessing the "Delete a Book" button available under the respective categories "Currently Reading", "Completed", or "Want to Read".
