# -*- coding: utf-8 -*-

# This module  implements functionallity for extracting meaningful 
# content from web-pages such HTML and XHTML. 
#

# Alternatives:
#	1. https://github.com/buriy/python-readability
#	2. https://github.com/gfxmonk/python-readability
#	3. http://www.minvolai.com/blog/decruft-arc90s-readability-in-python/

from lxml.html.clean import clean_html
import re


def get_meaningful_text(html):
	pass


#r1 = re.compile("^\s*$")
#r2 = re.compile(u"[a-zA-Zа-яА-Я]+")
#
#ttest = lambda text: re.search(r2, text)
#
#html_file_1 = "../data/html/ru/page3.html"
#html_file_2 = "text.html"
#
#html = open(html_file_1, "r").read().decode("UTF-8")
#html = clean_html(unicode(html))
#
#tree = []
#is_markup = False
#markup_count = 0
#loot = []
#text = ""
#
#out = open(html_file_2, "w")
#
#for ch in html:
#    
#    if ch == "<":
#        is_markup = True
#        tree.append(("TX", text))
#        text = ""
#        markup_count = 1
#        continue
#
#    if is_markup:
#        markup_count += 1
#    
#    if ch == ">":
#        is_markup = False
#        tree.append(("MK", markup_count))
#        continue
#        
#    if not is_markup:
#        text += ch
#        
#new_tree = []
#
#is_mk = tree[0][0] == "TX" and ttest(tree[0][1])
#
#for t,v in tree:
#    
#    if not (t == "TX" and not ttest(v)):
#    
#        if t == "MK" and not is_mk:
#            is_mk = True
#            new_tree.append(["MK", v])
#        elif t == "TX" and is_mk:
#            is_mk = False
#            new_tree.append(["TX", v])
#        else:
#            if t == "TX":
#                new_tree[-1][1] += " " + v
#            else:
#                new_tree[-1][1] += v
#    
#
# for x in new_tree:
#     print x
#
#tree = new_tree
#
#last = None
#        
#for i in xrange(1, len(tree) - 1):
#    
#    if tree[i][0] == "TX":
#        
#        
#        m_1 = i - 3 if i > 3 else i - 1
#        m_2 = i - 1
#        m_3 = i + 1
#        m_4 = i + 3 if i < len(tree) - 3 else i + 1
#        
#        t_1 = i - 2 if i > 2 else i
#        t_2 = i
#        t_3 = i + 2 if i < len(tree) - 2 else i
#        
#        mrkp_score = sum(map(lambda x: tree[x[0]][1] * x[1], [(m_1, 0.3), (m_2, 0.8), (m_3, 0.8), (m_4, 0.3)]))
#        text_score = sum(map(lambda x: len(tree[x[0]][1]) * x[1], [(t_1, 0.4), (t_2, 1.0), (t_3, 0.4)]))
#        
#        weight = float(text_score) / float(mrkp_score + text_score)
#        
#        if weight >= 0.25:
#            if not last or i - last < 10000:
#                last = i
#                out.write(("<p><b>{0:0.2f}</b>".format(weight) + tree[i][1]  + "</p>").encode("UTF-8"))
#            else:
#                print i - last
#        
        # out.write(("<p><b>{0:0.2f}</b>".format(weight) + tree[i][1]  + "</p>").encode("UTF-8"))
#        
#        
        # prev, next = tree[i + 1][1], tree[i - 1][1]
        # text_len = len(tree[i][1])
        # 
        # if (float(text_len) / float(prev + text_len + next)) > 0.85:
        # 
        #    out.write(("<p>" + tree[i][1]  + "</p>").encode("UTF-8"))
        #     
#
#
#
#
# open(html_file_2, "w").write(html.encode("UTF-8"))