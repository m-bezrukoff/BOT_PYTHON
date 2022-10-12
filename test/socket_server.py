import socket

#Create a TCP server socket
#(AF_INET is used for IPv4 protocols)
#(SOCK_STREAM is used for TCP)

serverPort = 50997
# serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# print("hostname is: "), gethostname()
print("hostname is: "), socket.gethostname()

serverSocket.bind(('', serverPort))
serverSocket.listen(1)      # Listen to at most 1 connection at a time

while True:
    print("Ready to serve...")

    # Set up a new connection from the client
    connectionSocket, addr = serverSocket.accept()

    try:
        # Receives the request message from the client
        message = connectionSocket.recv(1024)
        print("Message is: "), message

        filename = message.split()[1]
        print("File name is: "), filename

        f = open(filename[1:])

        outputdata = f.read()
        connectionSocket.send(bytes('HTTP/1.1 200 OK\r\n\r\n', 'UTF-8'))

        for i in range(0, len(outputdata)):
            connectionSocket.send(bytes(outputdata[i], 'UTF-8'))
        connectionSocket.send(bytes('\r\n', 'UTF-8'))

        # Close the client connection socket
        connectionSocket.close()

    except IOError:
        # Send HTTP response message for file not found
        connectionSocket.send(bytes('HTTP/1.1 404 Not Found\r\n\r\n', 'UTF-8'))
        connectionSocket.send(bytes('<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n', 'UTF-8'))
        # Close the client connection socket
        connectionSocket.close()

        serverSocket.close()
