# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      yinz
#
# Created:     09/06/2013
#              22/09/2013 clean code
#-------------------------------------------------------------------------------

import os
os.chdir('d:/codemesh/pw-dict')


import codecs      # stdlib, read/write utf-8 files
import unicodedata # stdlib
import json        # stdlib
import urllib      # stdlib
import datetime    # stdlib


import epub2txt  # included, a modified version of epub2txt
import nltk      # need to be installed separately, NLP toolkit, for sentence parsing
import markdown2 # markdown to html

# epub file list
EPUBS = [ 'A Room of One\'s Own.epub',
'A Room with a View.epub',
'Frankenstein.epub',
'Heart of Darkness.epub',
'Love in the time of Cholera.epub',
'Martin Eden.epub',
'The Call of the Wild.epub',
'The Count of Monte Cristo.epub',
'The Great Gatsby.epub',
'The Metamorphosis.epub',
'The Moon and Sixpence.epub',
'The Stranger.epub'
        ]

EPUBS = [efile.strip() for efile in open('epub.list.txt')]

# My Clippings.txt file from Paperwhite
MY_CLIPPINGS = r'My Clippings after June 8.txt'


# API keys for www.wordreference.com
WR_KEYS = ['XXXXX', 'YYYYY']
WR_Key_Index = 0
WR_Queries = 0

# maximum sentence per document
MAX_SENTENCE_PER_DOC = 5

# Output file
WORD_BOOK_MD   = 'wordbook.md'
WORD_BOOK_HTML = 'wordbook.html'


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def words_from_my_clipping(lines):

    def strip_word(word):
        l = 0
        r = len(word) - 1
        while l<=r and not (word[l].isalpha()): l = l + 1
        while l<=r and not (word[r].isalpha()): r = r - 1
        single_word = True
        for i in range(l,r+1):
            if not word[i].isalpha():
                single_word = False
                break
        return (single_word, word[l:r+1])

    def get_word(b):
        ls = b.split('\n')
        #print ls[4]
        return strip_word(ls[4])[1]

    def highlight_block(b):
        try: #possible invalid blocks
            ls = b.split('\n')
            return len(ls)>2 and ls[2].find(u'Your Highlight')>=0 or ls[2].find(u'标注')>=0
        except:
            return False

    def word_block(b):
        ls = b.split('\n')
        return strip_word(ls[4])[0]

    text = ''.join(lines)
    blocks = text.split('==========')

    words = [get_word(b) for b in blocks if highlight_block(b) and word_block(b)]

    return unique(words)


def epub_sentences(epubfile):
    ''' get the text from an epub file, and use nltk to split the whole document
        into sentences
    '''
    text = epub2txt.epub2txt(epubfile).replace('\n', ' ')
    sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
    sents = sent_tokenizer.tokenize(text)
    return sents

def en2zh(word):
    ''' English words to Chinese meanings, using wordreference.com
    '''
    global WR_Queries, WR_Key_Index
    if WR_Queries > 550:
        if WR_Key_Index + 1 < len(WR_KEYS):
            WR_Key_Index += 1
            WR_Queries = 0
        else:
            return "Not Found"
    WR_Queries += 1


    url = 'http://api.wordreference.com/%s/json/enzh/%s'%(WR_KEYS[WR_Key_Index],word)

    #print url

    short_meanings = []

    try:
        j = json.loads(urllib.urlopen(url).read())
        meaning_groups = None
        if u'Entries' in j[u'term0']:
            meaning_groups = j[u'term0'][u'Entries']
        elif u'PrincipalTranslations' in j[u'term0']:
            meaning_groups = j[u'term0'][u'PrincipalTranslations']
        else:
            return "Not Found"

        group_id = 0
        while group_id >= 0:
            try:
                meaning = meaning_groups[str(group_id)][u'FirstTranslation'][u'term']
                short_meanings.append(meaning)
                group_id += 1
            except:
                group_id = -1
    except:
        pass

    if len(short_meanings)>0:
        return '; '.join(short_meanings)
    else:
        return "Not Found"


def main():
    with codecs.open(MY_CLIPPINGS, 'r', encoding='utf-8') as f:
        marked_words = words_from_my_clipping(f.readlines())
        sents_in_epubs = [(efile.replace('.epub',''), epub_sentences(efile)) for efile in EPUBS]
        word_set = set(marked_words)
        #print len(word_set)
        #770

        # { word : { booktitle: sentence list } }
        index_table = {}
        for word in word_set:
            index_table[word] = {}

        for book in sents_in_epubs:
            title, sents = book
            for sent in sents:
                words = nltk.word_tokenize(sent)
                for word in words:
                    if word in word_set:
                        if title not in index_table[word]:
                            index_table[word][title] = []
                        index_table[word][title].append(sent)


        # write the makrdown file
        with codecs.open(WORD_BOOK_MD, 'w', encoding ='utf-8') as g:
            now = datetime.datetime.now()
            date = '%d/%d/%d'%(now.year,now.month,now.day)
            g.write('Kindle Word Book %s\n=========\n\n'%date)

            for word in marked_words:
                word = unicodedata.normalize('NFKD', word).encode('ascii','ignore')
                g.write('[%s](http://dict.baidu.com/s?wd=%s)\n---------\n\n'%(word,word))
                g.write(u'* ' + en2zh(word))
                g.write('\n\n')

                for title in index_table[word]:
                    g.write('* ' + title + '\n')
                    for i, sent in enumerate(index_table[word][title]):
                        if i >= MAX_SENTENCE_PER_DOC:
                            break
                        sent_underline = sent.replace(word, '<u>'+word+'</u>') # u'<u>%s</u>'%word)
                        g.write(('  > %d/ %s\n\n'%(1+i,sent_underline)).decode('utf8') )

            g.write('\n')
            for word in marked_words:
                g.write('')

        # convert the markwon file to html
        with codecs.open(WORD_BOOK_HTML, 'w', encoding ='utf-8') as g:
            html_text = markdown2.markdown_path(WORD_BOOK_MD)
            html_head = '''<head>
  <title>Paperwhite Wordbook</title>
  <meta charset="utf-8">
  <meta name="author" content="Yin Zhu">

  <link href="https://fonts.googleapis.com/css?family=Arvo:400,700&subset=latin" rel="stylesheet" type="text/css">
  <link href="foghorn.css" rel="stylesheet">
</head>
'''
            g.write(html_head + html_text)


if __name__ == '__main__':
    main()
