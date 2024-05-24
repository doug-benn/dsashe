package main

// import "bufio"

// func ReadLine(reader bufio.Reader) (line []byte, isPrefix bool, err error) {
// 	line, err = reader.ReadSlice('\n')
// 	if err == bufio.ErrBufferFull {
// 		if len(line) > 0 && line[len(line)-1] == '\r' {
// 			reader.r--
// 			line = line[:len(line)-1]
// 		}
// 		return line, true, nil
// 	}

// 	if len(line) == 0 {
// 		if err != nil {
// 			line = nil
// 		}
// 		return
// 	}
// 	err = nil

// 	if line[len(line)-1] == '\n' {
// 		drop := 1
// 		if len(line) > 1 && line[len(line)-2] == '\r' {
// 			drop = 2
// 		}
// 		line = line[:len(line)-drop]
// 	}
// 	return
// }

//  err != bufio.ErrBufferFull {
// 			return nil, err
// 		}

// 		full := make([]byte, len(b))
// 		copy(full, b)

// 		b, err = r.rd.ReadBytes('\n')
// 		if err != nil {
// 			return nil, err
// 		}

// 		full = append(full, b...) //nolint:makezero
// 		b = full
// 	}
// 	if len(b) <= 2 || b[len(b)-1] != '\n' || b[len(b)-2] != '\r' {
// 		return nil, fmt.Errorf("redis: invalid reply: %q", b)
// 	}
// 	return b[:len(b)-2], nil
// }

// func readStream(reader *bufio.Reader) ([]byte, error) {
// 	// Check stream is good
// 	// Split stream on \r and check
// func (r *Reader) readLine() ([]byte, error) {
// 	b, err := r.rd.ReadSlice('\n')
// 	if err != nil {
// 		if err != bufio.ErrBufferFull {
// 			return nil, err
// 		}

// 		full := make([]byte, len(b))
// 		copy(full, b)

// 		b, err = r.rd.ReadBytes('\n')
// 		if err != nil {
// 			return nil, err
// 		}

// 		full = append(full, b...) //nolint:makezero
// 		b = full
// 	}
// 	if len(b) <= 2 || b[len(b)-1] != '\n' || b[len(b)-2] != '\r' {
// 		return nil, fmt.Errorf("redis: invalid reply: %q", b)
// 	}
// 	return b[:len(b)-2], nil
// }	// To avoid allocations, attempt to read the line using ReadSlice.
// 	p, err := reader.ReadSlice('\n')
// 	if err == bufio.ErrBufferFull {
// 		// The line does not fit in the bufio.Reader's buffer. Fall back to
// 		// allocating a buffer for the line.
// 		buf := append([]byte{}, p...)
// 		for err == bufio.ErrBufferFull {
// 			p, err = reader.ReadSlice('\n')
// 			buf = append(buf, p...)
// 		}
// 		p = buf
// 	}
// 	if err != nil {
// 		return nil, err
// 	}
// 	i := len(p) - 2
// 	if i < 0 || p[i] != '\r' {
// 		return nil, errors.New("bad line terminator")
// 	}
// 	return p[:i], nil
// }
