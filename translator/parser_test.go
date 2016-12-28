package translator

import (
	"io"
	"log"
	"net/http"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNotFound(t *testing.T) {
	assert := assert.New(t)

	resp, parseErr := Parse(readFile("examples/xxxzzz.html"))
	assert.Nil(resp)
	assert.NotNil(parseErr)
	typedError, ok := parseErr.(*LingueeError)
	assert.True(ok)
	assert.Equal(typedError.StatusCode, http.StatusNotFound)
}

func TestNotFoundWithCorrection(t *testing.T) {
	assert := assert.New(t)
	resp, parseErr := Parse(readFile("examples/constibado.html"))
	assert.Nil(resp)
	assert.NotNil(parseErr)
	typedError, ok := parseErr.(*LingueeError)
	assert.True(ok)
	assert.Equal(typedError.StatusCode, http.StatusFound)
	assert.Equal(*typedError.Correction, "constipado")
}

func TestObrigado(t *testing.T) {
	assert := assert.New(t)
	resp, err := Parse(readFile("examples/obrigado.html"))
	if err != nil {
		t.Fatal(err)
	}

	assert.Equal(resp.SrcLang, "pt")
	assert.Equal(resp.DstLang, "en")
	assert.Equal(resp.Query, "obrigado")
	assert.Equal(resp.CorrectQuery, "obrigado")
	assert.Len(resp.ExactMatches, 6)

	match0 := resp.ExactMatches[0]
	match1 := resp.ExactMatches[1]
	match2 := resp.ExactMatches[2]

	assert.True(match0.Featured)
	assert.False(match2.Featured)

	assert.Equal(match0.Text, "obrigado")
	assert.Equal(match0.Wt, 1000)
	assert.Equal(match0.LemmaID, "PT:obrigado49462")
	assert.Equal(match0.WordType.POS, "interjection")
	assert.Equal(match0.WordType.Gender, "")
	assert.Len(match0.AudioLinks, 2)

	assert.Equal(match0.AudioLinks[0].Lang, "Brazilian Portuguese")
	assert.Equal(match0.AudioLinks[0].URLPart, "PT_BR/f5/f5491d72610965dd0a287c1ab1025c0f-1000")

	assert.Len(match1.Forms, 3)
	assert.Equal(match1.Forms[0].Text, "obrigada")
	assert.Equal(match1.Forms[0].FormType.POS, "noun")
	assert.Equal(match1.Forms[0].FormType.Gender, "feminine")
	assert.Equal(match1.Forms[0].FormType.Plural, false)

	assert.Len(match0.Translations, 1)

	tr := match0.Translations[0]
	assert.True(tr.Featured)
	assert.Equal(tr.Bid, "10001019966")
	assert.Equal(tr.LemmaID, "EN:thank#you26529")
	assert.Equal(tr.Text, "thank you")
	assert.Equal(tr.WordType.POS, "interjection")

	assert.Equal(tr.Examples[0].Source, "Obrigado por sua participação em nossa pesquisa.")
	assert.Equal(tr.Examples[0].Target, "Thank you for your participation in our survey.")

	assert.Len(resp.RealExamples, 28)
	ex0 := resp.RealExamples[0]
	assert.Equal(ex0.Src, "Muito obrigado por estas palavras [...] tão simpáticas.")
	assert.Equal(ex0.Dst, "So thank you very much for all the [...] nice words.")
	assert.Equal(ex0.URL, "http://www.europarl.europa.eu/sides/getDoc.do?pubRef=-//EP//TEXT+CRE+20011113+ITEMS+DOC+XML+V0//PT&amp;language=PT")
}

func TestTwoWordSentence(t *testing.T) {
	assert := assert.New(t)
	resp, err := Parse(readFile("examples/not_bad.html"))
	if err != nil {
		t.Fatal(err)
	}

	assert.Equal(resp.SrcLang, "en")
	assert.Equal(resp.DstLang, "pt")
	assert.Equal(resp.Query, "not bad")
	assert.Equal(resp.CorrectQuery, "not bad")

	match := resp.ExactMatches[0]
	assert.Equal(match.Text, "not bad")

	tr := match.Translations[0]
	assert.Equal(tr.Text, "nada mal")
}

func TestMultipleTranslations(t *testing.T) {
	assert := assert.New(t)
	resp, err := Parse(readFile("examples/esgotar.html"))
	if err != nil {
		t.Fatal(err)
	}

	assert.Equal(resp.SrcLang, "pt")
	assert.Equal(resp.DstLang, "en")

	match := resp.ExactMatches[0]
	assert.Equal(match.Text, "esgotar")

	tr := match.Translations[0]
	assert.Equal(tr.Text, "exhaust (sth.)")
}

func readFile(filename string) *io.Reader {
	var html io.Reader
	fd, err := os.Open(filename)
	if err != nil {
		log.Fatal("Unable to read file ", filename, err)
	}
	html = fd
	return &html
}
