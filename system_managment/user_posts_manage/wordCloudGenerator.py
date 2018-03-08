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
            mystopwords = stopwords.words('thai')
            wordcloud = WordCloud(margin=30,width=1920, height=1080,max_words=100,max_font_size=625,font_path='THSarabunNew.ttf', stopwords=mystopwords, background_color="white", regexp=r"[\u0E00-\u0E7Fa-zA-Z']+").generate(' '.join(word_tokenize(text,engine="newmm")))
            plt.figure()
            plt.imshow(wordcloud, cmap=plt.cm.gray, interpolation='bilinear')
            plt.axis("off")
            plt.show()
            plt.savefig('wordcloud_pic/%s.png' % uid, dpi=400)
        except:
            return "error"
        return "done"
