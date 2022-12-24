import spacy
from spacy.matcher import PhraseMatcher
nlp = spacy.load("en_core_web_lg")


def get_collection(collection_name, key_file_path):
    """
    Read in key to mongoDB and return collection
    @param collection_name: specify the collection to call
    @return: collection object
    """
    import pymongo
    import os
    import sys
    path = f'{key_file_path}'
    os.environ['PATH'] += ':'+path
    with open(f"{path}mongo_key.txt", "r") as f:
        data = f.readlines()
        
    client_address = data
    # establish connection to database
    client = pymongo.MongoClient(client_address)
    # access the database by making an instance
    db = client['community-board']
    # make collection instance
    collection = db[collection_name]

    return collection


def entire_db_object(collection_obj):
    """
    Grab all objects in collection that are between specified range
    @param collection_obj: collection object from mongoDB
    @param start_db: initial date to begin
    @param end_db: the date to end
    @return: database collection object filtered to date
    """
    query = collection_obj.find()
    return query


def filter_db_object(collection_obj, start_db: str, end_db:str):
    """
    Grab all objects in collection that are between specified range
    @param collection_obj: collection object from mongoDB
    @param start_db: initial date to begin
    @param end_db: the date to end
    @return: database collection object filtered to date
    """
    from datetime import datetime
    start_date = datetime.strptime(start_db, '%Y-%m-%d')
    end_date = datetime.strptime(end_db, '%Y-%m-%d')
    query = collection_obj.find(
        {"YoutubeMetadata.publishDate": {"$gte": start_date.isoformat(), "$lt": end_date.isoformat()}})
    return query


def analyze_month(end_date=None):
    """
    Input date to filter database by. 
    @param start_date: initial date to filter a week from
    @return: date range of week from start date.
    """
    import datetime as dt
    from datetime import datetime
    
    # Query to last week's data
    if end_date is not None:
        day = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        day = dt.datetime.now().date()

    # Make range date
    start = day - dt.timedelta(days=30)
    end = day
    return start, end


def analyze_week(start_date=None):
    """
    Input date to filter database by. 
    @param start_date: initial date to filter a week from
    @return: date range of week from start date.
    """
    import datetime as dt
    from datetime import datetime
    
    # Query to last week's data
    if start_date is not None:
        day = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        day = dt.datetime.now().date()

    # Make range date
    start = day - dt.timedelta(days=day.weekday() + 1)
    end = start + dt.timedelta(days=6)
    return start.date(), end.date()


def structure_df(input_db_query):
    import pandas as pd
    db_id = []
    video_url = []
    author = []
    publish_date = []
    title = []
    topic = []
    full_transcript = []
    word_count_list = []
    length = []
    for id in input_db_query:
        db_id.append("https://blockparty.studio/Archive/?_id=" + str(id.get('_id')))
        video_url.append("https://www.youtube.com/watch?v=" + str(id.get('properties').get('videoURL')))
        author.append(str(id.get('CommunityBoardInfo').get('normalizedName')))
        publish_date.append(id.get('YoutubeMetadata').get('publishDate'))
        title.append(str(id.get('YoutubeMetadata').get('title')))
        topic.append(str(id.get('properties').get('meetingType')))
        full_transcript.append(str(id.get('properties').get('fullTranscript')))
        length.append(str(id.get('YoutubeMetadata').get('lengthSeconds')))
        # get list of key words
        word_count_dict = id.get('properties').get('wordCountFullTranscript')
        word_count_dict.update(id.get('properties').get('wordCountSummary'))
        #word_count = list(dict(list(full_word_count.items()) + list(summary_word_count.items())).keys())
        #print(word_count)
        # make into dictionary
        word_count_list.append(word_count_dict)
    
    # make each list into dataframe
    output_df = pd.DataFrame(
    {'meeting_url': db_id,
     'video_url': video_url,
     'meeting_author': author,
     'meeting_publish_date': publish_date,
     'meeting_title': title,
     'meeting_topic': topic,
     'fullTranscript': full_transcript,
     'top_word_count': word_count_list,
     'meeting_length':length
    })

    return output_df


def format_time(input_string):
    from datetime import datetime 
    return datetime.strptime(input_string, '%Y-%m-%dT00:00:00').date().strftime('%B %d, %Y')


def get_date_range_words(start_date_input):
    from collections import Counter
    import pandas as pd
    
    db_collection = get_collection('transcripts_v4')
    #start_date, end_date = analyze_week(start_date_input)
    start_date, end_date = analyze_week(start_date_input)
    print(f'Query from {start_date.strftime("%B %d")}th to {end_date.strftime("%B %d")}th')
    db_query = filter_db_object(db_collection, start_date, end_date)
    df_week = structure_df(db_query)
    print(f"Number of Meetings: {df_week.shape[0]}")

    date_range = format_time(df_week.publish_date.min())
    
    # make plots
    make_plot(df_week, start_date)
 
    # get word count
    labels, values = zip(*merge_dicts(df_week['word_count']).items())
    count_words = pd.DataFrame({"label" : labels, "count" : values}).sort_values('count', ascending=False)
    
    return df_week, count_words



