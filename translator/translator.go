package translator

import (
	"fmt"
	"log"
	"net/http"
	"net/url"
	"strings"

	"github.com/imankulov/linguee-api/cache"
)

// User-Agent string, where %s is replaced with the service name
var userAgentTemplate = "Linguee API proxy at %s (https://github.com/imankulov/linguee-api)"

// lang codes supported by Linguee
var validCodes = map[string]string{
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

// Translator is the main API endpoint
type Translator struct {
	ServiceName string
	Cache       cache.Cache
}

// Translate returns translation for text from srclang to dstLang
func (t *Translator) Translate(q, srcLang, dstLang string, guessDirection bool, processCorrection bool) (*APIResponse, error) {
	if q == "" {
		return nil, &LingueeError{Message: "empty query", StatusCode: http.StatusBadRequest}
	}

	srcLangPair, err := validateLang(srcLang)
	if err != nil {
		return nil, err
	}
	dstLangPair, err := validateLang(dstLang)
	if err != nil {
		return nil, err
	}

	lingueeURL := fmt.Sprintf("http://www.linguee.com/%s-%s/search?query=%s&ajax=1",
		srcLangPair.name,
		dstLangPair.name,
		url.QueryEscape(q),
	)

	if !guessDirection {
		lingueeURL = fmt.Sprintf("%s&source=%s", lingueeURL, srcLangPair.code)
	}

	userAgent := fmt.Sprintf(userAgentTemplate, t.ServiceName)
	log.Println("Send request:", lingueeURL)

	reader, err := downloadURL(t.Cache, userAgent, lingueeURL)
	if err != nil {
		log.Printf("ERROR: %s", err)
		return nil, err
	}

	obj, err := Parse(&reader)
	if err != nil && processCorrection {
		lingueeErr, ok := err.(*LingueeError)
		if ok && lingueeErr.Correction != nil {
			return t.Translate(*lingueeErr.Correction, srcLang, dstLang, guessDirection, false)
		}
	}
	return obj, err
}

type langPair struct {
	name string
	code string
}

func validateLang(langCode string) (*langPair, error) {
	normalizedCode := strings.ToUpper(langCode)
	langName := validCodes[normalizedCode]
	if langName == "" {
		return nil, &LingueeError{Message: "invalid language", StatusCode: http.StatusBadRequest}
	}
	return &langPair{name: langName, code: normalizedCode}, nil
}
