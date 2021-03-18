package cache

import (
	"bytes"
	"compress/zlib"
	"crypto/sha256"
	"database/sql"
	"errors"
	"fmt"
	"io/ioutil"
	"time"
)

// Cache interface used to store locally and temporarily
// pages downloaded from Linguee. Made to reduce the load on Linguee
// servers and to speed up the API.
type Cache interface {
	// Set used to save in the cache the status code and the content of the URL
	Set(url string, statusCode int, content []byte) error
	// Get used to get back data from the cache
	Get(url string) (int, []byte, error)
	// Clear removes all records from the cache
	Clear() error
}

// MemoryCache is an object which implements the cache interface and stores data
// in memory (dummy implementation: use in production with care, since
// never releases the cache, prone to memory leaks)
type MemoryCache map[string]memoryCacheItem

type memoryCacheItem struct {
	statusCode        int
	compressedContent []byte
}

// NewMemoryCache returns a memory cache object
func NewMemoryCache() Cache {
	c := make(MemoryCache)
	return &c
}

// Set used to save in the cache the status code and the content of the URL
func (c MemoryCache) Set(url string, statusCode int, content []byte) error {
	// compress the content to "compressed" buffer
	var compressed bytes.Buffer
	w := zlib.NewWriter(&compressed)
	_, err := w.Write(content)
	if err != nil {
		return err
	}
	err = w.Close()
	if err != nil {
		return err
	}
	c[url] = memoryCacheItem{statusCode: statusCode, compressedContent: compressed.Bytes()}
	return nil
}

// Get used to get back data from the cache
func (c MemoryCache) Get(url string) (statusCode int, content []byte, err error) {
	item, ok := c[url]
	if !ok {
		err = errors.New("url not in cache")
		return
	}
	statusCode = item.statusCode

	// decompress data from memory
	compressedReader := bytes.NewReader(item.compressedContent)
	decompressedReader, err := zlib.NewReader(compressedReader)
	if err != nil {
		return
	}
	defer decompressedReader.Close()
	content, err = ioutil.ReadAll(decompressedReader)
	return
}

// Clear removes all records from the cache
func (c MemoryCache) Clear() error {
	for k := range c {
		delete(c, k)
	}
	return nil
}

// DBCache is an object which implements the cache interface, and stores
// data in a database in compressed format
type DBCache struct {
	Database *sql.DB
	Table    string
	Timeout  time.Duration
}

// Set used to save in the cache the status code and the content of the URL
func (c DBCache) Set(url string, statusCode int, content []byte) error {
	// compress the content to "compressed" buffer
	var compressed bytes.Buffer
	w := zlib.NewWriter(&compressed)
	_, err := w.Write(content)
	if err != nil {
		return err
	}
	err = w.Close()
	if err != nil {
		return err
	}

	// add/replace a row to database (functionality available since PostgreSQL 9.5)
	// see https://www.postgresql.org/docs/9.5/static/sql-insert.html
	q := fmt.Sprintf(`
    INSERT INTO "%s" (id, url, status_code, content)
    VALUES ($1, $2, $3, $4)
    ON CONFLICT(id) DO UPDATE SET status_code = $3, content = $4`, c.getTable())

	_, err = c.Database.Exec(q, hash(url), url, statusCode, compressed.Bytes())
	return err
}

// Get is used to get back data from the cache
func (c DBCache) Get(url string) (statusCode int, content []byte, err error) {
	q := fmt.Sprintf(`SELECT status_code, content FROM "%s" WHERE id = $1`, c.getTable())
	row := c.Database.QueryRow(q, hash(url))

	var compressedContent []byte
	err = row.Scan(&statusCode, &compressedContent)
	if err != nil {
		return
	}

	// decompress data from memory
	compressedReader := bytes.NewReader(compressedContent)
	decompressedReader, err := zlib.NewReader(compressedReader)
	if err != nil {
		return
	}
	defer decompressedReader.Close()
	content, err = ioutil.ReadAll(decompressedReader)
	return
}

// Clear removes all records from the cache
func (c DBCache) Clear() error {
	q := fmt.Sprintf(`TRUNCATE "%s"`, c.getTable())
	_, err := c.Database.Exec(q)
	return err
}

func (c DBCache) getTable() string {
	if c.Table == "" {
		return "linguee_cache"
	}
	return c.Table
}

func hash(value string) []byte {
	sum := sha256.Sum256([]byte(value))
	return sum[:]
}
