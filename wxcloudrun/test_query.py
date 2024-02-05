# -*- coding: utf-8 -*-
from whoosh.fields import *
from jieba.analyse import ChineseAnalyzer
import json

# 创建schema, stored为True表示能够被检索
schema = Schema(title=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                desc=TEXT(stored=True, analyzer=ChineseAnalyzer()),
                url=ID(stored=False)
                )