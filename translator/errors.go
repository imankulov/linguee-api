package translator

// LingueeError is a Linguee error which implements error interface
type LingueeError struct {
	Message    string  `json:"message"`
	StatusCode int     `json:"status_code"`
	Correction *string `json:"correction,omitempty"`
}

func (e *LingueeError) Error() string {
	return e.Message
}
