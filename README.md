# Tree_Message_Board

# Login Example

This sample app demonstrates a simple login system that allows users to
register, log in, and view pages specific to their user role. Those pages don't
really do anything: it's just a simplified example to share some basic tools
and techniques you might need when building a real-world login system.

There are three user roles in this system:
- **User**
- **Staff**
- **Admin**

Anyone who registers via the app will be a **User**. The only way to create
**Staff** or **Admin** accounts in this simple app is to insert them directly
into the database. Hey, we didn't say this app was complete!

## Getting this Example Running

To run the example yourself, you'll need to:

1. Open the project in Visual Studio Code.
2. Create yourself a virtual environment.
3. Install all of the packages listed in requirements.txt (Visual Studio will
   offer to do this for you during step 2).
4. Use the [Database Creation Script](<Create Database.sql>) to create your own
   copy of the **loginexample** database.
5. Use the [Database Population Script](<Populate Database.sql>) to populate
   the **loginexample** ***users*** table with example users.
6. Modify [connect.py](loginapp/connect.py) with the connection details for
   your local database server.
7. Run [The Python/Flask application](run.py).

At that point, you should be able to register yourself a new **user** account
or log in using one of the **user**, **staff**, or **admin** accounts listed in
the [Database Population Script](<Populate Database.sql>).

Enjoy!

## Database Scripts

While we're talking about the database, you should take a look at:
- [MySQL script to create the necessary database](<Create Database.sql>)
- [MySQL script to populate the database with users](<Populate Database.sql>)
- [Python script to create password hashes](password_hash_generator.py)

What's that third one? Well, for that we need to talk about...

## Passwords

One of the key things about this login system is that it doesn't actually store
users' passwords in the database. That may lead you to ask...

### Why not store passwords?
People tend to re-use passwords across multiple websites, no matter how much
security experts might tell them not to. That means if someone gets access to
your database, containing a whole lot of users' passwords and other details
like names or email addresses, they can use those passwords to compromise
your users' accounts with other services (like their email, or bank account).

### How do you handle registration and login without storing passwords?

Easy! Well, sort of. It goes like this:

1. When the user first gives us a password during registration, we pass it
   through a cryptographic "hash" function: a one-way mathematical operation
   that transforms the original password into its corresponding "hash value"
   or "hash". The same password always results in the same hash.
   
2. We throw away the original password, and just keep the hash.
   
3. The hash value is useless to an attacker: because the hash-function is
   one-way, anyone who steals our database of user accounts can't work out
   what the users' passwords are. Well, okay, there are clever ways around
   that. Look up "rainbow tables" if you're interested. Read Cory Doctorow's
   "Knights of the Rainbow Table" if you're *really* interested. But it takes
   a whole lot more time and computing power for an attacker to get a user's
   password back from its hash than it does to just read the plain password
   straight out of your database.

4. When a user tries to log in, we take the password they supplied us, run it
   through the exact same hash function, and then compare the hash to the one
   we have on file. Because the same password will always produce the same
   hash, if the two hashes match then the passwords must match! Again, kinda.
   It's possible, though very unlikely, that two passwords may produce the
   same hash value. In that case, you'd be able to log in using either
   password. These kinds of "hash collisions" are extremely rare, though. Rare
   enough that we won't worry about that here.

So, in short:
1. The user gives us a password.
2. We put that password though a one-way hashing algorithm to get its "hash".
3. We store the hash, **not** the password.
4. During login, we put the supplied password through the same algorithm.
5. If the hash of the supplied password matches the hash of the user's original
   password that we stored in step 3, then we know the user has supplied the
   correct password... without having to know their password at all.

Cool, huh?

### Salting Passwords

Remember how we mentioned that it's technically possible for an attacker to
work out a user's original password from its hash, just expensive? Well, it's
actually not expensive at all if you just pre-calculate one of those "rainbow
tables": essentially a giant table mapping hash values back to passwords. It
takes time to generate something like that, and the tables are absolutely huge,
but storage is pretty cheap these days and you only have to generate the table
once per hash algorithm. Once someone has a rainbow table for a particular
algorithm, translating hashes back to passwords is just a simple lookup.

The contemporary solution to this is to add a "salt" to each password before
you hash it. The salt is just some random string. It doesn't have to be secret,
necessarily, just specific to your app (like we do here) or, ideally, specific
to each password. Adding a salt to your passwords totally breaks the whole
"rainbow table" approach: an attacker can't just use an off-the-shelf table
any more: they need to generate one specific to *your application's salt*. In
the ideal scenario, if you're using per-password salts, an attacker would have
to generate one of those giant tables to break *each individual password* in
your database.

### How exactly do we do all this?

With the flask_hashing library (which is really just a wrapper for Python's
hashlib) and a couple lines of code.

If you take a look at the [database creation script](<Create Database.sql>),
you'll see that instead of a "password" field to store the password, we have a
"password_hash" field that stores exactly 64 characters.

By default, the flask_hashing library uses the SHA-256 hashing algorithm. The
"256" means those hashes are 256 bits in length, or 32 bytes. This is true
regardless of password length: whether your password is 8 or 80 characters
long, you're still getting a 32-byte hash. Those 32 raw bytes will contain all
sorts of "non-printable" characters, though, so flask_hashing gives us the
hash value neatly encoded in hexadecimal (you know, those strings made up of
0-9 and A-F). In hexadecimal, or "hex", each byte is represented by two
characters. That's probably worth reading up on at some point in future, but
we won't cover that here. Point is, a 32 byte hash comes out as 64 characters
in hexadecimal... and that's why we have a CHAR(64) field in the database for
each password hash.

If this sounds terrifyingly complicated, don't worry. Take a look at the
[Hash generator Python script](password_hash_generator.py) for an example of
how to create the hashes (literally one line of code) and check a password
against a hash (again, one line of code).
