# -*- coding: utf-8 -*-
import os
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from jieba.analyse import ChineseAnalyzer
import json

def build():
    # 创建schema, stored为True表示能够被检索
    schema = Schema(title=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                    desc=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                    url=ID(stored=True)
                    )

    # 解析poem.csv文件
    with open('UID_TO_CONTENT.csv', 'r', encoding='utf-8') as f:
        texts = [_.strip().split('\t')[1:4] for _ in f.readlines() if len(_.strip().split('\t')) == 4]
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
        title, desc, url = texts[i]
        writer.add_document(title=title, desc=desc, url=url)
    writer.commit()

if __name__ == '__main__':
    # build()
    print('test')