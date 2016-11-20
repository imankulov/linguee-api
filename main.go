package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
)

var userAgentTemplate = "Linguee API proxy at %s (https://github.com/imankulov/linguee-api)"

func redirect(w http.ResponseWriter, r *http.Request) {
	http.Redirect(w, r, "https://github.com/imankulov/linguee-api", http.StatusFound)
}

func api(w http.ResponseWriter, r *http.Request) {
	queryString := r.URL.Query()
	q := queryString.Get("q")

	srcLang := validateLang(queryString.Get("src"))
	dstLang := validateLang(queryString.Get("dst"))

	if srcLang == nil || dstLang == nil || q == "" {
		http.Error(w, http.StatusText(http.StatusBadRequest), http.StatusBadRequest)
		return
	}

	lingueeURL := fmt.Sprintf("http://www.linguee.com/%s-%s/search?query=%s&ajax=1&source=%s",
		srcLang.name,
		dstLang.name,
		url.QueryEscape(q),
		srcLang.code,
	)
	userAgent := fmt.Sprintf(userAgentTemplate, r.Header.Get("Host"))
	log.Print("Send request:", lingueeURL)

	reader, err := downloadURL(userAgent, lingueeURL)
	if err != nil {
		http.Error(w, http.StatusText(http.StatusInternalServerError),
			http.StatusInternalServerError)
		return
	}

	obj, err := Parse(reader)
	if err != nil {
		notFound, ok := err.(*NotFoundError)
		if ok {
			if notFound.Correction == "" {
				log.Print("Parser error. Return 404:", err)
				http.Error(w, http.StatusText(http.StatusNotFound), http.StatusNotFound)
				return
			}
			log.Print("Parser error. Return redirect:", err)
			redirect := fmt.Sprintf(`/?q=%s`, url.QueryEscape(notFound.Correction))
			http.Redirect(w, r, redirect, http.StatusFound)
			return
		}

		log.Print("Parser error. Return 500:", err)
		http.Error(w, http.StatusText(http.StatusInternalServerError), http.StatusInternalServerError)
		return
	}

	js, err := json.MarshalIndent(obj, "", "  ")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Write(js)
}

type langPair struct {
	name string
	code string
}

func validateLang(langCode string) *langPair {
	validCodes := map[string]string{
		"BG": "bulgarian",
		"CS": "czech",
		"DA": "danish",
		"DE": "german",
		"EL": "greek",
		"EN": "english",
		"ES": "spanish",
		"ET": "estonian",
		"FI": "finnish",
		"FR": "french",
		"HU": "hungarian",
		"IT": "italian",
		"JA": "japanese",
		"LT": "lithuanian",
		"LV": "latvian",
		"MT": "maltese",
		"NL": "dutch",
		"PL": "polish",
		"PT": "portuguese",
		"RO": "romanian",
		"RU": "russian",
		"SK": "slovak",
		"SL": "slovene",
		"SV": "swedish",
		"ZH": "chinese",
	}
	normalizedCode := strings.ToUpper(langCode)
	langName := validCodes[normalizedCode]
	if langName == "" {
		return nil
	}
	return &langPair{name: langName, code: normalizedCode}
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
