# Handle natural language
import re
with open('miracle-in-the-andes.txt', 'r', encoding='utf-8') as file:
    book = file.read()

    # Find all 'Character'
    # pattern = re.compile('Chapter \d+')
    # print(re.findall(pattern, book))

    # Find sentences contain 'love'
    # pattern2 = re.compile('[^.]*[^a-zA-Z]+love[^a-zA-Z]+[^.]*')
    # findings = re.findall(pattern2, book)
    # print(findings)

    # Find paragraphs contain 'love'
    # pattern_paragraph = re.compile('[^\n]+love[^\n]+')
    # findings_paragraph = re.findall(pattern_paragraph, book)
    # print(findings_paragraph)

    # Find the most used words
    # pattern3 = re.compile('[a-zA-Z]+')
    # findings2 = re.findall(pattern3, book.lower())
    # d = {}
    # for word in findings2:
    #     if word in d.keys():
    #         d[word] = d[word] + 1
    #     else:
    #         d[word] = 1
    # max_key = max(d, key=d.get)
    # print(max_key)

    # Get title of chapter
    # pattern = re.compile('([a-zA-Z ,]+)\n\n')
    # findings = re.findall(pattern, book)
    # print(findings)

    # Find occurrence of give word, else exist return msg
    def find(w):
        """
            Return occurrence of word
        :param w: word
        :type w: str
        :return: occurrence
        :rtype: int
        """
        pattern = re.compile('[a-zA-Z]+')
        findings = re.findall(pattern, book.lower())
        d = {}
        for word in findings:
            if word in d.keys():
                d[word] = d[word] + 1
            else:
                d[word] = 1
        try:
            return d[w]
        except:
            return f'The book does not contain the word "{w}"'

    # print(find('love'))
