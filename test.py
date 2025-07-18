# News Recommendation System using Two-Tower Model
# Adapted from Movie Recommendation System for MIND small dataset

import numpy as np
import pandas as pd
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import tensorflow as tf
from tensorflow.keras import Model
from tensorflow.keras.layers import Input, Dense, Dot, Embedding, Flatten, Lambda
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Set random seed for reproducibility
np.random.seed(1)
tf.random.set_seed(1)

# Paths to MIND small dataset components:
DATA_DIR = "./MINDsmall"
BEHAVIORS_PATH = os.path.join(DATA_DIR, "behaviors.tsv")
NEWS_PATH = os.path.join(DATA_DIR, "news.tsv")

# --- Load news data ---
def load_news(path):
    df = pd.read_csv(path, sep='\t', header=None,
                     names=['id', 'category', 'subcategory', 'title', 'abstract',
                            'url', 'title_entities', 'abstract_entities'])
    df.fillna('', inplace=True)
    df['content'] = df['title'] + ' ' + df['abstract']
    return df

# --- Load user behaviors ---
def load_behaviors(path):
    df = pd.read_csv(path, sep='\t', header=None,
                     names=['impression_id', 'user_id', 'time', 'history', 'impressions'])
    df.fillna('', inplace=True)
    return df

# --- One-hot encode categories ---
def encode_categories(series):
    return pd.get_dummies(series, prefix=series.name)

# --- TF-IDF for text features ---
def get_tfidf_features(corpus, max_features=5000):
    tfidf = TfidfVectorizer(max_features=max_features)
    return tfidf.fit_transform(corpus).toarray()

# Load data
news_df = load_news(NEWS_PATH)
behaviors_df = load_behaviors(BEHAVIORS_PATH)

# Build news feature matrix
tfidf_feats = get_tfidf_features(news_df['content'], max_features=5000)
cat_feats = encode_categories(news_df['category'])
subcat_feats = encode_categories(news_df['subcategory'])
news_features = pd.concat([
    pd.DataFrame(tfidf_feats, index=news_df.index),
    cat_feats, subcat_feats
], axis=1)

# Create mapping from news IDs to indices
news_id_map = {nid: i for i, nid in enumerate(news_df['id'])}

# Parse interactions: (user_id, news_index, label)
records = []
for _, row in behaviors_df.iterrows():
    uid_raw = row['user_id']
    user_id = int(uid_raw[1:]) if isinstance(uid_raw, str) and uid_raw.startswith('U') else int(uid_raw)
    for imp in row['impressions'].split():
        if '-' not in imp:
            continue
        nid, lbl = imp.split('-')
        if nid in news_id_map:
            records.append((user_id, news_id_map[nid], int(lbl)))
interactions = pd.DataFrame(records, columns=['user_id', 'news_idx', 'label'])

# Map users and news to indices
user_ids = interactions['user_id'].unique()
user_id_map = {uid: i for i, uid in enumerate(user_ids)}
interactions['user_idx'] = interactions['user_id'].map(user_id_map)

news_ids = news_df['id'].unique()
news_id_map = {nid: i for i, nid in enumerate(news_ids)}
interactions['news_idx'] = interactions['news_idx'].map(lambda x: x)  # already mapped

num_users = len(user_id_map)
num_news = len(news_id_map)

# Build training arrays
y = interactions['label'].values
user_indices = interactions['user_idx'].values
news_indices = interactions['news_idx'].values

# Train-test split
u_train, u_test, n_train, n_test, y_train, y_test = train_test_split(
    user_indices, news_indices, y, test_size=0.2, random_state=42
)

# Define two-tower model using Embedding for both users and news
embedding_dim = 64

input_user = Input(shape=(), dtype='int32', name='user_idx')
user_embedding = Embedding(input_dim=num_users, output_dim=embedding_dim)(input_user)
user_vec = Flatten()(user_embedding)
user_vec = Lambda(lambda x: tf.linalg.l2_normalize(x, axis=1))(user_vec)

input_news = Input(shape=(), dtype='int32', name='news_idx')
news_embedding = Embedding(input_dim=num_news, output_dim=embedding_dim)(input_news)
news_vec = Flatten()(news_embedding)
news_vec = Lambda(lambda x: tf.linalg.l2_normalize(x, axis=1))(news_vec)

score = Dot(axes=1)([user_vec, news_vec])
model = Model(inputs=[input_user, input_news], outputs=score)
model.compile(optimizer='adam', loss='mse')
model.summary()

# Train
model.fit([u_train, n_train], y_train, epochs=5, batch_size=128, validation_split=0.1)

model.save("news_recommender_model.keras") 

# Evaluate
loss = model.evaluate([u_test, n_test], y_test)
print(f"Test loss: {loss:.4f}")

# Cold-start recommendation for a new user (user index = 0)
new_user_idx = np.array([0] * num_news)
all_news_idx = np.arange(num_news)
scores = model.predict([new_user_idx, all_news_idx], verbose=0)
top_idxs = np.argsort(scores.flatten())[::-1][:10]

print("Top recommended news for new user:")
for idx in top_idxs:
    print(f"- {news_df.iloc[idx]['title']}")