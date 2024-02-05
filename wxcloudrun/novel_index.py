# -*- coding: utf-8 -*-
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.sorting import FieldFacet
from jieba.analyse import ChineseAnalyzer
from run import app
import json
import os

# # 创建schema, stored为True表示能够被检索
# schema = Schema(title=TEXT(stored=True, analyzer=ChineseAnalyzer()),
#                 desc=TEXT(stored=True, analyzer=ChineseAnalyzer()),
#                 url=ID(stored=False),
#                 author=ID(stored=True)
#                 )

# 存储schema信息至indexdir目录
current_path = os.getcwd()
indexdir = os.path.join(current_path, 'wxcloudrun', 'indexdir/')
app.logger.info('\n\nindexdir=' + indexdir)
ix = open_dir(indexdir, indexname='indexname')

# 创建一个检索器
searcher = ix.searcher()

def search_by_keyword(keyword):
    # 单关键词搜索
    # 方式1： results = searcher.find("desc", "仙侠")
    # 方式2：parser = QueryParser("title", ix.schema).parse("手册")
    # 多关键词同时搜索
    parser = MultifieldParser(["title", 'desc'], ix.schema).parse(keyword)
    # 对结果进行排序
    facet = FieldFacet("title", reverse=True)
    # limit为搜索结果的限制，默认为10，None为不限制。sortedby为排序规则
    results = searcher.search(parser, limit=None, sortedby=facet, terms=True)
    return results

if __name__ == '__main__':
    keyword = "诡秘之主"
    results = search_by_keyword(keyword)
    app.logger.info('\n一共发现%d份文档。' % len(results))
    for i in range(min(10, len(results))):
        app.logger.info(json.dumps(results[i].fields(), ensure_ascii=False))
