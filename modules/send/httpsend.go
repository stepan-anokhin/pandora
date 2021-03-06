package send

import (
	"encoding/json"
	"net/http"
	"strings"

	"github.com/gocontrib/mediatype"
	log "github.com/sirupsen/logrus"
)

func JSON(w http.ResponseWriter, data interface{}, status ...int) error {
	w.Header().Set("Content-Type", mediatype.JSON)

	if len(status) > 0 {
		w.WriteHeader(status[0])
	}

	marshaller, ok := data.(json.Marshaler)
	if ok {
		b, err := marshaller.MarshalJSON()
		if err != nil {
			// TODO check whether it is possible to send error at this phase
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return err
		}
		_, err = w.Write(b)
		if err != nil {
			log.Errorf("http.ResponseWriter.Write fail: %v", err)
		}
		return err
	}

	err := json.NewEncoder(w).Encode(data)
	if err != nil {
		// TODO check whether it is possible to send error at this phase
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return err
	}

	return nil
}

func Error(w http.ResponseWriter, err error, status ...int) {
	if len(status) == 0 {
		errstr := err.Error()
		if strings.Contains(errstr, "not valid") || strings.Contains(errstr, "invalid") {
			status = []int{http.StatusBadRequest}
		} else if strings.Contains(errstr, "not found") {
			status = []int{http.StatusNotFound}
		} else {
			status = []int{http.StatusInternalServerError}
		}
	}

	data := &struct {
		Error string `json:"error"`
	}{
		Error: err.Error(),
	}
	_ = JSON(w, data, status...)
}
