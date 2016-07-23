#!/usr/bin/env python
import datetime
import flask
import redis
import time
import json
import tweepy
import re
from tweepy import Stream
from tweepy.streaming import StreamListener



app = flask.Flask(__name__)
app.secret_key = 'xxxxxxx'
red = redis.StrictRedis()



def event_stream():
    pubsub = red.pubsub()
    pubsub.subscribe('live')
    for message in pubsub.listen():
        if message['data'] != 1:
            print(message)
            yield 'data: %s\n\n' % message['data'].decode(encoding='utf-8',errors='ignore')

def event_stream_chat():
    pubsub_chat = red.pubsub()
    pubsub_chat.subscribe('chat')
    for message in pubsub_chat.listen():
        if message['data'] != 1 and not message['data'] == b'anonymous: ':
            print(message)
            yield 'data: %s\n\n' % message['data'].decode(encoding='utf-8',errors='ignore')



@app.route('/post', methods=['POST'])
def post():
    message = flask.request.form['message']
    if message == "GO":
        call_twitter(['teammystic','teamvalor','teaminstinct'],1)
        #red.publish('live', u'1 2 3||||app_delimiter||||DONE')
        #red.publish('live', u'DONE')
        #red.publish('live', u'DONE')
        return flask.Response(status=204)
    else:
        user = flask.session.get('user', 'anonymous')
        #now = datetime.datetime.now().replace(microsecond=0).time()
        red.publish('chat', u'%s: %s' % (user, message))
        return flask.Response(status=204)




@app.route('/stream')
def stream():
    return flask.Response(event_stream(),
                          mimetype="text/event-stream")

@app.route('/chat')
def stream_chat():
    return flask.Response(event_stream_chat(),
                          mimetype="text/event-stream")





@app.route('/')
def home():
    flask.session.clear()
    return """
        <!doctype html>
        <title>pokemon listener</title>
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
        <style>body { max-width: 100px; margin: 40px; padding: 1em; background: #fff; color: #000066; font: 16px/1.6 menlo, monospace; }
        pre { color:  #000066}
        </style>
        <pre>Pokemon Listener</pre>
        <pre>By George Zeinieh</pre>
        <p>zeiniehgeorge@gmail.com</p>
        <table>
          <tr>
            <td><img src="https://jackaloupe.files.wordpress.com/2016/07/team-mystic-cutout1.png" width ="350" height="400"></td>
            <td><img src="https://jackaloupe.files.wordpress.com/2016/07/team-valor-cutout-no-outside1.png" width ="350" height="400"></td>
            <td><img src="https://jackaloupe.files.wordpress.com/2016/07/team-instinct-cutout.png" width ="350" height="400"></td>
          </tr>
        </table>
        <pre id="out1"></pre>
        <script>
            function sse() {
                var empty = "                   ";
                var source = new EventSource('/stream');
                var out = document.getElementById('out1');
                source.onmessage = function(e) {

                   out.innerHTML = empty.concat(e.data.split("||||app_delimiter||||")[0].split(" ")[2],empty,empty,e.data.split("||||app_delimiter||||")[0].split(" ")[1], empty,empty,e.data.split("||||app_delimiter||||")[0].split(" ")[0])


                };


            }
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('/post', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();
        </script>
        <div id="myDiv" style="width: 800px; height: 380px; margin:0 auto;"><!-- Plotly chart will be drawn inside this DIV --></div>
          <!-- Plotly.js -->
          <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
          <!-- Numeric JS -->
          <script src="https://cdnjs.cloudflare.com/ajax/libs/numeric/1.2.6/numeric.min.js"></script>

        <script>

        function sse() {
                var source = new EventSource('/stream');
                var out = document.getElementById('myDIv');
                source.onmessage = function(e) {

                var count_blue = e.data.split("||||app_delimiter||||")[0].split(" ")[2]
                var count_red = e.data.split("||||app_delimiter||||")[0].split(" ")[1]
                var count_yellow = e.data.split("||||app_delimiter||||")[0].split(" ")[0]

                var data = [{
                values: [count_blue, count_red, count_yellow],
                labels: ['Team Mystic', 'Team Valor', 'Team Instinct'],
                type: 'pie',
                marker: {
                colors: ['rgb(102,178,255)','rgb(255,102,102)','rgb(255,255,102)']
                  }

                }];

                var layout = {
                height: 380,
                width: 480
                };

                out.innerHTML = Plotly.newPlot('myDiv', data, layout);

                };


            }
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('/post', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();





        </script>
        <p>Message: <input id="in" / size="100"></p>
        <pre >Live Messages</pre>

        <pre id="chat"></pre>
        <script>
            function sse() {
                var source = new EventSource('/chat');
                var out = document.getElementById('chat');
                source.onmessage = function(e) {
                    out.innerHTML =  e.data  + '\\n' +  out.innerHTML;
                };
            }
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('/post', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();
        </script>

        <pre >Live Tweets</pre>

        <pre id="out"></pre>
        <script>
            function sse() {
                var count = 0
                var source = new EventSource('/stream');
                var out = document.getElementById('out');
                source.onmessage = function(e) {
                    count +=1
                    if (count % 5 === 0) {
                    out.innerHTML =  e.data.split("||||app_delimiter||||")[1].replace(/(.{80})/g, "$1<br>");


                    }
                    else {
                    out.innerHTML =  out.innerHTML + "<br>" + e.data.split("||||app_delimiter||||")[1].replace(/(.{80})/g, "$1<br>")

                    }
                };
            }
            $('#in').keyup(function(e){
                if (e.keyCode == 13) {
                    $.post('/post', {'message': $(this).val()});
                    $(this).val('');
                }
            });
            sse();
        </script>

    """

