package translator

import (
	"bytes"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"strings"

	"golang.org/x/net/html/charset"
)

func downloadURL(userAgent string, url string) (*io.Reader, error) {
	// Make request object, and send GET request to the server
	client := http.Client{}
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Print("HTTP error:", err)
		return nil, err
	}
	req.Header.Add("User-Agent", userAgent)
	resp, err := client.Do(req)
	if err != nil {
		log.Print("HTTP error:", err)
		return nil, err
	}

	// Read response content to byte array
	body, err := ioutil.ReadAll(resp.Body)
	defer resp.Body.Close()
	if err != nil {
		log.Print("HTTP error:", err)
		return nil, err
	}

	// detect charset, and make reader returning unicode data
	unicodeReader, err := charset.NewReaderLabel(
		detectCharset(resp), bytes.NewReader(body))
	if err != nil {
		log.Print("HTTP error:", err)
		return nil, err
	}

	return &unicodeReader, nil
}

func detectCharset(resp *http.Response) string {
	_, utf8 := charset.Lookup("utf-8")

	charsetChunks := strings.Split(resp.Header.Get("Content-Type"), `"`)
	if len(charsetChunks) > 1 {
		_, charset := charset.Lookup(charsetChunks[len(charsetChunks)-2])
		if charset != "" {
			return charset
		}
		log.Printf("Warning. Unable to define charset in %s. Fall back to %s",
			charset, utf8)
		return utf8
	}
	return utf8
}
