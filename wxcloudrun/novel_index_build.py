# -*- coding: utf-8 -*-
import os
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.sorting import FieldFacet
from jieba.analyse import ChineseAnalyzer
import json

def build():
    # 创建schema, stored为True表示能够被检索
    schema = Schema(title=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                    desc=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                    url=ID(stored=True),
                    author=ID(stored=True)
                    )

    ITEM_LINE_SPLIT = "###"
    texts = []
    # 解析poem.csv文件
    with open('UID_TO_CONTENT.csv', 'r', encoding='utf-8') as f:
        for _ in f.readlines():
            if len(_.strip().split(ITEM_LINE_SPLIT)) == 5:
                texts.append(_.strip().split(ITEM_LINE_SPLIT)[1:5])
        print(texts)

    # 存储schema信息至indexdir目录
    indexdir = 'indexdir/'
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
        # 使用create_in方法创建索引，index_path为索引路径，schema为前面定义的索引字段，indexname为索引名称（根据需要进行修改）
        ix = create_in(indexdir, schema=schema, indexname='indexname')

    #
    # 按照schema定义信息，增加需要建立索引的文档
    writer = ix.writer()
    for i in range(1, len(texts)):
        title, desc, url, author = texts[i]
        writer.add_document(title=title, desc=desc, url=url, author=author)
    writer.commit()

def test_query(keyword = '一品狂医'):
    current_path = os.getcwd()
    indexdir = os.path.join(current_path, 'indexdir/')
    ix = open_dir(indexdir, indexname='indexname')
    searcher = ix.searcher()
    parser = MultifieldParser(["title", 'desc', 'author'], ix.schema).parse(keyword)
    facet = FieldFacet("title", reverse=True)
    # limit为搜索结果的限制，默认为10，None为不限制。sortedby为排序规则
    results = searcher.search(parser, limit=None, sortedby=facet, terms=True)
    print('\n一共发现%d份文档。' % len(results))
    for i in range(min(10, len(results))):
        print((json.dumps(results[i].fields(), ensure_ascii=False)))
    ix.close()

if __name__ == '__main__':
    # build()
    # test_query('都重生了谁谈恋爱啊')
    # test_query('出名太快怎么办')
    # test_query('万古神帝')
    # test_query('斗气')
    # test_query('万古剑神')
    # test_query('修真路')
    # test_query('入修真路')
    print('test')