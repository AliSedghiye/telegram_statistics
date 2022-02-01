import json
from collections import Counter, defaultdict
from os import path
from pathlib import Path
from typing import Union

from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, sent_tokenize, word_tokenize
from src.data import DATA_DIR
from wordcloud import WordCloud


class chatstatistics:
    def __init__(self , json_file:Union[str, Path]):
        with open(DATA_DIR / json_file) as f:
            self.chat_data = json.load(f)

        stop_word = open(DATA_DIR / 'stopwords.txt').readlines()
        self.stop_word = list(map(str.strip , stop_word))
        self.normalizer = Normalizer()
        self.stop_word = list(map(self.normalizer.normalize , self.stop_word))

    @staticmethod
    def rebuild_message(sub_message):
        msg_content = ''
        for sub_msg in sub_message:
            if isinstance(sub_msg , str):
                msg_content += sub_msg
            elif 'text' in sub_msg:
                msg_content += sub_msg['text']

        return msg_content
    
    def generate_statistics(self):

        is_question = defaultdict(bool)
        for msg in self.chat_data['messages']:
            if not isinstance(msg['text'] , str):
                msg['text'] = self.rebuild_message(msg['text'])
            sentences = sent_tokenize(msg['text'])
            for sentence in sentences:
                if ('?' not in sentence) and ('؟' not in sentence):
                    continue

                is_question[msg['id']] = True
                break

        users = []
        for msg in self.chat_data['messages']:

            if not msg.get('reply_to_message_id'):
                continue

            if is_question[msg['reply_to_message_id']] is False:
                continue

            users.append(msg['from'])

        return dict(Counter(users).most_common())



    def generate_word_cloud(self , save_dir:Union[str, Path]):

        text_content = ''
        for msg in self.chat_data['messages']:
            if type(msg['text']) is str:
                text_content += f" { msg['text']}"

        token = word_tokenize(text_content)
        token = list(filter(lambda item: item not in self.stop_word , token))
        
        tokens = []
        for tk , num in Counter(token).most_common()[:8000]:
            tokens += [tk] * num

        filter_text_content = ''.join(tokens)
        filter_text_content = self.normalizer.normalize(filter_text_content)

        filter_text_content = arabic_reshaper.reshape(filter_text_content)
        filter_text_content = get_display(filter_text_content)

        text = filter_text_content
        wordcloud = WordCloud(
            font_path=str(DATA_DIR/'Vazir.ttf'),
             background_color='white',
             width=1000,
             height=1000,
             max_font_size=200,
             ).generate(text)

        wordcloud.to_file(Path(save_dir) / 'wordcloud.png')
    print('Done!')


sample = chatstatistics('group_data.json')
sample.generate_word_cloud(DATA_DIR)

#print(sample.generate_statistics())
