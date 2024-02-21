# -*- coding: utf-8 -*-
import os
import re

from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.sorting import FieldFacet
import jieba
from jieba.analyse import ChineseAnalyzer
import jieba.analyse
import json
import html

# tp = r'\n.\n'
# a = """
# 你好：
# 我
# 无语
# """
# x = re.findall(tp, a)

STOPWORDS = [a for a in '，、。！？；：“”‘’（）【】《》【】……—·～']
jieba.load_userdict('indexdata/stopwords.dict.txt')
jieba.analyse.set_stop_words('indexdata/stopwords.dict.txt')
BAD_SENTENCE_PATTERN = [
    r'群.*\d.*\d.*\d.*\d.*\d.*\d.*\d'
]
def flat_sentence(sentence):
    # 特殊字符过滤
    for pattern in BAD_SENTENCE_PATTERN:
        matches = re.findall(pattern, sentence)
        if matches:
            return ''
    return sentence
    # while '  ' in s.strip():
    #     s = s.replace('  ', ' ')


def replace_html_entities(text):
    # 定义需要替换的特殊字符和对应的替换值
    html_entities = {
        '<br>': '\n',
        '<br />': '\n',
        '<p>': '\n',
        '</p>': '\n'
    }
    pattern = re.compile('|'.join(html_entities.keys()))
    replaced_text = pattern.sub(lambda m: html_entities[m.group(0)], text)

    return replaced_text

def is_meaningful_line(text):
    pattern = r'^[^\u4e00-\u9fa5a-zA-Z.]+$'
    if re.search(pattern, text):
        return False
    else:
        return True

def flat_content(title, text):
    # 网页特殊字符替换
    text1 = html.unescape(text)
    text1 = html.unescape(text1)
    text1 = html.unescape(text1)
    text1 = replace_html_entities(text1)

    # 过滤明显有问题的行
    text1 = text1.replace('…', '…\n')
    text1 = text1.replace('...', '...\n')
    text1 = text1.replace('※※※', '※※※\n')
    text1 = text1.replace('===', '===\n')
    text1 = text1.replace('___', '___\n')
    text1 = text1.replace('---', '---\n')
    text1 = text1.replace('＊＊＊', '＊＊＊\n')
    text1 = text1.replace('———', '———\n')
    text1 = text1.replace('~~~', '~~~\n')
    lines = [a for a in text1.split('\n') if is_meaningful_line(a)]
    text2 = '\n'.join(lines)

    # # 处理换行
    # tp = r'\n..\n'
    # tp = r'\n'
    # x = re.findall(tp, text2)
    # if x:
    #     print(x)
    #     print("\n\n\n{}\n=== before【{}】\n=== after 【{}】".format(title, text, text2))

    # 断句

    # 分句子处理
    sentences = [e.strip() for e in re.split(r'[。！？\n\r]', text2)]
    sentences = [flat_sentence(e.strip()) for e in sentences]
    sentences = [a for a in sentences if a != '']
    text3 = '\n'.join(sentences).strip()

    # tp = r'\n.*\n'
    # x = re.findall(tp, text)
    # if x:
    #     print("\n\n{}\n《{}》\n=== before【{}】\n=== after 【{}】".format(x, title, text, text3))

    return '；'.join(sentences)
    # # 分句子
    # seg_list = jieba.cut(text)
    # word1 = [w for w in seg_list]
    # word2 = [word1[0]]
    # for seg in word1[1:]:
    #     if seg != word2[-1]:
    #         word2.append(seg)
    # return word2

    # # 过滤停用词和单个字符
    # filtered_words = [word for word in seg_list if word not in STOPWORDS and len(word) > 1]
    # text = '|'.join(filtered_words)
    # return '\n'.join(arr2).strip()
def parse_one_detail(line):
    if line.strip() == 'ERROR':
        return {}
    book_json = json.loads(line.strip())
    book = book_json['state']['Book']
    bookInfo = book['bookInfo']
    title = bookInfo['title']
    className = bookInfo['classInfo']['className']
    author = bookInfo['author']
    score = bookInfo['score']
    scorerCount = bookInfo['scorerCount']
    scoreDetail = bookInfo['scoreDetail']
    tags = bookInfo['tags']
    tags.append(className.strip())
    tags = list(set([t.strip() for t in tags]))
    tags_as_str = ','.join(tags)
    status = bookInfo['status']  # 0 连载中，1 已完结
    introduction = bookInfo['introduction']
    # a = introduction.strip()
    # b = flat_content(title, a)
    # print("\n\n\n=== before【{}】\n=== after 【{}】".format(a, b))

    countWord = bookInfo['countWord']
    cover = bookInfo['cover']
    # scores = book['scoreDetail']
    # tags = book['tags']

    sources = book['bookSource']
    jump_link = sources[0]['phonePage'] if len(book['bookSource']) > 0 else '暂无链接'
    booklists = book['booklistsResult']['booklists']  # 只有第一页，最多20篇
    # assert len(booklists) == book['booklistsResult']['total']
    assert len(booklists) <= 20

    comments = book['commentsResult']['comments']
    # assert len(comments) == book['commentsResult']['total']
    assert len(comments) <= 20  # 只有第一页，最多20篇


    return {
        "title": title.strip(),
        "author": author.strip(),
        "score": score,
        "scorerCount": scorerCount,
        "className": className.strip(),
        "tags": tags_as_str.strip(),
        "desc": flat_content(title, introduction),
        "url": jump_link
    }

