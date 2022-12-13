# BOOKNOTES
### Video Demo:  <https://youtu.be/FRaYRQYX2VM>
### Description:

#### **Files:**
##### **Overview:**

 Booknotes is a note-taking web app, specifically designed to take book reading notes.

##### **Inspiration:**

 As someone who reads a lot of self-development books, yet oftentimes forgets important information I read, I wanted a system where I could store notes on what I read. I usually store my notes all over the place, whether it be on my phone, in journals, on sticky notes, and it's justt not an efficient system. Therefore, I thought a note-taking app would be a great solution.

 ##### **Technologies used:**

 I decided to create my app using Flask.

##### **application.py:**

This file controls what happends inside the app, the "program" piece. Through the Flask framework, this file calls up the right HTML template files to use and when, as well as sends/pulls records to/from the database.

##### **booknotes.db:**

This file contains the database where the following tables are stores: users, books, and notes.

The users table contains username and passwords so that users can create accounts and login.

The books table contains the book titles, and connects to the user id from the users table.

The notes table contains all of the notes entries. Each note entry connects to a book id from the books table.

##### **requirements.txt:**

This file contains the Python dependancies.

##### **templates:**

This folder contains all the HTML templates. There are two main layouts (layout.html and in-app-layout.html), which extends on all the other HTML files. The login and registration pages extend the layout.html, and all other pages extend the in-app-layout.html.

The login and registration forms were created using a Boostrap template.

As I already had an idea of the design for the in-app pages, I have created those from scratch.

##### **static:**

This folder contains the CSS and JS files, as well as all the image files used throughout the HTML pages.

#### **User experience:**
##### **Step 1: Log in**

The user starts their journey at the login/regsitration screen. As all of the other pages (the in-app pages) do require a login, users must login before navigating anywhere else.

##### **Step 2: Start a new book**

Once the user logs in, they are now able to access the rest of the app. The first thing they will likely do is add a new book by clicking on "New Book". This will also prompt them to enter the first book entry. The user can create as many new books as they want.

##### **Step 3: View and add notes**

Once the user has officially created their first book entry, they are now able to see this entry by clicking on "Currently Reading", as their newly entered book has been added to the "Currently Reading" list. This is also the page where they can add multiple other entries for this same book, by clicking "Add Entry". All entries are stampes with the date and time when it was made.

##### **Step 4: Complete a book**

Once the user has finished reading their book, they can move this book over to the "Completed" section by going to "Currently Reading" > "Complete a Book". The book as well as the entries made can now be viewed under the "Completed" section. This keeps all the books organized by completion status. A user can decide to revert a book back to "Currently Reading" anytime by going to "Completed" > "Revert a Book".

##### **Step 5: Start a wishlist**

There is also a section called "Want to Read" where the user can create a book wishlist (books that they wish to read). The user can add book titles to this list by going to "Want to Read" > "Add Book". The user can also decide to start any of these books at any time by going to "Want to Read" > "Start a Book". The user will then be prompted to add the first notes entry, and the book as well as the notes will now be accessible under "Currently Reading".

##### **Step 6: Organize and cleanup**

If at any point the user wants to delete any books for any reason, they can do so by accessing the "Delete a Book" button available under the respective categorie ("Currently Reading", "Completed", or "Want to Read").

#### **Challenges:**
##### **Duplicate book entries causing database issues:**

One of the main challenges I encountered was when testing the app, I noticed that if two books in the database had the same title, it would cause issues in the database records. Whenever a book needed to be updated (whether notes added, book completed, book deleted, etc.) the SQL query would affect all records with the same book title. To prevent this from happening, I added error-checking that only allows each user to create unique book names (duplicates per user are not allowed).

##### **Wrong date/time format:**

Another challenge I encountered was that whenever a user would add a notes entry, the datetime function would print out the wrong time (3 hours behind I believe it was). After some research, some trial and error, and some testing, the solution I decided to implement was to put the datetime function's output through a formula that sets the time back to the correct time.

