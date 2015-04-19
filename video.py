from vatypes import VideoFile
import random
class Video(object):
    def __init__(self, videocfg, basepath='', length=1):
        self.files = []
        self.fillin = videocfg.get('fillin')
        self.distort = videocfg.get('distort')
        self.length = videocfg.get('length')
        self.fullscreen = False
        self.options = videocfg.get('options', {})
        self.loopseqall = 0
        for i in self.options:
            if i['option'] == 'loop_seq_all':
                self.loopseqall = i.get('repeat', 1)

        for fil in videocfg['files']:
            self.files.append(VideoFile(basepath + fil['filename'],
                fil['position'], startat=fil.get('startat', 0)))
        scrl = length - len(self.files)
        for i in xrange(scrl):
            self.files.append(VideoFile('', vtype=self.fillin))


    def get_input_list(self, length=1):
        inputlist = []
        for fil in self.files[:]:
            if fil.position.isdigit():
                oldpos = self.files[fil.position]
                if oldpos.position == fil.position:
                    raise Exception("2 Files fighting for same screen check scenecfg")
                oldi = self.files.index(fil)
                self.files[fil.position] = fil
                self.files[oldi] = oldpos

        for fil in self.files[:]:
            if fil.position == 'random':
                pos = random.randint(0,len(self.files)-1)
                oldf = self.files[pos]
                while oldf.position.isdigit():
                    pos = random.randint(0,len(self.files)-1)
                    oldf = self.files[pos]
                newi = self.files.index(fil)
                self.files[pos] = fil
                self.files[newi] = oldf
            if fil.position == 'fullscreen':
                self.fullscreen = True
                self.files = [ fil ]
                break

        inputlist = [ i.get_input_line() for i in self.files ]

        return inputlist

    def get_distort_line(self):
        if self.distort:
            return ' -bsf:v noise={0}'.format(self.distort)
        return ''

    def get_video_layers(self, scr):
        layers = []
        #inputs
        if self.fullscreen:
            layers.append('[0:v] scale=' +
                repr(scr.get_total_width()) + 'x' +
                repr(scr.get_total_height()) + ' [row0place0]')
        else:
            row = 0
            rowposcount = 0
            videocount = 0
            for i in xrange(len(scr.screens)):
                screen = scr.screens[i]
                r = screen.row
                if row != r:
                    rowposcount = 0
                    row = r
                hue = ',hue=s=0 ' if self.files[i].vtype == 'noise' else ''
                print hue
                layers.append('[{videon}:v] scale={width}x{height} {hue}'
                   '[row{rown}place{rowposn}]'.format(
                   videon=i, width=screen.width, height=screen.height,
                   rown=screen.row, rowposn=rowposcount, hue=hue))

                videocount += 1
                rowposcount += 1


        #layering
        if self.fullscreen:
            layers.append('[base][row0place0] overlay=shortest=1:x=0:y=0 ')
            videocount = 1
        else:
            currlast = '[base]'
            currcount = 0
            heightoffset = 0
            widthoffset = 0
            rowposcount = 0
            row = 0
            concatdone = False
            for i in xrange(len(scr.screens)):
                screen = scr.screens[i]
                if screen.row != row:
                    row = screen.row
                    heightoffset += scr.get_screen_row_size(screen)[1]
                    widthoffset = 0
                    rowposcount = 0
                newcurr = '[tmp' + repr(currcount) + ']'
                sh = 1 if self.length == 'shortest' else 0
                layers.append('{currlast} [row{rown}place{rowposn}] overlay='
                'shortest={shortest}:x={x}:y={y}'.format(
                currlast=currlast, rown=row, rowposn=rowposcount,
                x=widthoffset, y=heightoffset, shortest=sh))
                layers[-1] += newcurr
                widthoffset += screen.width

                currcount += 1
                currlast = newcurr
                videocount += 1
                rowposcount += 1
            layers[-1] = layers[-1][:-len(currlast)]

        return layers, videocount
