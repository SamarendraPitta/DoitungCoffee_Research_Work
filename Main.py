import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim import corpora, models
from gensim.models.ldamodel import LdaModel
from gensim.corpora import Dictionary
import pyLDAvis.gensim
import gensim
import spacy
import matplotlib.pyplot as plt
import seaborn as sns
from gensim.models.coherencemodel import CoherenceModel
from wordcloud import WordCloud
import pandas as pd
import numpy as np
from nltk.probability import FreqDist

# Read the data and preprocess
with open('DoiTungcoffeedata_v1+v2.txt', 'r', encoding='utf-8') as file:\
    lines = file.read()\n",
    all_newline_positions = [i for i, char in enumerate(lines) if char == '^']
    data = []
    j = 0
    for i in all_newline_positions:
        text = lines[j:i]
        data.append(text)
        j = i

# Tokenize the data using spaCy
nlp = spacy.load('en_core_web_sm')

# Define a function to preprocess each document
def preprocess_document(document):
    # Tokenize the document using spaCy
    tokenized_document = nlp(document)
    # Apply filtering to select relevant tokens
    filtered_words = [token.lemma_ for token in tokenized_document 
                      if token.is_alpha and not token.is_punct 
                      and not token.is_space and not token.is_stop 
                      and token.pos_ in ['NOUN', 'VERB', 'ADJ']]
    return filtered_words

# Apply the preprocess_document function to each document in your dataset
tokenized_documents = [preprocess_document(doc) for doc in data]

# Filter extremes based on frequency
high_freq_threshold = 0.9 * len(tokenized_documents)
token_articles_w_pos = [[token for token in tokens if word_freq[token] <= high_freq_threshold] for tokens in tokenized_documents]

NUM_OF_PROCESS = 4
NUM_OF_TOPICS = 20

# Filter extremes before creating dictionary
dictionary_word_pos = corpora.Dictionary(token_articles_w_pos)
corpus_bow_word_pos = [dictionary_word_pos.doc2bow(article) for article in token_articles_w_pos]


# Create and train the LDA model
LDA_Model = gensim.models.ldamodel.LdaModel(corpus=corpus_bow_word_pos, num_topics=NUM_OF_TOPICS, 
                                            id2word=dictionary_word_pos, random_state=1, passes=10,
                                            alpha='auto', eta='auto')

# Print the topics
#topics = LDA_Model.print_topics(num_topics=NUM_OF_TOPICS, num_words=10)
#for topic_id, topic_words in topics:
#    print(f\"Topic {topic_id}: {topic_words}\")

def get_top_topics(article_idx, min_topic_prob):

  # Sort from highest to lowest topic probability.
  topic_prob_pairs = sorted(LDA_Model.get_document_topics(corpus_bow_word_pos[article_idx],
                                                          minimum_probability=min_topic_prob),
                            key=lambda tup: tup[1])[::-1]

  word_prob_pairs = [LDA_Model.show_topic(pair[0]) for pair in topic_prob_pairs]
  topic_words = [[pair[0] for pair in collection] for collection in word_prob_pairs]

  data = {
      'Major Topics': topic_prob_pairs,
      'Topic Words': topic_words
  }

  return pd.DataFrame(data)

pd.set_option('max_colwidth', 600)
snippet_length = 300
min_topic_prob = 0.001

topics_df = pd.DataFrame(columns=['Topic ID', 'Probability', 'Topic Words'])
for i in range(1,20):
    article_idx = i
    topic_data = get_top_topics(article_idx, min_topic_prob)
    topics_df = pd.concat([topics_df, topic_data], ignore_index=True)
print(topics_df)

# Calculate word frequencies
word_freq = FreqDist([word for doc in tokenized_documents for word in doc])

topics_df = pd.DataFrame(columns=['Topic ID', 'Probability', 'Topic Words'])
for i in range(20):  # Change this line
    article_idx = i
    topic_data = get_top_topics(article_idx, min_topic_prob)
    topics_df = pd.concat([topics_df, topic_data], ignore_index=True)
print(topics_df)

pyLDAvis.enable_notebook()
vis = pyLDAvis.gensim.prepare(LDA_Model,corpus_bow_word_pos,dictionary = LDA_Model.id2word)

# Display word clouds for each topic
def render_word_cloud(model, rows, cols, max_words):
    word_cloud = WordCloud(background_color='white', max_words=max_words, prefer_horizontal=1.0)
    fig, axes = plt.subplots(rows, cols, figsize=(15, 15))

    for i, ax in enumerate(axes.flatten()):
        fig.add_subplot(ax)
        topic_words = dict(model.show_topic(i))
        word_cloud.generate_from_frequencies(topic_words)
        plt.gca().imshow(word_cloud, interpolation='bilinear')
        plt.gca().set_title('Topic {id}'.format(id=i))
        plt.gca().axis('off')

    plt.axis('off')
    plt.show()

render_word_cloud(LDA_Model, 3, 3, 10)
