package cache

import (
	"database/sql"
	"log"
	"testing"

	"github.com/stretchr/testify/assert"

	_ "github.com/lib/pq"
)

func TestMemorySetGet(t *testing.T) {
	c := NewMemoryCache()
	testSetGet(c, t)
}

func TestDBSetGet(t *testing.T) {
	c := newDBCache()
	testSetGet(c, t)
}

func TestMemoryEmpty(t *testing.T) {
	c := NewMemoryCache()
	testEmpty(c, t)
}

func TestDBEmpty(t *testing.T) {
	c := newDBCache()
	testEmpty(c, t)
}

func newDBCache() DBCache {
	db, err := sql.Open("postgres", "sslmode=disable")
	if err != nil {
		log.Fatal(err)
	}
	c := DBCache{Database: db}
	c.Clear()
	return c
}

func testEmpty(c Cache, t *testing.T) {
	assert := assert.New(t)
	_, _, err := c.Get("http://example.com")
	assert.NotNil(err)
}

func testSetGet(c Cache, t *testing.T) {
	assert := assert.New(t)
	err := c.Set("http://example.com", 200, []byte("foo bar"))
	if err != nil {
		log.Fatal(err)
	}
	code, content, err := c.Get("http://example.com")
	assert.Nil(err)
	assert.Equal(200, code)
	assert.Equal([]byte("foo bar"), content)
}
