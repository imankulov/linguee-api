package translator

import (
	"fmt"
	"strings"
)

var posFullNames = map[string]string{
	"noun":                        "noun",
	"noun as adjective":           "noun as adjective", // en: "test"
	"verb":                        "verb",
	"adjective":                   "adjective",
	"adjective / past participle": "adjective / past participle",
	"adverb":                      "adverb",
	"pronoun":                     "pronoun",
	"preposition":                 "preposition",
	"conjunction":                 "conjunction",
	"interjection":                "interjection",
	"article":                     "article",
}

var genderFullNames = map[string]string{
	"feminine":  "feminine",
	"masculine": "masculine",
	"neuter":    "neuter",
}

var pluralFullNames = map[string]bool{
	"singular": false,
	"plural":   true,
}

var posShortNames = map[string]string{
	"n":      "noun",
	"m":      "noun",
	"f":      "noun",
	"nt":     "noun",
	"pl":     "noun",
	"v":      "verb",
	"adj":    "adjective",
	"adv":    "adverb",
	"pron":   "pronoun",
	"prep":   "preposition",
	"conj":   "conjunction",
	"interj": "interjection",
	"art":    "article",
}

var revPostShortNames = map[string]string{
	"noun":         "n",
	"verb":         "v",
	"adjective":    "adj",
	"adverb":       "adv",
	"pronoun":      "pron",
	"preposition":  "prep",
	"conjunction":  "conj",
	"interjection": "interj",
	"article":      "art",
}

var genderShortNames = map[string]string{
	"m":  "masculine",
	"f":  "feminine",
	"nt": "neuter",
}

var revGenderShortNames = map[string]string{
	"masculine": "m",
	"feminine":  "f",
	"neuter":    "nt",
}

var pluralShortNames = map[string]bool{
	"sl": false,
	"pl": true,
}

// wordProperties contains structured information about the
// part of speech, gender, and singular-plural status
type wordProperties struct {
	POS    string `json:"pos,omitempty"`
	Gender string `json:"gender,omitempty"`
	Plural bool   `json:"plural,omitempty"`
}

func (wp wordProperties) empty() bool {
	return wp.POS == "" && wp.Gender == ""
}

// Full returns full string representation of properties
func (wp wordProperties) Full() string {
	var chunks = make([]string, 0, 3)
	if wp.POS != "" {
		chunks = append(chunks, wp.POS)
	}
	if wp.Gender != "" {
		chunks = append(chunks, wp.Gender)
	}
	if wp.Plural {
		chunks = append(chunks, "plural")
	}
	return strings.Join(chunks, ", ")
}

// Abbrev returns abbreviated string representation of properties
func (wp wordProperties) Abbrev() string {
	var s string
	if wp.Gender != "" {
		s = revGenderShortNames[wp.Gender]
	} else {
		s = revPostShortNames[wp.POS]
	}
	if wp.Plural {
		s = fmt.Sprintf("%s pl", s)
	}
	return strings.TrimSpace(s)
}

// parseLongProperties parses the "long variant" of part of speech + gender description
// and returns the pair of string constants: part of speech and gender
// examples:
// adjective -> wordProperties{pos: "adjective", gender: "", plural: false}
// noun -> wordProperties{pos: "noun", gender: "", plural: false}
// noun, masculine -> wordProperties{pos: "noun", gender: "masculine", plural: false}
// noun, plural -> wordProperties{pos: "noun", gender: "", plural: true}
func parseLongProperties(definition string) (wp wordProperties) {
	for _, chunk := range strings.Split(definition, ",") {
		chunk = strings.TrimSpace(chunk)

		// check for pos
		val, ok := posFullNames[chunk]
		if ok {
			wp.POS = val
			continue
		}

		// check for gender
		val, ok = genderFullNames[chunk]
		if ok {
			wp.Gender = val
			continue
		}

		// check for plural status
		plural, ok := pluralFullNames[chunk]
		if ok {
			wp.Plural = plural
			continue
		}
	}
	return wp
}

// parseShortProperties takes the "short variant" of of part of speech + gender description
// and returns the pair of strings with part of speech and gender
//
// examples:
// adj -> wordProperties{pos: "adjective", gender: "", plural: false}
// n -> wordProperties{pos: "noun", gender: "", plural: false}
// m -> wordProperties{pos: "noun", gender: "masculine", plural: false}
// pl -> wordProperties{pos: "noun", gender: "", plural: true}
func parseShortProperties(definition string) (wp wordProperties) {
	for _, chunk := range strings.Split(definition, " ") {
		chunk = strings.TrimSpace(chunk)

		// check for pos
		val, ok := posShortNames[chunk]
		if ok {
			wp.POS = val
		}

		// check for gender
		val, ok = genderShortNames[chunk]
		if ok {
			wp.Gender = val
		}

		// check for plural status
		plural, ok := pluralShortNames[chunk]
		if ok {
			wp.Plural = plural
		}
	}
	return
}
