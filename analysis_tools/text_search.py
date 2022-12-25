import spacy
from spacy.matcher import PhraseMatcher
nlp = spacy.load("en_core_web_lg")


class TextParser:
    """
    Parse input text file.
    """
    def __init__(self, client, db_name: str, collection_name: str):
        self.client = client
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    def add_key_sentence(df, dict_input):
        df['key_sentence'] = df['fullTranscript'].apply(lambda x: split_full_transcript(x, dict_input))
        #df = df.explode('key_sentence')
        return df


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