def make_plot(df_week, start_date):
    from collections import Counter
    import datetime
    import matplotlib.pyplot as plt
    # output secondary plot of all topics flattened
    df_week['topic_noun'] = df_week['topic'].apply(lambda x: split_topic(x))
    # flatten list
    topics = dict(Counter([item for sublist in df_week['topic_noun'] for item in sublist]).most_common())
    labels, values = zip(*topics.items())
    fig, ax = plt.subplots(figsize = (10,5))
    plt.barh(labels,values,align='center') 
    plt.title('Topics Counted for the week of: ' + start_date.strftime('%B %d, %Y'), fontsize=15)
    plt.xlabel('Meeting Count', fontsize=12)
    plt.ylabel('Topic', fontsize=12)
    plt.xticks(range(min(values), max(values) + 1, 1))
    plt.tight_layout()
    #plt.savefig(f'../viz/topic_count_{datetime.date.today()}.png')
    plt.show()
    
    
def merge_dicts(x):
    return {k: v for d in x.dropna() for k, v in d.items()}

def mergeDict(dict1, dict2):
    dict3 = {**dict1, **dict2}
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
               dict3[key] = [value + dict1[key]][0]
    return dict3


def split_topic(input_value):
    import ast
    
    topic_list = [classifier[1] for classifier in ast.literal_eval(input_value) if classifier[0] > .05]
    return topic_list


def make_subset(word_list, label, db_collection_input):
    ptrn = "|".join(word_list)
    
    # use $regex to find docs that start with case-sensitive "obje"
    query = { "properties.fullTranscript": { "$regex": ptrn , "$options": "i"}}
    print(ptrn)
    # print count
    docs = db_collection_input.count_documents(query)
    print(docs)
    subset_df = structure_df(db_collection_input.find(query))
    # add topic
    subset_output = add_topic(subset_df, ptrn, label)
    return subset_output


def create_taxonomy(word_dict_input, db_collection_input):
    """
    
    """
    import numpy as np
    import pandas as pd
    # +r'\b'
    word_list = [r'\b' + i + r'\b' for i in list(word_dict_input.values())[0]]
    title = list(word_dict_input.keys())[0]
    df = make_subset(word_list, title, db_collection_input)
    # format as datetime
    df['publish_date'] = pd.to_datetime(df['publish_date'], format='%Y-%m-%dT%H:%M:%S')
    df['topic_count'] = df.fullTranscript.apply(lambda x: \
                                        word_counter(x, [term.lstrip().rstrip() for term in word_list]))
    top_topic_words = {}
    for i in range(len(df)):
        top_topic_words = mergeDict(top_topic_words, df.topic_count.loc[i] )
    print({k: v for k, v in sorted(top_topic_words.items(), key=lambda item: item[1])})
    
    topics_df = pd.concat([df, pd.DataFrame(list(df.topic_count))], axis=1)
    print(topics_df.shape)

    # fix for when the input word in not found!!!!!
    # concatenate topics under title
    topics_df[title+'_total'] = np.add.reduce(topics_df[word_list].fillna(0), axis=1)
    topics_df.columns = topics_df.columns.str.strip('\\b')
    topics_df.columns = topics_df.columns.str.strip('.')
    topics_df.columns = topics_df.columns.str.replace("?", "")
    topics_df['video_url'] = topics_df['video_url'].apply(lambda x: f"https://www.youtube.com/watch?v={x}")
    return topics_df


def add_topic(df, reg_ptrn, label):
    df['topic_label'] = label
    df['topic_label_count'] = df.fullTranscript.apply(lambda x: count_word_occurence(x, reg_ptrn))
    
    return df


def count_word_occurence(input_text, reg_ptrn):
    import re
    ptn = re.compile(reg_ptrn, flags=re.IGNORECASE)
    print(len(ptn.findall(input_text)))
    return len(ptn.findall(input_text))


def word_counter(string_input, word_list):
    import re
    total_word_count = {}
    for i in range(len(word_list)):
        print(word_list[i])
        pattern = re.compile(fr'\b{word_list[i]}\b', re.I) # case insensitive
        print(pattern.findall(string_input))
        num = len(pattern.findall(string_input))
        if num > 0:
            
            total_word_count[word_list[i]] = num
    return total_word_count


def split_full_transcript(full_transcript_id, input_dict):
    """
    Takes the transition words and full transcript to split the chunk of text into meaningful line breaks
    @return:
    """
    input_list = [input_x.strip('.') for input_x in [term for term in list(input_dict.values())][0]]

    # Find the sentences containing a transition word
    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    phrases = input_list
    patterns = [nlp(text) for text in phrases]
    phrase_matcher.add('word_input', None, *patterns)
    print('next')

    doc = nlp(full_transcript_id)

    # Append to list
    key_sentences = []
    for sent in doc.sents:
        
        for match_id, start, end in phrase_matcher(nlp(sent.text)):
            if sent.text not in key_sentences:
                if nlp.vocab.strings[match_id] in ["word_input"]:
                    print(sent)
    
                    key_sentences.append(sent.text)


    return key_sentences



def add_key_sentence(df, dict_input):
    df['key_sentence'] = df['fullTranscript'].apply(lambda x: split_full_transcript(x, dict_input))
    #df = df.explode('key_sentence')
    return df


def get_imp(bow,mf,ngram):
    import pandas as pd
    import numpy as np
    # creates BOW
    import sklearn.feature_extraction.text as text
    tfidf=text.CountVectorizer(bow, ngram_range=(ngram,ngram), max_features=mf, stop_words='english')
    matrix=tfidf.fit_transform(bow)
    return pd.Series(np.array(matrix.sum(axis=0))[0],index=tfidf.get_feature_names()).sort_values(ascending=False).head(1000)

    
    