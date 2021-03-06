package dgraph

import (
	"context"
	"io/ioutil"
	"os"

	"github.com/dgraph-io/dgo/v2/protos/api"
	log "github.com/sirupsen/logrus"
)

func InitSchema() {
	// TODO configurable path to schemas
	initSchema("./schema.txt")
	initGraphqlSchema("./schema.gql")
}

func initSchema(path string) {
	schema, err := ioutil.ReadFile(path)
	if err != nil {
		log.Errorf("read schema fail: %v", err)
		return
	}

	ctx := context.Background()

	dg, close, err := NewClient(ctx)
	if err != nil {
		log.Errorf("cannot init dgraph schema: %v", err)
		// TODO retry after few seconds
		return
	}
	defer close()

	ctx = WithAuthToken(ctx)

	err = dg.Alter(ctx, &api.Operation{
		Schema: string(schema),
	})
	if err != nil {
		log.Errorf("init %s fail: %v", path, err)
	}
}

func initGraphqlSchema(path string) {
	schema, err := os.Open(path)
	if err != nil {
		log.Errorf("read schema fail: %v", err)
		return
	}

	// init graphql schema via HTTP call for now
	rc := NewRestClient()
	err = rc.PostData("/admin/schema", "text/plain", schema, nil)
	if err != nil {
		log.Errorf("init of graphql schema fail: %v", err)
		return
	}

	log.Info("graphql schema initialized")
}
