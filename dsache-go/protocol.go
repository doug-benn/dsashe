package main

import (
	"bytes"
	"errors"
	"log/slog"
	"net"
	"strings"
)

const (
	cmdPING = "PING"
	cmdECHO = "ECHO"
	cmdGET  = "GET"
)

func handleCommand(parsedMsg [][]byte, conn net.Conn) {
	switch strings.ToUpper(string(parsedMsg[0])) {
	default:
		slog.Error("Unknown Command")
		conn.Write([]byte("-1\r\n"))
	case cmdPING:
		slog.Info("Ping: Sending PONG")
		conn.Write([]byte("PONG\r\n"))
	case cmdECHO:
		slog.Info("Echo: Echoing back", "Message:", parsedMsg[1:])
		conn.Write(parsedMsg[1])

	}
}

func parseMessage(buffer bytes.Buffer) (parsedMsg [][]byte, err error) {
	message, remain_buf, found := bytes.Cut(buffer.Bytes(), []byte{'\r', '\n'})
	if found {
		buffer.Reset()
		buffer.Write(remain_buf)

		splitMsg := bytes.Split(message, []byte{'\n', '\n'})
		return splitMsg, nil
	} else {
		return nil, errors.New("message separator not found")
	}
}
