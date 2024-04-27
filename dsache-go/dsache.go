package main

import (
	"bytes"
	"fmt"
	"net"
	"os"
)

func main() {
        fmt.Println("Server Running...")
        server, err := net.Listen("tcp", "localhost:6479")
        if err != nil {
                fmt.Println("Error listening:", err.Error())
                os.Exit(1)
        }
        defer server.Close()
        fmt.Println("Listening on localhost:6479")
        fmt.Println("Waiting for client...")
        for {
                connection, err := server.Accept()
                if err != nil {
                        fmt.Println("Error accepting: ", err.Error())
                        os.Exit(1)
                }
                fmt.Println("client connected", connection.RemoteAddr())
                go processClient(connection)
        }
}
func processClient(connection net.Conn) {
	var received int
  buffer := bytes.NewBuffer(nil)
  for {
		for !bytes.Contains(buffer.Bytes(), []byte("\r\n")) {
			chunk := make([]byte, 1024)
			chunkLength, err := connection.Read(chunk)
			
			if err != nil {
				//return received, buffer.Bytes(), err
				fmt.Println("Error: ", err)
			}
			if chunkLength == 0 {
				fmt.Println("Socket Connection Closed")
				break
			}
			if chunkLength > 8 && (!bytes.Contains(buffer.Bytes(), []byte("\n\n")) || !bytes.Contains(buffer.Bytes(), []byte("\r\n"))) {
				fmt.Println("Problem with the data being sent by", connection.RemoteAddr())
			}

			received += chunkLength
			buffer.Write(chunk[:chunkLength])
			fmt.Println("Received: ", string(chunk[:chunkLength]))
		}
		fmt.Println("Received: ", buffer.String())
		message := buffer.String()
		fmt.Println("Received: ", message)
	}
	//fmt.Println(received, buffer.Bytes(), nil)
	//return received, buffer.Bytes(), nil
}