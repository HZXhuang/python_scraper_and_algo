from snownlp import sentiment


def model_train():
    sentiment.train('neg.txt', 'pos.txt')
    sentiment.save('weibo_sentiment_marshal.3')


if __name__ == '__main__':
    model_train()
