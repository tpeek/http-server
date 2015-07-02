Authors:
-Tyler Peek
-Wesley Wooten

# http-server
A simple HTTP server implemented in Python.


Summary:
This is a server that takes in requests and returns valid HTTP responses. If the requested resourse is a file and it exists, the server will return its content in the body of the response. If it is a directory and it exists, it return  a simple HTML listing of that directory as the body. If the request is invalid or the requested resource does not exist, an appropriate HTTP Error page will be shown.
