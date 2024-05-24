package main

import (
	"bytes"
	"fmt"
	"io"
	"net"
	"os"
	"strings"
)

type Config struct {
	ListenAddr string
	ListenPort string
}

type Server struct {
	Config
	ServerListener net.Listener
}

func NewServer(cfg Config) *Server {
	return &Server{
		Config: cfg,
	}
}

func (s *Server) Start() error {
	listener, err := net.Listen("tcp", s.ListenAddr+s.ListenPort)
	if err != nil {
		return err
	}
	s.ServerListener = listener

	// go s.loop()

	// slog.Info("goredis server running", "listenAddr", s.ListenAddr)

	// return s.acceptLoop()
}

func main() {
	fmt.Println("Server Running...")
	server := NewServer(Config{
		ListenAddr: "localhost",
		ListenPort: "6479",
	})
	//server, err := net.Listen("tcp", "localhost:6479")
	// if err != nil {
	// 	fmt.Println("Error listening:", err.Error())
	// 	os.Exit(1)
	// }
	//defer server.Close()

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

func SplitTCP(data []byte, _ bool) (advance int, token []byte, err error) {
	message, _, found := bytes.Cut(data, []byte{'\r', '\n'})
	if !found {
		return 0, nil, nil // Waiting for more data
	}
	messageLength := len(message)
	return messageLength, data[:messageLength], nil
}

func ParseMessage(msg []byte) (command string, data []byte) {
	//fmt.Printf("%q\n", msg)
	splitMsg := bytes.Split(msg, []byte{'\n', '\n'})

	return strings.ToLower(string(splitMsg[0])), splitMsg[1]

	// switch strings.ToLower(string(splitMsg[0])) {
	// case "ping":
	// 	return "ping", nil

	// default:
	// 	return "", errors.New("unsupported command")
	// }

}

func processClient(connection net.Conn) {
	defer connection.Close()
	for {
		var received int
		buffer := bytes.NewBuffer(nil)
		for !bytes.Contains(buffer.Bytes(), []byte("\r\n")) {
			chunk := make([]byte, 1024)
			chunkLength, err := connection.Read(chunk)
			if err != nil || chunkLength == 0 {
				if err != io.EOF {
					fmt.Println("Error: ", err)
				}
				return
			}
			if chunkLength > 8 && (!bytes.Contains(buffer.Bytes(), []byte("\n\n")) || !bytes.Contains(buffer.Bytes(), []byte("\r\n"))) {
				fmt.Println("Problem with the data being sent by", connection.RemoteAddr())
				break
			}
			received += chunkLength
			buffer.Write(chunk[:chunkLength])
		}

		message, remain_buf, found := bytes.Cut(buffer.Bytes(), []byte{'\r', '\n'})
		if found {
			buffer.Reset()
			buffer.Write(remain_buf)

			splitMsg := bytes.Split(message, []byte{'\n', '\n'})

			fmt.Println("Command: ", strings.ToLower(string(splitMsg[0])))
			switch strings.ToLower(string(splitMsg[0])) {
			case "ping":
				_, err := connection.Write([]byte("PONG\r\n"))
				if err != nil {
					fmt.Println("Write Error: ", err)
				}
			default:
				fmt.Println("Unsupported: ", strings.ToLower(string(splitMsg[0])))
				connection.Write([]byte("-1\r\n"))
			}
		}
	}
}

// scanner := bufio.NewScanner(connection)
// scanner.Split(SplitTCP)

// for scanner.Scan() {
// 	msg := scanner.Bytes()
// 	cmd, err := ParseCommand(msg)
// 	if err != nil {
// 		panic(err)
// 	}
// 	switch cmd {
// 	case "ping":
// 		fmt.Println("Ping")
// 	default:
// 		fmt.Println("Odd")
// 	}
// }
