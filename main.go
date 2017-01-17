package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"

	"github.com/imankulov/linguee-api/cache"
	"github.com/imankulov/linguee-api/translator"
)

var c cache.Cache

func redirect(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, "https://github.com/imankulov/linguee-api", http.StatusFound)
}

func api(w http.ResponseWriter, r *http.Request) {
	queryString := r.URL.Query()
	q := queryString.Get("q")
	srcLang := queryString.Get("src")
	dstLang := queryString.Get("dst")

	if c == nil {
		c = cache.NewMemoryCache()
	}

	tr := translator.Translator{
		ServiceName: r.Header.Get("Host"),
		Cache:       c,
	}

	obj, err := tr.Translate(q, srcLang, dstLang, false, false)
	if err != nil {
		lingueeError, ok := err.(*translator.LingueeError)
		if !ok {
			lingueeError = &translator.LingueeError{
				Message:    http.StatusText(http.StatusInternalServerError),
				StatusCode: http.StatusInternalServerError,
			}
		}

		// special case for correction
		if lingueeError.Correction != nil {
			redirect := fmt.Sprintf(`/api?q=%s&src=%s&dst=%s`, url.QueryEscape(*lingueeError.Correction), srcLang, dstLang)
			http.Redirect(w, r, redirect, http.StatusFound)
			return
		}

		// Just return HTTP error
		log.Printf("Linguee error #%v\n", lingueeError)
		WriteJSON(w, lingueeError, lingueeError.StatusCode)
		return
	}

	WriteJSON(w, obj, http.StatusOK)
}

func main() {
	http.HandleFunc("/", redirect)
	http.HandleFunc("/api", api)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}
	http.ListenAndServe(fmt.Sprintf(":%s", port), nil)

}

// WriteJSON writes object representation in JSON to HTTP.
func WriteJSON(w http.ResponseWriter, obj interface{}, status int) {
	buffer, err := json.MarshalIndent(obj, "", "    ")
	if err != nil {
		log.Println("Internal server error while converting object to json: ", obj)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	SetCORSHeaders(w)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	w.Write(buffer)
}

// SetCORSHeaders sets CORS headers
func SetCORSHeaders(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Max-Age", "86400")
}
