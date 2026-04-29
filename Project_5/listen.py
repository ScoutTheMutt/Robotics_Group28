from pocketsphinx import LiveSpeech



speech = LiveSpeech(keyphrase='Robot Lab', kws_threshold=1e-20)
for phrase in speech:
    print(phrase.segments(detailed=True))