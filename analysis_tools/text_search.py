import spacy
from spacy.matcher import PhraseMatcher, Matcher
print("Importing en_core_web_lg...")
nlp = spacy.load("en_core_web_lg")

def extract_ents(sentence, NERTag="LOC"):
    """
    Extracts specified NERtag entity from input text.
    @ return: list of all nertags specified.
    """
    import numpy as np
    # print(f"Processing sent:  {sentence}")
    doc = nlp(sentence)
    matching_ents = [ent.text for ent in doc.ents if ent.label_ == NERTag]
    if not matching_ents:
        return np.nan
    else:
        return matching_ents


class TextParser:
    """
    Parse input text file.
    """
    def __init__(self, df, input_dict: dict):
        self.df = df
        self.input_dict = input_dict


    def filterTextByRegexPtn(self, text_input):
        """
        Takes the transition words and full transcript to split the chunk of text into meaningful line breaks
        @return:
        """
        # convert the input dictionary into a list
        input_phrase_list = "|".join([input_x for input_x in [term for term in list(self.input_dict.values())][0]])

        # Find the sentences containing a list of key terms
        pattern = [{'TEXT': {'REGEX': f"(?i)({input_phrase_list})"}}]
        print(f"Generating Matcher object for {pattern}")
        matcher = Matcher(nlp.vocab)
        matcher.add('key_term', [pattern])
        doc = nlp(text_input)
        matches = matcher(doc)
        # create list of sentence matches:
        matched_sents = []
        for match_id, start, end in matches:
            span = doc[start:end]  # The matched span
            print(f"Text: {span.text}")
            matched_sents.append(str(span.sent))
        return matched_sents


    def filterTextByPhraseMatcherPtn(self, full_transcript_id):
        """
        Takes the transition words and full transcript to split the chunk of text into meaningful line breaks
        @return:
        """
        # convert the input dictionary into a list
        input_list = [input_x.strip('.') for input_x in [term for term in list(self.input_dict.values())][0]]

        print("Generating PhraseMatcher object...")
        # Find the sentences containing a key term
        print('process LEMMA')
        phrase_matcher = PhraseMatcher(nlp.vocab, attr="LEMMA")
        phrases = input_list
        patterns = [nlp(text) for text in phrases]
        phrase_matcher.add('word_input', None, *patterns)
        

        doc = nlp(full_transcript_id)

        # Append to list
        key_sentences = []
        for sent in doc.sents:
            
            for match_id, start, end in phrase_matcher(nlp(sent.text)):
                if sent.text not in key_sentences:
                    if nlp.vocab.strings[match_id] in ["word_input"]:
                        print(sent)
                        key_sentences.append(sent.text)
        print('Processing next document...')

        return key_sentences