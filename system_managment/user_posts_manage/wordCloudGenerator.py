from pythainlp import word_tokenize
from pythainlp.corpus import stopwords
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt



class WordCloudGenerator:
    def __init__(self):
        pass

    def generate(self, text, uid):
        try:
            wordcloud = WordCloud(width=1920, height=1080,font_path='THSarabunNew.ttf', stopwords = ' '.join(stopwords.words('thai')), background_color="white", regexp=r"[\u0E00-\u0E7Fa-zA-Z']+").generate(' '.join(word_tokenize(text,engine="newmm")))
            plt.figure()
            plt.imshow(wordcloud, cmap=plt.cm.gray, interpolation='bilinear')
            plt.axis("off")
            plt.show()
            plt.savefig('wordcloud_pic/%s.png' % uid, dpi=400)
        except:
            return "error"
        return "done"
