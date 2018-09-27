package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/gocontrib/auth"
)

func makeUserStore() auth.UserStore {
	return &UserStore{}
}

type UserStore struct {
}

// TODO support user roles

func (s *UserStore) ValidateCredentials(ctx context.Context, username, password string) (auth.User, error) {
	query := fmt.Sprintf(`{
        users(func: has(%s)) @filter(eq(email, %q) OR eq(login, %q)) {
			uid
			name
			email
            checkpwd(password, %q)
        }
	}`, userLabel(), username, username, password)

	return s.FindUser(ctx, query, username, true)
}

func (s *UserStore) FindUserByID(ctx context.Context, userID string) (auth.User, error) {
	query := fmt.Sprintf(`{
        users(func: uid(%s)) @filter(has(%s)) {
			uid
			name
			email
        }
	}`, userID, userLabel())

	return s.FindUser(ctx, query, userID, false)
}

func userLabel() string {
	return nodeLabel("user")
}

func (s *UserStore) Close() {
}

func (s *UserStore) FindUser(ctx context.Context, query, userID string, checkPwd bool) (auth.User, error) {
	client, err := newDgraphClient()
	if err != nil {
		return nil, err
	}

	txn := client.NewTxn()
	defer txn.Discard(ctx)

	resp, err := txn.Query(ctx, query)
	if err != nil {
		return nil, err
	}

	var result struct {
		Users []struct {
			ID       string `json:"uid"`
			Name     string `json:"name"`
			Email    string `json:"email"`
			Password []struct {
				CheckPwd bool `json:"checkpwd"`
			} `json:"password"`
		} `json:"users"`
	}
	err = json.Unmarshal(resp.GetJson(), &result)
	if err != nil {
		return nil, err
	}

	if len(result.Users) == 0 {
		return nil, fmt.Errorf("user not found: %s", userID)
	}

	user := result.Users[0]
	if checkPwd && !user.Password[0].CheckPwd {
		return nil, fmt.Errorf("wrong password: %s", userID)
	}

	return &UserInfo{
		ID:    user.ID,
		Name:  user.Name,
		Email: user.Email,
	}, nil
}

type UserInfo struct {
	ID    string
	Name  string
	Email string
	Admin bool
}

func (u *UserInfo) GetID() string    { return u.ID }
func (u *UserInfo) GetName() string  { return u.Name }
func (u *UserInfo) GetEmail() string { return u.Email }
func (u *UserInfo) IsAdmin() bool    { return u.Admin }
