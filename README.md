# HTTP-Server

I created a small HTTP server that provides user authentication and supports
returning contents of files. Users can log in with a username and password, and upon
successful authentication, they can query the contents of files from the users directory. The
server is designed to use cookies to manage user sessions and to ensure the security of file
retrieval.

# Server Functionality 
User Authentication:
  - Users can log in with a username and password.
  - Passwords are stored as SHA-256 salted-hashed values in an “accounts.json” file.
  - Successful logins are authenticated by hashing the plaintext password with the salt stored in “accounts.json”.
  - User sessions are tracked using a cookie with a timeout.
  - Multiple users can be logged in at the same time.
    
File Download:
  - Authenticated users can view the contents of files from a specified directory.
  - File access is restricted to the authenticated users directory only.
  - Unauthorized access to files is denied.
    
Session Management:
  - User sessions are managed using randomly generated session IDs stored as a cookie.
  - Sessions expire after a configurable timeout period.
