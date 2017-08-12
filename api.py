import os
from flask import request
from flask import Flask, jsonify, render_template
from text_analysis import TextAnalysis
from spell_checker import SpellChecker
from speech_to_text import SpeechToText
from classifiers import Classifiers
from werkzeug.utils import secure_filename
from utils import logger_exception, tokenize


app = Flask(__name__, template_folder='static/templates')
app.config['UPLOAD_FOLDER'] = '/tmp/'


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=('POST', ))
@logger_exception
def upload_file():
    try:
        file = request.files.get('file')
        if file and file.filename.rsplit('.', 1)[1] in ('txt', ):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify('File uploaded successfully')
        return jsonify({'message': 'File format is not supported. Please use txt'}), 400
    except Exception as e:
        return jsonify('Failed to upload file'), 400


@app.route('/speech_to_text', methods=('POST', ))
@logger_exception
def get_text_from_audio():
    try:
        file = request.files.get('file')
        if file and file.filename.rsplit('.', 1)[1] in ('flac', 'wav'):
            speech_to_text = SpeechToText()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            text = speech_to_text.recognize(audio_file=os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({'text': text})
        return jsonify({'message': 'File format is not supported. Please use flac, wav'}), 400
    except Exception as e:
        return jsonify('Failed to upload file'), 400


@app.route('/<filename>/text_analysis/')
@logger_exception
def analyze(filename):
    try:
        analyzer = TextAnalysis(
            filepath=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        )
        return jsonify(analyzer.analyze())
    except FileNotFoundError as e:
        return jsonify('File not found'), 400


@app.route('/text_analysis', methods=('POST', ))
@logger_exception
def analyze_post():
    data = request.get_json().get('data')
    analyzer = TextAnalysis(text=data)
    return jsonify({
        'original_text': data,
        'text_analysis': analyzer.analyze()
    })


@app.route('/<filename>/spell_check')
@logger_exception
def spell_check(filename):
    try:
        spell_checker = SpellChecker()
        result = spell_checker.multiple_check(
            open(os.path.join(app.config['UPLOAD_FOLDER'], filename)).read()
        )
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify('File not found'), 400


@app.route('/spell_check', methods=('POST', ))
@logger_exception
def spell_check_post():
    data = request.get_json().get('data')
    spell_checker = SpellChecker()
    result = spell_checker.multiple_check(data)
    return jsonify({
        'original_text': data,
        'spell_check': result
    })


@app.route('/<filename>/sentiment_analysis/')
@logger_exception
def sentiment_analysis(filename):
    try:
        data = open('text_data/text.txt').read()
        words = [word for word in tokenize(data)]
        classifiers = Classifiers()
        classifiers.get_trained()
        naive_best_words = classifiers.naive_best_words.predict(words)
        naive_bag_of_words = classifiers.naive_bag_of_words.predict(words)
        svm = classifiers.svm.predict(words)
        result = {
            'naive_best_words': dict(zip(words, naive_best_words)),
            'naive_bag_of_words': dict(zip(words, naive_bag_of_words)),
            'svm': dict(zip(words, svm))
        }
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify('File not found', 400)


@app.route('/sentiment_analysis', methods=('POST', ))
@logger_exception
def sentiment_analysis_post():
    data = request.get_json().get('data')
    words = [sent for sent in tokenize(data)]
    classifiers = Classifiers()
    classifiers.get_trained()
    naive_best_words = classifiers.naive_best_words.predict_prob(words)
    naive_bag_of_words = classifiers.naive_bag_of_words.predict_prob(words)
    svm = classifiers.svm.predict(words)
    result = {
        'original_text': data,
        'classifiers': {
            'naive_best_words': naive_best_words,
            'naive_bag_of_words': naive_bag_of_words,
            'svm': svm
        }
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
