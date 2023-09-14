from sql_dao.sql_utils import insert_recommend_work, db_engine
import pandas as pd
import re
from sqlalchemy import text
from recommend.CB import *
from recommend.userCF import *


# 输出推荐给该用户的节目列表
# max_num:最多输出的推荐节目数
def insert_to_db(userId, recommend_items_sorted, max_num, conn):
    count = 0
    for item, degree in recommend_items_sorted:
        count += 1
        insert_recommend_work(userId, item, degree, conn)
        if count == max_num:
            break


def recommend():
    conn = db_engine.connect()
    # 读取所有的作品
    monitor_work_df = pd.read_sql("select id, name, category, labels, postTime from monitor_work", conn)
    all_labels = []  # 所有的标签
    monitor_work_df['labels'].apply(lambda x: all_labels.extend(re.split(' +', x.strip())))
    all_labels = set(all_labels)
    all_labels = list(all_labels)
    label_num = len(all_labels)
    # 提取所有的作品id
    all_work_names = monitor_work_df['id'].values
    data_mat = []
    for i in range(len(all_work_names)):
        vector = [0] * label_num
        label_names = re.split(' +', monitor_work_df.iloc[i, 3].strip())
        for label in label_names:
            if len(label.strip()) == 0:
                continue
            loc = all_labels.index(label)
            vector[loc] = 1
        data_mat.append(vector)

    # 各个作品的标签矩阵
    work_labels_df = pd.DataFrame(data=data_mat, index=all_work_names, columns=all_labels)
    user_record_df = pd.read_sql("select * from user_recent_record;", conn)
    workId_lst = user_record_df['workId'].unique().tolist()
    userId_lst = user_record_df['userId'].unique().tolist()
    work_num = len(workId_lst)
    user_work_data = []
    for userId in userId_lst:
        row_ = [0] * work_num
        query_df = user_record_df.query('userId == {}'.format(userId))  # 筛选userId用户的浏览记录
        max_cnt = query_df['visitCounts'].max()  # 用户的最大浏览次数
        for i in query_df.index:
            loc = workId_lst.index(query_df.loc[i, 'workId'])
            row_[loc] = query_df.loc[i, 'visitCounts'] / max_cnt
        user_work_data.append(row_)

    user_work_df = pd.DataFrame(data=user_work_data, index=userId_lst, columns=workId_lst)

    monitor_work_less = monitor_work_df[['id', 'labels']]
    monitor_work_less.columns = ['workId', 'labels']
    user_record_df_merge = pd.merge(user_record_df, monitor_work_less, how='inner')
    user_record_df_merge_unique = user_record_df_merge[['workId', 'labels']].drop_duplicates()
    df_data = []
    for i in user_record_df_merge_unique.index:
        row_ = [0] * label_num
        labels = re.split(' +', user_record_df_merge_unique.loc[i, 'labels'].strip())
        for label in labels:
            loc = all_labels.index(label)
            row_[loc] = 1
        df_data.append(row_)

    all_user_saw_work_label_df = pd.DataFrame(data=df_data,
                                              index=user_record_df_merge_unique['workId'], columns=all_labels)

    # 用户id列表
    all_users_ids = user_record_df['userId'].unique().tolist()
    # 所有用户对其看过的作品的评分矩阵  浏览次数作为隐性评分
    data_array1 = user_work_df.values
    # 所有用户浏览过的作品
    works_user_saw_names1 = user_work_df.columns.tolist()

    # users_dict = {用户一:[['节目一', 3.2], ['节目四', 0.2], ['节目八', 6.5]], 用户二: ... }
    users_dict = createUsersDict(user_work_df)
    # items_dict = {节目一: [用户一, 用户三], 节目二: [...], ... }
    items_dict = createItemsDict(user_work_df)

    # 所有用户看过的作品标签矩阵
    data_array2 = all_user_saw_work_label_df.values
    works_user_saw_names2 = all_user_saw_work_label_df.index.tolist()

    # 为用户浏览过的作品建立作品画像
    works_users_saw_profile = createItemsProfiles(data_array2, all_labels, works_user_saw_names2)

    # 建立用户画像和用户浏览过的作品集
    (users_profiles, works_users_saw) = createUsersProfiles(data_array1, all_users_ids,
                                                            works_user_saw_names1, all_labels, works_users_saw_profile)

    # 备选作品的标签矩阵
    data_array3 = work_labels_df.values
    works_to_be_recommended_names = work_labels_df.index.tolist()
    # 为备选推荐作品集建立作品画像
    works_to_be_recommended_profiles = createItemsProfiles(data_array3, all_labels, works_to_be_recommended_names)

    # 两种推荐算法后融合，也就是将两种推荐算法对某个用户分别产生的两个推荐节目集按不同比例混合，得出最后的对该用户的推荐结果
    # 对于每个用户推荐topN个节目,在两种推荐算法产生的推荐集中分别选取比例为w1和w2的推荐结果,CB占w1, userCF占w2
    # w1 + w2 = 1 且 w1 * topN + w2 * topN = topN
    topN = 10

    w1 = 0.7
    w2 = 0.3

    # 从CB的推荐集中选出前topW1项
    topW1 = int(w1 * topN)

    # 从userCF的推荐集中选出前topW2项
    topW2 = topN - topW1

    for user in all_users_ids:

        # 对于用户user的最终混合推荐节目集
        recommend_items = []

        # CB
        # recommend_items1 =  [[节目名, 该节目与该用户user画像的相似度], ...]
        recommend_items1 = contentBased(users_profiles[user], works_to_be_recommended_profiles,
                                        works_to_be_recommended_names, all_labels, works_users_saw[user])
        len1 = len(recommend_items1)

        if len1 <= topW1:
            recommend_items = recommend_items + recommend_items1
        else:
            recommend_items = recommend_items + recommend_items1[:topW1]

        # userCF
        # recommend_item2 = [[节目名, 该用户user对该节目的感兴趣程度],...]
        recommend_items2 = userCF(user, users_dict, items_dict, 2, works_to_be_recommended_names)
        len2 = len(recommend_items2)

        if len2 <= topW2:
            recommend_items = recommend_items + recommend_items2
        else:
            recommend_items = recommend_items + recommend_items2[:topW2]

        # 将推荐结果按推荐指数降序排序
        recommend_items.sort(key=lambda item: item[1], reverse=True)

        # print("对于用户 %s 的推荐节目如下" % user)
        # printRecommendItems(recommend_items, 10)
        # print()
        conn.execute(text(f"delete from recommend_work where userId = {user}"))
        insert_to_db(user, recommend_items, 10, conn)

    conn.commit()
    conn.close()
    del conn
    return True


if __name__ == "__main__":
    recommend()
    pass
