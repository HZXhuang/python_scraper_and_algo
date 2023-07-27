import pandas as pd
from snownlp import SnowNLP, sentiment
from sklearn import metrics


# 利用模型分析所得情绪极性结果
def sentiment_analysis_to_result(text):
    s = SnowNLP(text)
    if s.sentiments >= 0.6:
        return 'positive'
    else:
        return 'negative'


# 利用模型分析所得预测分数
def sentiment_analysis_to_score(text):
    s = SnowNLP(text)
    return s.sentiments


# 利用模型分析所得预测标记
def sentiment_analysis_to_label(text):
    s = SnowNLP(text)
    if s.sentiments >= 0.6:
        return 1
    else:
        return 0


#  利用sklearn计算模型的性能指标accuracy(准确率）、precision(精确率）、recall(召回率)、f1score(F1值)
def model_other_target_test():
    f = open('model/waimai_10k.csv', 'r', encoding='utf-8')
    data = pd.read_csv(f)
    y_true = []
    y_pred = []
    record_num = data.shape[0]  # 返回行数
    #  遍历所有行
    for i in range(record_num):
        record = data.iloc[i, :]
        label = sentiment_analysis_to_label(record['review'])
        y_true.append(record['label'])
        y_pred.append(label)
    accuracy = metrics.accuracy_score(y_true, y_pred)
    precision = metrics.precision_score(y_true, y_pred, average='binary')
    recall = metrics.recall_score(y_true, y_pred, average='binary')
    f1score = metrics.f1_score(y_true, y_pred, average='binary')
    return accuracy,  precision, recall, f1score


#  利用sklearn计算模型的性能指标auc
def model_auc_test():
    f = open('model/waimai_10k.csv', 'r', encoding='utf-8')
    data = pd.read_csv(f)
    y_true = []
    y_pred = []
    record_num = data.shape[0]  # 返回行数
    #  遍历所有行
    for i in range(record_num):
        record = data.iloc[i, :]
        score = sentiment_analysis_to_score(record['review'])
        y_true.append(record['label'])
        y_pred.append(score)
    fpr, tpr, thresholds = metrics.roc_curve(y_true, y_pred, pos_label=1)
    auc = metrics.auc(fpr, tpr)
    return auc


if __name__ == '__main__':
    # emotion = sentiment_analysis_to_result('很难理解……(在)很多时候，你只是觉得自己在一片无路可走的荒野中徘徊。')
    # print(emotion)
    # auc = model_auc_test()  # 使用自己的snownlp所建模型，程序运行所得结果为0.8403282678101915
    # print(auc)
    accuracy, precision, recall, f1score = model_other_target_test()
    print(accuracy, precision, recall, f1score)   # 使用自己的snownlp所建模型，程序依次返回0.7809293401184617 0.6676427525622255 0.684 0.675722400592739
