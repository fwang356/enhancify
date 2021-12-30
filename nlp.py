import lyricsgenius
import nltk
from deep_translator import GoogleTranslator
from nltk.sentiment import SentimentIntensityAnalyzer

genius = lyricsgenius.Genius('twk9aMNXtiEl_zGc1rA9fd1eLJ_OWmd0owpsntBsLQyq2QYKKoPTMMM-Sh5V2ENK')
stopwords = nltk.corpus.stopwords.words("english")
sia = SentimentIntensityAnalyzer()

def lyrics(title, artist):
    song = genius.search_song(title, artist)
    if song == None:
        return "Not Found"
    string = song.lyrics.replace("EmbedShare", "")
    string = string.replace("URLCopyEmbedCopy", "")

    length = len(string)
    string = string[0:length - 1]
    length -= 1
    while string[length - 1].isdigit() or string[length - 1] == '' or string[length - 1] == '\n':
        string = string[0:length - 1]
        length -= 1
    
    phrases = string.split('\n')
    phrases.append(string)

    for i in range(1, len(phrases)):
        if phrases[i] != '' and phrases[i][0] == '[' and phrases[i][len(phrases[i]) - 1] == ']':
            if phrases[i-1] != '':
                phrases.insert(i, '')
    
    return phrases


def clean(string):    
    if string == "Not Found":
        return string
    string = string.replace('[', "1")
    string = string.replace(']', "1")

    string = GoogleTranslator(source="auto", target="en").translate(string)

    lyrics = string.split('\n')
    
    for i in range(len(lyrics)):
        lyrics[i] = nltk.word_tokenize(lyrics[i])
        lyrics[i] = [w for w in lyrics[i] if w.isalpha()]
        lyrics[i] = [w for w in lyrics[i] if w.lower() not in stopwords]
        lyrics[i] = ' '.join(lyrics[i])
    
    lyrics = [phrase for phrase in lyrics if phrase != '']

    return lyrics


def analyze(lyrics):
    if lyrics == "Not Found":
        return 0
    total = 0
    for phrase in lyrics:
        total += sia.polarity_scores(phrase)["compound"]

    score = total/len(lyrics) + 1
    score *= 50
    return round(score)