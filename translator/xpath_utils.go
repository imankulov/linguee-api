package translator

import (
	"bytes"
	"fmt"
	"strings"

	xmlpath "gopkg.in/xmlpath.v2"
)

// getById returns element by id, or error if there's no element,
// or more than one element
func getByID(root *xmlpath.Node, id string) (*xmlpath.Node, error) {
	return getByXPath(root, fmt.Sprintf(`.//*[@id="%s"]`, id))
}

// getByXPath returns element by xpath, or error if there's no element, or
// more than one element
func getByXPath(root *xmlpath.Node, path string) (*xmlpath.Node, error) {
	p, err := xmlpath.Compile(path)
	if err != nil {
		return nil, err
	}
	it := p.Iter(root)
	hasFirst := it.Next()
	if !hasFirst {
		return nil, fmt.Errorf("Element with xpath %s not found", path)
	}
	ret := it.Node()
	hasSecond := it.Next()
	if hasSecond {
		return nil, fmt.Errorf("Found more than one element with path %s", path)
	}
	return ret, nil

}

// nodeHasClass returns true if node matches the class in question
func nodeHasClass(node *xmlpath.Node, class string) bool {
	path := xmlpath.MustCompile(`@class`)
	if val, ok := path.String(node); ok {
		chunks := strings.Fields(val)
		for _, chunk := range chunks {
			if chunk == class {
				return true
			}
		}
	}
	return false
}

func extractValue(node *xmlpath.Node, path string) string {
	if val, ok := xmlpath.MustCompile(path).String(node); ok {
		return val
	}
	return ""
}

func extractValues(node *xmlpath.Node, path string) []string {
	ret := make([]string, 0, 0)
	for it := xmlpath.MustCompile(path).Iter(node); it.Next(); {
		ret = append(ret, it.Node().String())
	}
	return ret
}

func extractNodeContentUntil(node *xmlpath.Node, path string, stopPath string) string {
	var buffer bytes.Buffer
	compiledStopPath := xmlpath.MustCompile(stopPath)

	for it := xmlpath.MustCompile(path).Iter(node); it.Next(); {
		n := it.Node()
		if compiledStopPath.Exists(n) {
			break
		}
		buffer.Write(n.Bytes())
	}

	return buffer.String()
}

func mergeSpaces(s string) string {
	chunks := strings.Fields(s)
	return strings.Join(chunks, " ")
}
