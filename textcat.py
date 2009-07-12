#!/usr/bin/python
## Copyright (C) 2009  David Roberts <dvdr18@gmail.com>
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
## 02110-1301, USA.

import sys

import pytextcat

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h','--help'):
        print """
%(0)s [-v] [FILE]...

Determine the language of each FILE.

If -v is present, then full ranking information will be given for each file.

Examples:
%(0)s test_texts/*.txt
%(0)s -v README
        """.strip() % {'0': sys.argv[0]}
        return
    elif sys.argv[1] == '-v':
        verbose = True
        fnames = sys.argv[2:]
    else:
        verbose = False
        fnames = sys.argv[1:]
    
    for fname in fnames:
        text = open(fname).read(1024)
        ranks = pytextcat.classify(text)
        ans = []
        
        for i,(rank,(lang,enc)) in enumerate(ranks):
            lang = lang.replace('_',' ').title()
            if enc: lang = "%s (%s)" % (lang,enc)
            if rank < 1.05: ans.append(lang)
            rank = int(100*rank) - 100
            ranks[i] = (lang,rank)
        
        print fname, "is probably",
        if len(ans) == 1:
            print ans[0]
        elif len(ans) == 2:
            print "%s or %s" % (ans[0], ans[1])
        else:
            print "%s, or %s" % (', '.join(ans[:-1]), ans[-1])
        
        if verbose:
            print
            print "Full ranking information is given below:"
            print
            print "Language                        Score"
            for lang,rank in ranks:
                print "%s%s%2d%% worse than best score" \
                    % (lang,' '*(32-len(lang)),rank)
            print
            print
if __name__ == '__main__': main()
