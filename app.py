import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine


API_TOKEN = ''
WEBHOOK_URL = ''

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'root',
        'song',
        'artist',
        'style',
        'black_list',
        'black_list_song',
        'spi_music_list',
        'spi_music',
        'more_black_song',
        'more_spi_music'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'root',
            'dest': 'song',
            'conditions': 'is_going_to_song',
        },
        {
            'trigger': 'advance',
            'source': 'root',
            'dest': 'artist',
            'conditions': 'is_going_to_artist'
        },
        {
            'trigger': 'advance',
            'source': 'root',
            'dest': 'style',
            'conditions': 'is_going_to_style'
        },
        {
            'trigger': 'song_next',
            'source': 'song',
            'dest': 'spi_music',
        },
        {
            'trigger': 'black_list_next',
            'source': 'black_list',
            'dest': 'black_list_song',
        },
        {
            'trigger': 'to_spi_list',
            'source': [
                'artist',
                'style'
              ],
            'dest': 'spi_music_list',
        },
        {
            'trigger': 'go_back',
            'source': [
                'more_black_song',
                'more_spi_music',
                'spi_music_list',
                'spi_music',
                'black_list_song'
            ],
            'dest': 'root'
        },
        {
            'trigger': 'black',
            'source': [
                'song',
                'artist',
                'style'
              ],
            'dest': 'black_list',
        },
        {
            'trigger': 'black_list_song_next',
            'source': [
                'black_list_song',
                'more_black_song'
                ],
            'dest': 'more_black_song'
        },
        {
            'trigger': 'spi_music_list_next',
            'source': [
                'spi_music_list',
                'more_spi_music'
                ],
            'dest': 'more_spi_music'
        }
    ],
    initial='root',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    msg = update.message.text
    chat_id = update.message.chat_id
    # run fsm
    machine.analys(update)
    state = machine.state 
    if case_0(state):
        machine.advance(update)    
    elif case_1(state):
        if machine.vec['more'] == 1:
            machine.spi_music_list_next(update)
        else: 
            machine.go_back(update)   
    elif case_2(state):
        if machine.vec['more'] == 1:
            machine.black_list_song_next(update)
        else: 
            machine.go_back(update)

    # send the photo of fsm
    if machine.show == 1:
        machine.get_graph().draw('my_state_diagram.png', prog='dot')    
        print('send_fsm_diagram')
        with open('my_state_diagram.png','rb') as photo:
            bot.send_photo(chat_id=chat_id, photo=photo);
    
    print('####now state is ' + machine.state)
    return 'ok'

def case_0(text):
    return  machine.state == 'root'

def case_1(text):
    return  machine.state == 'spi_music_list' or machine.state == 'more_spi_music' 

def case_2(text):
    return  machine.state == 'black_list_song' or machine.state == 'more_black_song' 

@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()
