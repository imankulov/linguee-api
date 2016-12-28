package translator

import (
	"bytes"
	"errors"
	"io"
	"log"
	"net/http"
	"strconv"
	"strings"

	"golang.org/x/net/html"
	xmlpath "gopkg.in/xmlpath.v2"
)

// APIResponse is the root structure of parsed API response
type APIResponse struct {
	SrcLang        string        `json:"src_lang"`      // e.g "pt"
	DstLang        string        `json:"dst_lang"`      // e.g "en"
	Query          string        `json:"query"`         // e.g "obrigado"
	CorrectQuery   string        `json:"correct_query"` // e.g "obrigado"
	ExactMatches   []Lemma       `json:"exact_matches"`
	InexactMatches []Lemma       `json:"inexact_matches"`
	RealExamples   []RealExample `json:"real_examples"`
}

// Lemma contains information about one found word (lemma)
type Lemma struct {
	Featured     bool           `json:"featured"`
	Wt           int            `json:"wt"`        // e.g 1000 or 386
	LemmaID      string         `json:"lemma_id"`  // e.g "PT:obrigado49462"
	Text         string         `json:"text"`      // e.g. "obrigado"
	WordType     wordProperties `json:"word_type"` // e.g "adjective / past participle, masculine"
	AudioLinks   []AudioLink    `json:"audio_links"`
	Forms        []LemmaForm    `json:"forms"`
	Translations []Translation  `json:"translations"`
}

// LemmaForm contains variants of the lemma (how it would be in plural, feminine, etc)
type LemmaForm struct {
	Text     string         `json:"text"`      // e.g "obrigada"
	FormType wordProperties `json:"form_type"` // e.g "f sl"
}

// AudioLink contains the link to the audio file along with the language variant
type AudioLink struct {
	URLPart string `json:"url_part"` // e.g "PT_BR/f5/f5491d72610965dd0a287c1ab1025c0f-300"
	Lang    string `json:"lang"`     // e.g "Brazilian Portuguese"
}

// Translation is one of the possible translation of the term
type Translation struct {
	Featured   bool                 `json:"featured"`
	Text       string               `json:"text"`      // e.g "required"
	Bid        string               `json:"bid"`       // e.g. "10003211476"
	LemmaID    string               `json:"lemma_id"`  // e.g "EN:required5162"
	WordType   wordProperties       `json:"word_type"` // e.g "adjective"
	AudioLinks []AudioLink          `json:"audio_link"`
	Examples   []TranslationExample `json:"examples"`
}

// TranslationExample is a pair of phrases in source and target languages,
// providing a usage sample for the term
type TranslationExample struct {
	Source string `json:"source"` // e.g. "Estou obrigado pelo contrato a trabalhar seis horas por dia."
	Target string `json:"target"` // e.g. "I am bound by the contract to work six hours a day."
}

// RealExample is an example of usage of the word in the context
type RealExample struct {
	ID  string `json:"id"`  // e.g "row_0_8255523216_0"
	Src string `json:"src"` // e.g "Parabéns e um grande obrigado a todos que ajudaram [...] ao sucesso desta noite!"
	Dst string `json:"dst"` // e.g "Well done and many thanks to everyone who helped [...] make this evening a success!"
	URL string `json:"url"` // e.g "http://www.findmadeleine.com/pt/updates@page=2.html"
}

// Parse returns API response from source HTML (provided as a byte array)
func Parse(src *io.Reader) (*APIResponse, error) {
	resp := APIResponse{}

	// parse XML
	xmlroot, err := xmlDocument(src)
	if err != nil {
		return nil, err
	}

	// check if it's a "not found" response
	if xmlpath.MustCompile(`//h1[@class="noresults wide_in_main"]`).Exists(xmlroot) {
		correction := extractValue(xmlroot, `//span[@class="corrected"]`)
		if correction != "" {
			return nil, &LingueeError{
				Message:    "Another term found",
				StatusCode: http.StatusFound,
				Correction: &correction,
			}
		}
		return nil, &LingueeError{Message: "Term not found", StatusCode: http.StatusNotFound}
	}

	dataDiv, err := getByID(xmlroot, "data")
	if err != nil {
		return nil, errors.New(`<div id="data"> not found`)
	}
	resp.SrcLang = strings.ToLower(extractValue(dataDiv, `@data-sourcelang`))
	resp.DstLang = strings.ToLower(extractValue(dataDiv, `@data-targetlang`))
	resp.Query = extractValue(dataDiv, `@data-query`)
	resp.CorrectQuery = extractValue(dataDiv, `@data-correctspellingofquery`)

	dictionaryDiv, err := getByID(xmlroot, "dictionary")
	if err == nil {
		resp.ExactMatches = make([]Lemma, 0)
		for it := xmlpath.MustCompile(`.//div[@class="exact"]`).Iter(dictionaryDiv); it.Next(); {
			node := it.Node()
			for lemmaIt := xmlpath.MustCompile(`div`).Iter(node); lemmaIt.Next(); {
				lemmaNode := lemmaIt.Node()
				lemmaObj, lemmaErr := lemmaFromNode(lemmaNode)
				if lemmaErr == nil {
					resp.ExactMatches = append(resp.ExactMatches, lemmaObj)
				}
			}
		}
	}

	resp.RealExamples = extractRealExamples(xmlroot)

	return &resp, nil
}

