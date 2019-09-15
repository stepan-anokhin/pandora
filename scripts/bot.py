#!/usr/bin/env python

import sys
import os
import cambridge
import api
import re
import json

__dir__ = os.path.dirname(os.path.realpath(__file__))
TAGS = {}  # friendly tag name to uid
TERMS = {}  # key=text@lang, value=uid
__next_id__ = 1


def next_id(prefix):
    global __next_id__
    id = prefix + str(__next_id__)
    __next_id__ += 1
    return id


def is_word(s):
    return True if re.match(r'^\w+$', s) else False


def commit_edges(edges):
    pass


# TODO refactor as generator
def read_words():
    with open(os.path.join(__dir__, 'us1000.txt'), 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')
        lines = [s.strip() for s in lines]
        return [s for s in lines if len(s) > 0]


def define_term(data, tags=[]):
    text = data['text']
    tags.append('word' if is_word(text) else 'phrase')
    id = next_id('term')
    tag_ids = [TAGS[t] for t in tags if t in TAGS]

    res = api.nquads(data, id)
    res.extend([api.nquad(id, 'tag', t) for t in tag_ids])
    # TODO commit term to dgraph
    key = '{0}@{1}'.format(data['text'], data['lang'])
    TERMS[key] = id
    print('\n'.join(res))
    return id


def define_word(word, lang='en'):
    def proc_def(term_id, dfn):
        def_id = define_term({
            'text': dfn['text'],
            'lang': lang,
        })
        edges = [[term_id, 'definition', def_id],
                 [def_id, 'definition_of', term_id]]
        # TODO remove note in brackets
        trans = dfn['trans']['text']
        tran_lang = dfn['trans']['lang']
        for tran in trans.split(','):
            tran_id = define_term({
                'text': tran.strip(),
                'lang': tran_lang,
            })
            edges.extend([
                [term_id, 'translated_as', tran_id],
                [tran_id, 'translated_as', term_id],
            ])
        commit_edges(edges)

    print('..."{0}"...'.format(word))
    cam = cambridge.translate(word, lang)
    # print(json.dumps(cam, sort_keys=True, indent='  '))

    # get tags from cambridge (noun, verb, adjective, etc)
    tags = []
    data = {'text': word, 'lang': lang}
    for pron in cam['prons']:
        data['transcript@{0}'.format(pron['region'])] = pron['ipa']
    term_id = define_term(data, tags)
    for phrase in cam['phrases']:
        if phrase['text'] == word:
            # direct translation
            proc_def(term_id, phrase['defs'][0])
        else:
            # common phrase with definitions
            phrase_id = define_term({
                'text': phrase['text'],
                'lang': lang,
            })
            commit_edges([[term_id, 'in', phrase_id],
                          [phrase_id, 'of', term_id]])
            for dfn in phrase['defs']:
                proc_def(phrase_id, dfn)


# TODO define tags
# TODO define words with definitions, examples (in)
# TODO define audio and visual edges


def main():
    if len(sys.argv) > 1:
        define_word(sys.argv[1])
        return
    for word in read_words():
        define_word(word)


if __name__ == '__main__':
    main()