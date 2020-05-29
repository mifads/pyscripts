#!/usr/bin/env python3
# See https://bibtexparser.readthedocs.io/en/master/tutorial.html
# codec? consider https://github.com/pexpect/pexpect/issues/401
""" Draft zero of code to read Dave's Refs.bib file and allow search 
  and pdf viewing """
import bibtexparser
import subprocess
import sys
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

# Failed
#import bibtexparser.bibtexexpression.BibtexExpression as be
#be.set_string_name_parse_action(None)

parser = BibTexParser(interpolate_strings=False)
parser.ignore_nonstandard_types= False # ?
parser.common_strings = True
#parser.interpolate_strings = False # None


homedir='/home/davids/'
texdir =  homedir + 'Documents/D_Articles/'

testr='Documents/TeX/testr.bib'
testr='Documents/TeX/fixed.testr.bib'  # fixtext2
testr=homedir+'Documents/TeX/Refs.bib'

test_export = False # True

def query_user():
   search_terms = input('Give search terms:') # eg QQDEP, 2014
   search_terms = search_terms.split()
   print(search_terms)
   print(len(bb.entries_dict)) # 6297
   return search_terms

def scan_for_pdfs(search_terms):
   pdfs = []
   for key in bb.entries_dict:
     entry = bb.entries_dict[key]
     copy  = entry.copy()
     copy.pop('abstract',None)

     if all ( x in str(copy) for x in search_terms):
       if 'file' in entry:
         print('MATCH:', len(pdfs), key, copy['file']) 
         pdf = copy['file'].split(':')[1]
         if pdf.startswith('/home/'):
           pdfs.append( pdf )
         else:
           pdfs.append( texdir + pdf )
       else:
         print('NO PDF:', key )
   return pdfs

def process_pdfs(pdfs):

   retcode = 'X'
   if len(pdfs) > 0:
      while True:
        ans = input('Open pdf? Give number, type n for new search, x to exit: ')

        if ans == 'x':
          sys.exit('Exit called')
        elif ans =='n':
          retcode = 'N'
          break
        elif ans.isalpha(): 
          print('Illegal answer: %s !! Need n, x or number. Try again' % ans)
          continue
        else:
          ipdf = int(ans)
          if ipdf >= len(pdfs):
            print('NUMBER TOO HIGH: %s !! Try again' % ans)
            continue
          else:
            print('Opens pdf number', ipdf)
            subprocess.call('evince %s' %  pdfs[int(ipdf)],shell=True)
            retcode = 'C'
   return retcode

def test_bibexport():
     a= bb.entries_dict['Yttri:Urban']
     db=BibDatabase()
     db.entries = [a]
     writer=BibTexWriter()
     with open('testoutbib.bib','w') as bibfile:
       bibfile.write(writer.write(db))
     sys.exit()

with open(testr,encoding='utf-8') as bfile:
#with open(testr,encoding='latin-1') as bfile:
   bb=bibtexparser.load(bfile, parser)

   if test_export: test_bibexport()

   while True:
     search_terms = query_user()

     pdfs = scan_for_pdfs(search_terms)

     if len(pdfs) == 0:
        print('Nothing found. Try again!')
        continue # New search

     p = process_pdfs(pdfs)
     if p == 'N':
        continue # New search
     else:
        sys.exit('Finished')
      
sys.exit('OOPS Shouldnt get here')

#print(bb.strings)  # e.g. acp = 
#   print(bb.entries_dict['Gon2013'] )
#   g= bb.entries_dict['Gon2013']
#   a= bb.entries_dict['Yttri:Urban']
#   print('doi: ' , g['doi'])

#with open('DFILE.bib','w') as dfile:
#  bibtexparser.dump(bb, dfile)


db = BibDatabase()
db.entries = [ g, a ] 
db.entries = bb.entries
print('NOWBB', len(bb.entries_dict)) # 6297
writer = BibTexWriter()
writer.indent = '    '
writer.common_strings = False
with open('BTEST.bib','w') as bibfile:
   bibfile.write(writer.write(db))