def load_books():
    uid_list = []
    books = []
    indexdata_path = 'indexdata'
    for root, dirs, files in os.walk(indexdata_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('_DETAIL.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for _ in f.readlines():
                        book = parse_one_detail(_)
                        if 'title' in book:
                            uid = '{}###{}'.format(book['title'], book['author'])
                            if not uid in uid_list:
                                books.append(book)
                                uid_list.append(uid)
                            else:
                                print('find ' + uid)
                print('loaded from {}, total document count {}.'.format(file_path, len(books)))
    return books

def build(books):
    jieba.load_userdict("./indexdata/semantic_labels.dict.txt")

    # 创建schema, stored为True表示能够被检索
    schema = Schema(
        title=TEXT(stored=True),
        author=ID(stored=True),
        score=NUMERIC(stored=True, sortable=True),
        scorerCount=NUMERIC(stored=True, sortable=True),
        className=ID(stored=True),
        tags=KEYWORD(stored=True, analyzer=ChineseAnalyzer()),
        desc=TEXT(stored=True, analyzer=ChineseAnalyzer()),
        url=ID(stored=True)
    )
    # 存储schema信息至indexdir目录
    indexdir = 'indexdir/'
    if not os.path.exists(indexdir):
        os.mkdir(indexdir)
        # 使用create_in方法创建索引，index_path为索引路径，schema为前面定义的索引字段，indexname为索引名称（根据需要进行修改）
        ix = create_in(indexdir, schema=schema, indexname='indexname')

    writer = ix.writer()
    for book in books:
        writer.add_document(
            title=book['title'],
            author=book['author'],
            score=book['score'],
            scorerCount=book['scorerCount'],
            className=book['className'],
            tags=book['tags'],
            desc=book['desc'],
            url=book['url']
        )
    writer.commit()

def test_query(keyword):
    EMOJI_ALL = '🧠👀👁️🦾✍️🦴🫁👽👻👁️‍🗨️🐾🐈‍⬛🪶🕸️🕷️🏫🏥🌁🌄🌃🌆🌉🎪🎡🚨🚂🚇🧳🛸🛎️⌚⏳🕘🕰️🎃🎐🃏🧸🪁🪆🪄🎨👓👜👝💾🎞️📹📺📼📷🎥🔍🔎🔦🕯️📃📜📰🗞️✉️📦📮🖋️📆📐💼📎🗄️🔒🗝️🧪💉🩸💊'
    EMOJI_BY_CLASSNAME = {
        "玄幻": '👹🪽⛩️☘️🍀🍂🏔️🌋🏜️🗻🏝️🏛️🏯🏰⛪🕌🕋🕍🛕♨️🌪️🌑🎎🎏🥋🎴🔮🎭👑👘📿🥻🪭🪇🪕🏮🕯️🪔📜📕💰💸🪙⚔️🏹🗡️🛡️🪝🧪🪞⚰️🗿⚱️🧿🪦🪬☪️☯️☮️🛐♈♌♋⚜️⚕️🔰🔱💠🏴‍☠️🥷'
        , "悬疑": EMOJI_ALL
    }

    def _get_emoji(className):
        import random
        flag = '👉'
        if className in EMOJI_BY_CLASSNAME:
            flag = EMOJI_BY_CLASSNAME[className][random.randrange(len(EMOJI_BY_CLASSNAME[className]))]
        return flag

    current_path = os.getcwd()
    indexdir = os.path.join(current_path, 'indexdir/')
    ix = open_dir(indexdir, indexname='indexname')
    searcher = ix.searcher()
    parser = MultifieldParser(["title", "author", "desc"], ix.schema).parse(keyword)
    facet = FieldFacet("scorerCount", reverse=True)
    # limit为搜索结果的限制，默认为10，None为不限制。sortedby为排序规则
    results = searcher.search(parser, limit=None, sortedby=facet, terms=True)
    print('\n一共发现{}份【{}】文档。'.format(len(results), keyword))
    for i in range(min(9999, len(results))):
        # 标题
        print('《{}》{}著。{}。{}。评分:{}。{}'.format(
            results[i].fields()['title'],
            results[i].fields()['author'],
            _get_emoji(results[i].fields()['className']),
            # results[i].fields()['className'],
            results[i].fields()['tags'],
            results[i].fields()['score'],
            results[i].fields()['desc'])
        )
        # print((json.dumps(results[i].fields(), ensure_ascii=False)))
    ix.close()

if __name__ == '__main__':
    # books = load_books()
    # build(books)
    test_query('凡人修仙传')
    test_query('遮天')
    test_query('爱潜水的乌贼')
    test_query('诡秘')
    test_query('赞美愚者')
    test_query('愚者先生')
    test_query('诡秘之主')
    test_query('斗破苍穹')
    test_query('天蚕土豆')
    test_query('斗破')
    test_query('烽火戏诸侯')
    test_query('雪中悍刀行')


    # test_query('都重生了谁谈恋爱啊')
    # test_query('出名太快怎么办')
    # test_query('万古神帝')
    # test_query('斗气')
    # test_query('史上最牛宗门')
    #
    # test_query('总裁')
    # test_query('霸总')
    # test_query('霸道总裁')
    # test_query('贱人')
    # test_query('宫斗')
    print('test')