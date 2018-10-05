import Immutable from 'immutable'
import { combineReducers } from 'redux'
import { handleActions } from 'redux-actions'

import { loadMessages, pushMessage } from './actions'

const ChatState = Immutable.Record({
  messages: Immutable.List(),
})

const chatReducer = handleActions(
  {
    [loadMessages]: (state, action) => {
      return state.set('messages', action.messages || Immutable.List())
    },

    [pushMessage]: (state, action) => {
      const messages = state.messages.push(action.message)
      return state.set('messages', messages)
    },
  },
  ChatState()
)

export default combineReducers({
  chat: chatReducer,
})