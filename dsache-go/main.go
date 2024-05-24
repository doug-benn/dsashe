package main

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"log/slog"
	"net"
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

func (s *Server) acceptConnections() error {
	for {
		conn, err := s.ServerListener.Accept()
		if err != nil {
			slog.Error("Error accepting Connection", "err", err)
			continue
		}
		slog.Info("Client connected", "Remote Address", conn.RemoteAddr())
		go s.handleConnection(conn)
	}
}

// readStream Reads the TCP stream
func readStream(conn net.Conn) (*bytes.Buffer, error) {
	var received int
	buffer := bytes.NewBuffer(nil)
	for !bytes.Contains(buffer.Bytes(), []byte("\r\n")) {
		chunk := make([]byte, 1024)
		chunkLength, err := conn.Read(chunk)
		if err != nil || chunkLength == 0 {
			if err != io.EOF {
				fmt.Println("Error: ", err)
			}
			return nil, nil
		}
		received += chunkLength
		buffer.Write(chunk[:chunkLength])

		fmt.Print(string(chunk))
		if chunkLength > 8 && (!bytes.Contains(buffer.Bytes(), []byte("\n\n")) || !bytes.Contains(buffer.Bytes(), []byte("\r\n"))) {
			slog.Error("Problem with the data being sent by", "Remote Addr", conn.RemoteAddr())
		}
	}
	return buffer, nil
}

func (s *Server) handleConnection(conn net.Conn) {
	defer func() {
		_ = conn.Close()
		slog.Info("Closed connection", "to", conn.RemoteAddr())
	}()

	// limitedConn := &io.LimitedReader{
	// 	R: conn,
	// 	N: 1024,
	// }
	for {
		input, err := readStream(conn)
		if err != nil {
			slog.Error("Error reading TCP Stream", "Error:", err)
		}
		slog.Info(input.String())

		// 	var received int
		// 	buffer := bytes.NewBuffer(nil)
		// 	for !bytes.Contains(buffer.Bytes(), []byte("\r\n")) {
		// 		chunk := make([]byte, 1024)
		// 		chunkLength, err := conn.Read(chunk)
		// 		if err != nil || chunkLength == 0 {
		// 			if err != io.EOF {
		// 				fmt.Println("Error: ", err)
		// 			}
		// 			return
		// 		}
		// 		if chunkLength > 8 && (!bytes.Contains(buffer.Bytes(), []byte("\n\n")) || !bytes.Contains(buffer.Bytes(), []byte("\r\n"))) {
		// 			fmt.Println("Problem with the data being sent by", connection.RemoteAddr())
		// 			break
		// 		}
		// 		received += chunkLength
		// 		buffer.Write(chunk[:chunkLength])
		// 	}
		// }
	}
}

func (s *Server) Start() error {
	listener, err := net.Listen("tcp", s.ListenAddr+":"+s.ListenPort)
	if err != nil {
		return err
	}
	s.ServerListener = listener

	slog.Info("Server running", "listenAddr", s.ListenAddr)

	return s.acceptConnections()
}

func main() {
	slog.Info("Server is Starting...")
	server := NewServer(Config{
		ListenAddr: "localhost",
		ListenPort: "6479",
	})
	log.Fatal(server.Start())

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
// func SplitTCP(data []byte, _ bool) (advance int, token []byte, err error) {
// 	message, _, found := bytes.Cut(data, []byte{'\r', '\n'})
// 	if !found {
// 		return 0, nil, nil // Waiting for more data
// 	}
// 	messageLength := len(message)
// 	return messageLength, data[:messageLength], nil
// }

// func ParseMessage(msg []byte) (command string, data []byte) {
// 	//fmt.Printf("%q\n", msg)
// 	splitMsg := bytes.Split(msg, []byte{'\n', '\n'})

// 	return strings.ToLower(string(splitMsg[0])), splitMsg[1]

// 	// switch strings.ToLower(string(splitMsg[0])) {
// 	// case "ping":
// 	// 	return "ping", nil

// 	// default:
// 	// 	return "", errors.New("unsupported command")
// 	// }

// }
