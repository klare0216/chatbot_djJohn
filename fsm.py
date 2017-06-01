from transitions.extensions import GraphMachine
import urllib.request
import urllib.parse
import re

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )
        self.vec = {
                'song': 0,
                'artist': 0,
                'style': 0,
                'negative': 0,
                'more': 0,
            }
        self.data = ''
        self.cmd = {'song':'音樂', 'artist':'歌手', 'style':'風格'}
        self.yeslist = {'y':0,'yes':0,'好':0,'ok':0,'好阿':0,'好喔':0}
        self.nolist = {'no':0,'not':0,'不要':0,'禁止':0,'不':0,'n':0}
        self.show = 1
        self.song_list = []
    # to analys which question is the user ask    
    def analys(self, update):
        text = update.message.text
        # initialize
        for key in self.vec.keys():
          self.vec[key] = 0
        # enable/unalbe diagram show
        if text == '#show':
            self.show = 1
            return
        elif text == '#nshow':
            self.show = 0
            return
        # analys the command  
        for key in self.cmd:
            if text.find(self.cmd[key]) != -1:
                self.vec[key] = 1
                split = text.split()
                if len(split) == 2:
                    self.data = split[1]
                # 看看是否是否定句子
                elif len(split) == 3 and split[1] in self.nolist:
                    self.data = split[2]
                    self.vec['negative'] = 1
                return
        for key in self.yeslist:
            if text.lower() == key:
                self.vec['more'] = 1
                return
        for key in self.nolist:
            if text.lower() == key:
                self.vec['more'] = 0
                update.message.reply_text("知道拉～換點別的～")
                return
        update.message.reply_text("聽不懂欸>___<")

    def parse_youtube(self,keyword):
        url = 'https://www.youtube.com/results?' 
        print(keyword)
        url_right = urllib.parse.urlencode({'search_query':keyword})
        print(url_right)
        url = url + url_right
        print(url)
        website = urllib.request.urlopen(url)
        try:
            data = website.read().decode('utf-8')
        except exception as e:
            #print(type(e), str(e))
            print('e occur')
        song_re = re.compile('<td class=\"watch-card-main-col\" title=\"([^\"]*)\" colspan=\"2\">.*?<a href=\"([^\"]*)\"')
        
        self.song_list = song_re.findall(data)
        print(self.song_list)


    def parse_song(self,keyword):
        url = 'https://www.youtube.com/results?' 
        print(keyword)
        url_right = urllib.parse.urlencode({'search_query':keyword})
        print(url_right)
        url = url + url_right
        print(url)
        website = urllib.request.urlopen(url)
        try:
            data = website.read().decode('utf-8')
        except exception as e:
            #print(type(e), str(e))
            print('e occur')
        song_re = re.compile('<td class=\"watch-card-main-col\" title=\"([^\"]*)\" colspan=\"2\">.*?<a href=\"([^\"]*)\"')
        
        self.song_list = song_re.findall(data)
        print(self.song_list)



    def is_going_to_song(self, update):
        return self.vec['song'] == 1

    def is_going_to_artist(self, update):
        return self.vec['artist'] == 1
    
    def is_going_to_style(self, update):
        return self.vec['style'] == 1
    

    def on_enter_root(self, update):
        update.message.reply_text("想聽什麼音樂呢ouo?")

    def on_enter_song(self, update):
        update.message.reply_text("查詢"+self.vec['song']+'中...')
        if (self.vec['negative'] == 1):
            self.black(update)
        else:
            update.message.reply_text("查詢"+self.vec['song']+'中...')
            self.song_next(update)

    def on_exit_song(self, update):
        print('Leaving song')

    def on_enter_artist(self, update):
        print('進入artist')
        if (self.vec['negative'] == 1):
            self.black(update)
        else:
            update.message.reply_text("查詢"+self.data+'中...')
            self.parse_youtube(self.data)
            self.to_spi_list(update)

    def on_exit_artist(self, update):
        print('Leaving artist')

    def on_enter_style(self, update):
        if (self.vec['negative'] == 1):
            self.black(update)
        else:
            update.message.reply_text("查詢"+self.data+'中...')
            self.parse_youtube(self.data)
            self.to_spi_list(update)

    def on_exit_style(self, update):
        print('Leaving style')


    def on_enter_spi_music(self,update):
        print('enter_spi_music')
        self.go_back(update)
        
    def on_exit_spi_music(self,update):
        print('leave_spi_music')
 
    def on_enter_spi_music_list(self,update):
        print('enter_spi_music_list')
        self.spi_music_list_next(update)
                
    def on_exit_spi_music_list(self,update):
        print('leave_spi_music_list')
       

    
    def on_enter_more_spi_music(self,update):
        print('enter_more_spi_music')
        # 依序存進要回傳的資訊裡面
        msg = ''
        # 如果沒有歌了就回傳訊息並回到root
        if len(self.song_list) == 0: 
            update.message.reply_text('聽聽別的了吧oAo~')
            self.go_back(update)
        # 每次pop三首歌出來
        for i in range(3):
            if len(self.song_list) <= 0: break
            unit = self.song_list.pop()
            print(unit)
            msg = msg + unit[0] + '\n' 
            msg = msg + 'https://www.youtube.com/' + unit[1] + '\n'
        update.message.reply_text(msg)
        update.message.reply_text('想要更多'+self.data+'嗎(ﾟ∀。)?')
        
        
    def on_exit_more_spi_music(self,update):
        print('leave_more_spi_music')
    
    def on_enter_black_list(self,update):
        update.message.reply_text("查詢除了"+self.data+'的音樂中...')
        print('enter_black_list')
        self.black_list_next(update);
        
    def on_exit_black_list(self,update):
        print('leave_black_list')
   
    def on_enter_black_list_song(self,update):
        print('enter_black_list_song')
        update.message.reply_text('很抱歉,我還不夠厲害\n・゜・(PД`q｡)・゜・\n原諒我我會更努力變強的！')
        self.black_list_song_next(update)

    def on_exit_black_list_song(self,update):
        print('leave_black_list_song')
 
    def on_enter_more_black_song(self,update):
        print('enter_more_black_song')
        self.go_back(update)
        
    def on_exit_more_black_song(self,update):
        print('leave_more_black_song')