func xmlDocument(src *io.Reader) (*xmlpath.Node, error) {
	root, err := html.Parse(*src)
	if err != nil {
		log.Println("Unable to parse HTML document: ", err)
		return nil, err
	}

	// Write back and parse this time as valid XML document
	var b bytes.Buffer
	html.Render(&b, root)
	xmlReader := strings.NewReader(b.String())
	xmlroot, err := xmlpath.ParseHTML(xmlReader)
	if err != nil {
		return nil, err
	}

	return xmlroot, nil
}

func lemmaFromNode(node *xmlpath.Node) (Lemma, error) {
	obj := Lemma{}

	obj.Featured = nodeHasClass(node, "featured")

	wt := extractValue(node, `@wt`)
	obj.Wt, _ = strconv.Atoi(wt)

	obj.LemmaID = extractValue(node, `div/h2/@lid`)
	obj.WordType = parseLongProperties(extractValue(node, `.//span[@class="tag_wordtype"]`))

	// TODO: invalid value for verb tirar (lemma #1)
	textChunks := extractValues(node, `.//span[@class="tag_lemma"]/a[@class="dictLink"]`)
	obj.Text = strings.Join(textChunks, " ")

	audioLinksText := extractValue(node, `.//a[@class="audio"]/@onclick`)
	obj.AudioLinks = extractAudioLinks(audioLinksText)

	obj.Forms = extractLemmaForms(node)
	obj.Translations = extractTranslations(node)

	return obj, nil
}

func extractAudioLinks(js string) []AudioLink {
	links := make([]AudioLink, 0, 2)
	chunks := strings.Split(js, `"`)

	link := AudioLink{}
	for i, chunk := range chunks {
		if (i % 4) == 1 {
			link.URLPart = chunk
		}
		if (i % 4) == 3 {
			link.Lang = chunk
			links = append(links, link)
			link = AudioLink{}
		}
	}

	return links
}

func extractLemmaForms(node *xmlpath.Node) []LemmaForm {
	var forms []LemmaForm
	for it := xmlpath.MustCompile(`.//h2/span/span[@class="tag_s"]`).Iter(node); it.Next(); {
		formNode := it.Node()
		form := LemmaForm{}

		form.Text = extractValue(formNode, `a[@class="formLink"]`)
		form.FormType = parseShortProperties(extractValue(formNode, `span[@class="tag_type"]`))
		if form.Text != "" && !form.FormType.empty() {
			forms = append(forms, form)
		}
	}
	return forms
}

func extractTranslations(node *xmlpath.Node) []Translation {
	var translations []Translation
	for it := xmlpath.MustCompile(`.//div`).Iter(node); it.Next(); {

		translationNode := it.Node()
		if !nodeHasClass(translationNode, "translation") {
			continue
		}

		obj := Translation{}
		obj.Featured = nodeHasClass(translationNode, "featured")
		obj.Text = extractValue(translationNode, `.//span[@class="tag_trans"]/a[1]`)
		obj.Bid = extractValue(translationNode, `.//span[@class="tag_trans"]/@bid`)
		obj.LemmaID = extractValue(translationNode, `.//span[@class="tag_trans"]/@lid`)
		obj.WordType = parseShortProperties(extractValue(translationNode, `.//span[@class="tag_trans"]/span[@class="tag_type"]`))

		audioLinksText := extractValue(translationNode, `.//a[@class="audio"]/@onclick`)
		obj.AudioLinks = extractAudioLinks(audioLinksText)
		obj.Examples = make([]TranslationExample, 0)
		for itEx := xmlpath.MustCompile(`.//div[@class="example_lines"]`).Iter(translationNode); itEx.Next(); {
			exampleNode := itEx.Node()
			example := TranslationExample{
				Source: extractValue(exampleNode, `.//span[@class="tag_s"]`),
				Target: extractValue(exampleNode, `.//span[@class="tag_t"]`),
			}
			obj.Examples = append(obj.Examples, example)
		}

		translations = append(translations, obj)
	}

	return translations
}

func extractRealExamples(root *xmlpath.Node) []RealExample {
	var examples []RealExample

	resultTable, err := getByID(root, `result_table`)
	if err != nil {
		return examples
	}

	for it := xmlpath.MustCompile(`.//tr`).Iter(resultTable); it.Next(); {
		tr := it.Node()

		src := extractNodeContentUntil(tr, `td[1]/div/node()`, `.[@class="source_url_spacer"]`)
		dst := extractNodeContentUntil(tr, `td[2]/div/node()`, `.[@class="source_url_spacer"]`)

		example := RealExample{
			Src: mergeSpaces(src),
			Dst: mergeSpaces(dst),
			URL: extractValue(tr, `.//div[@class="source_url"]/a/@href`),
		}
		examples = append(examples, example)
	}

	return examples
}
