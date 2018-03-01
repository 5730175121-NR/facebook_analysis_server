from pythainlp import word_tokenize
from pythainlp.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class WordCloudGenerator:
    def __init__(self):
        pass

    def generate(self, text, uid):
        wordcloud = WordCloud(font_path='THSarabunNew.ttf', stopwords = ' '.join(stopwords.words('thai')), background_color="white", regexp=r"[\u0E00-\u0E7Fa-zA-Z']+").generate(' '.join(word_tokenize(text)))
        plt.use('Agg')
        plt.figure(dpi=400)
        plt.imshow(wordcloud, cmap=plt.cm.gray, interpolation='bilinear')
        plt.axis("off")
        plt.savefig('wordcloud_pic/%s.png' % uid)
        try:
            # wordcloud = WordCloud(font_path='THSarabunNew.ttf', stopwords = ' '.join(stopwords.words('thai')), background_color="white", regexp=r"[\u0E00-\u0E7Fa-zA-Z']+").generate(' '.join(word_tokenize(text)))
            # plt.figure(dpi=400)
            # plt.imshow(wordcloud, cmap=plt.cm.gray, interpolation='bilinear')
            # plt.axis("off")
            # plt.savefig('wordcloud_pic/%s.png' % uid)
        except:
            return "error"
        return "done"