#############################
######### TWitter ###########
#############################


######### auth ##############

class TwitterAuth():

    def __init__(self, CONSUMER_KEY,CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET):
        self.CONSUMER_KEY = CONSUMER_KEY
        self.CONSUMER_SECRET = CONSUMER_SECRET
        self.ACCESS_KEY = ACCESS_KEY
        self.ACCESS_SECRET = ACCESS_SECRET
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        self.api = tweepy.API(self.auth)


T = TwitterAuth('xxxxx', 'xxxxxxxxxxxx', 'xxxxxxxxxxx', 'xxxxxxxxxx')

auth = T.auth

############ Listener ###########

class Listener(StreamListener):

    def __init__(self, time_limit):
        """

        :param filter_by: the word to search for
        :param time_limit: the duration of the streaming
        """
        super().__init__()
        self.time_limit = time_limit * 60
        self.start_time = time.time()
        self.total = 0
        self.yellow = 0
        self.redd = 0
        self.blue = 0
        self.delimiter = '||||app_delimiter||||'


    def on_data(self, data):
        """

        :param data: data from twitter api
        :return: process data and push it to redis
        """
        if (time.time() - self.start_time) < self.time_limit:

            all_data = json.loads(data)

            self.total += 1

            tweet = all_data["text"]

            user = all_data["user"]["screen_name"]

            tweet = tweet.lower()

            if re.search(r'teaminstinct', tweet):
                self.yellow += 1
            if re.search(r'teamvalor', tweet):
                self.redd +=1
            if re.search(r'teammystic', tweet):
                self.blue += 1

            now = datetime.datetime.now().replace(microsecond=0).time()
            red.publish('live', u'%s %s %s %s %s [%s]: %s' % (self.yellow,self.redd, self.blue, self.delimiter, self.total, now.isoformat(), tweet))

            return True

        else:
            return False

    def on_error(self, status):
        """

        :param status: error
        :return: deal with twitter 420 api error (420: when making many wrong streaming api requests)
        """
        if status == 420:
            print(status)
            return False


def call_twitter(word,time_limit):
    twitterStream = Stream(auth, Listener(time_limit))
    twitterStream.filter(track=word)


##############


if __name__ == '__main__':
    app.debug = True
    app.run()


