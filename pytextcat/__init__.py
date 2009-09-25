# Copyright (C) 2009  David Roberts <d@vidr.cc>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA

import os
import re

class LanguageModel(object):
    def __init__(self, inp, encoding=None):
        if isinstance(inp, basestring):
            self.create(inp, encoding)
        elif type(inp) is file:
            self.load(inp, encoding)
        else:
            raise TypeError
    
    max_ngrams = 400
    
    def create(self, text, encoding=None):
        """Create a language model from the given text."""
        
        # calculate frequencies of n-grams for 1 <= n <= 5
        freq = {}
        for word in re.split('[\d\s]+', text):
            word = "_%s_" % word
            word_len = len(word)
            for i in xrange(word_len):
                for j in xrange(i+1, min(word_len, i+5) + 1):
                    substr = word[i:j]
                    freq[substr] = freq.get(substr, 0) + 1
        
        # sort in decreasing frequency
        sort = sorted([(n,s) for s,n in freq.iteritems()], reverse=True)
        
        # store at most top max_ngrams ngrams
        self.ngram = [s for _,s in sort[:self.max_ngrams]]
    
    def load(self, f, encoding=None):
        """Load language model from the given .lm file f."""
        self.ngram = []
        for line in f:
            ngram,_ = line.split()
            self.ngram.append(ngram)
    
    def compare(self, other):
        """Compare this reference language model with the other unknown
        language model and return a rank-order. A lesser rank indicates a
        closer match."""
        rank = 0
        for i,ngram in enumerate(other.ngram):
            if ngram in self.ngram:
                rank += abs(i - self.ngram.index(ngram))
            else:
                rank += self.max_ngrams
        return rank

lm_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lm'))
languages = {}
def load_lm():
    for fname in os.listdir(lm_dir):
        bname = fname[:-3]
        if '-' in bname:
            lang, encoding = tuple(bname.split('-',1))
            # TODO: actually do something with the encoding
            # <http://docs.python.org/library/codecs.html#standard-encodings>
        else:
            lang = bname
            encoding = None
        languages[lang,encoding] \
            = LanguageModel(open(os.path.join(lm_dir, fname)), encoding)
load_lm()

def classify(text):
    """Return a list of tuples (score,(language,encoding)) sorted in increasing
    order. Scores are scaled such that the score of the best language is 1.0.
    A lower score indicates a better match."""
    unknown = LanguageModel(text[:1024]) # we don't need more than 1KB of text
    ranks = sorted([(lm.compare(unknown), lang)
                    for lang,lm in languages.iteritems()])
    a = float(ranks[0][0])
    return [(r/a ,l) for r,l in ranks]
