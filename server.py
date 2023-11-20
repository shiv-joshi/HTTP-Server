import socket, json, random, datetime, hashlib, sys

# get current time for server log
def get_time():
    dt_now = datetime.datetime.now()
    year,month,day,hour,minute,second = dt_now.year,dt_now.month,dt_now.day,dt_now.hour,dt_now.minute,dt_now.second
    time = f"{year}-{month}-{day}-{hour}-{minute}-{second}"
    return time

# handle POST request for user login
def user_login(headers,conn,sessions):
    username = headers.get('username', '').rstrip('\r')
    password = headers.get('password', '').rstrip('\r')

    # if 1 or both fields missing
    if username=='' or password=='':
        time = get_time()
        print("SERVER LOG:",time,"LOGIN FAILED")
        response = "HTTP/1.0 501 Not Implemented"
        return response

    # open accounts.json as dict
    with open('accounts.json') as json_file:
        accounts = json.load(json_file)
    
    # check if username and password are valid
    valid = True
    if username in accounts:
        # check if the hashed password corresponds to the username supplied
        salt = accounts[username][1]
        hashed_password = hashlib.sha256((password+salt).encode('UTF-8')).hexdigest()

        # check if password is valid
        if hashed_password == accounts[username][0]:
            # create a cookie
            characters = '0123456789abcdefghijklmnopqrstuvwxyz'
            sessionID = ''.join(random.choices(characters, k=16))

            # create a session with cookie:username,timestamp
            sessions[sessionID] = (username,datetime.datetime.now())

            # log successful message
            time = get_time()
            print("SERVER LOG:",time,"LOGIN SUCCESSFUL:",username,":",password)

            # return HTTP response
            response = "HTTP/1.0 200 OK\r\nSet-Cookie: sessionID="+sessionID+"\r\n\r\nLogged in!"
            return response
        else:
            valid = False
    else:
        valid = False

    # if username and password not valid
    if valid == False:
        time = get_time()
        print("SERVER LOG:",time,"LOGIN FAILED:",username,":",password)
        response = "HTTP/1.0 200 OK\r\n\r\nLogin failed!"
        return response

# checks if file exists
def is_file(path):
    try:
        with open(path, 'r'):
            pass
        return True
    except FileNotFoundError:
        return False

# handle GET request file downloads
def get(headers,sessions,timeout,root,target):
    cookie = headers.get('Cookie', '').rstrip('\r')
    
    if cookie == '': 
        response = "HTTP/1.0 401 Unauthorized"
        return response
    else:
        cookie = cookie[10:]

    # check if sessionID cookie exists
    if cookie in sessions.keys():
        user = sessions[cookie][0]
        timestamp = sessions[cookie][1]

        # check if the session timed out
        if datetime.datetime.now() <= timestamp + datetime.timedelta(seconds=int(timeout)):
            # update time on cookie
            sessions[cookie] = (user,datetime.datetime.now())

            # if file exists
            path = f"{root}{user}{target}"
            if is_file(path):
                time = get_time()
                print("SERVER LOG:",time,f"GET SUCCEEDED: {user} : {target}")

                # get contents of file
                with open(path) as f:
                    s = f.read()
                    print(s)
                response = f"HTTP/1.0 200 OK\r\n\r\n{s}"
                return response
            else:
                time = get_time()
                print("SERVER LOG:",time,f"GET FAILED: {user} : {target}")
                response = "HTTP/1.0 404 NOT FOUND"
                return response
        else:
            # delete expired cookie
            del sessions[cookie]

            # send response
            time = get_time()
            print("SERVER LOG:",time,f"SESSION EXPIRED: {user} : {target}")
            response = "HTTP/1.0 401 Unauthorized"
            return response
    else:
        time = get_time()
        print("SERVER LOG:",time,f"COOKIE INVALID: {target}")
        response = "HTTP/1.0 401 Unauthorized"
        return response

# start the server
def start_server(ip, port, accounts_file, timeout, root, sessions):
    # create and bind TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))

    # listen for incoming connections
    sock.listen(0)

    while True:
        # accepts new connection and creates new socket to talk to client
        conn, addr = sock.accept()

        # recieve HTTP request from client
        req = conn.recv(1024).decode()

        # parse HTTP message
        req = str.replace(req, '\n', '\r\n')
        lines = req.split("\r\n")
        start_line = lines[0]
        method,target,version = start_line.split(" ")
        headers = {}
        for header in lines[1:]:
            if header == "\r": continue
            if header == "": break #reached body
            hkey,hval = header.split(": ",1)
            headers[hkey] = hval

        # redirect 
        if method == "POST" and target == "/":
            response = user_login(headers,conn,sessions)
            conn.sendall(response.encode())
        elif method == "GET":
            response = get(headers,sessions,timeout,root,target)
            conn.sendall(response.encode())
        else:
            response = "HTTP/1.0 501 Not Implemented\r\n\r\nLOGIN FAILED"
            conn.sendall(response.encode())
        conn.close()

# main function
def main():
    # read from command line
    ip = sys.argv[1]
    port = int(sys.argv[2])
    accounts_file = sys.argv[3]
    timeout = sys.argv[4]
    root = sys.argv[5]

    # call start_server and pass in args
    sessions = {}
    start_server(ip, port, accounts_file, timeout, root, sessions)

if __name__ == "__main__":
    main()

'''
python3 server.py [IP] [PORT] [ACCOUNTS_FILE] [SESSION_TIMEOUT] [ROOT_DIRECTORY]
Example: python3 server.py 127.0.0.1 8080 accounts.json 5 accounts/
● IP: The IP address on which the server will bind to.
● PORT: The port on which the server will listen for incoming connections.
● ACCOUNTS_FILE: A JSON file containing user accounts and their hashed passwords
along with the corresponding salt.
● SESSION_TIMEOUT: The session timeout duration (in seconds).
● ROOT_DIRECTORY: The root directory containing user directories
'''