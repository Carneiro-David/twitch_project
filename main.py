from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello World'

@app.route('/test', methods=['GET'])
def test():
    return 'test'

@app.route('/test2', methods=['GET'])
def test():
    return 'test2'

@app.route('/test3', methods=['GET'])
def test():
    return 'test3'

if (__name__ == '__main__'):
    app.run(debug=True)