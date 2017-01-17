package translator

import (
	"bytes"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"strings"

	"github.com/imankulov/linguee-api/cache"

	"golang.org/x/net/html/charset"
)

func downloadURL(cache cache.Cache, userAgent string, url string) (io.Reader, error) {
	if cache != nil {
		_, bb, err := cache.Get(url)
		if err == nil {
			log.Printf("Cache hit for %s", url)
			return bytes.NewReader(bb), nil
		}
		log.Printf("Cache miss for %s", url)
	}

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

	unicodeData, err := ioutil.ReadAll(unicodeReader)
	if err != nil {
		log.Print("HTTP error:", err)
		return nil, err
	}
	if cache != nil {
		err = cache.Set(url, resp.StatusCode, unicodeData)
		if err != nil {
			log.Printf("Warning: unable to populate the cache: %s", err)
		}
	}

	rd := bytes.NewReader(unicodeData)
	return rd, nil
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
