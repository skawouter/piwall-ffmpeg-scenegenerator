class VideoFile(object):
    def __init__(self, filename, position='random', vtype='file', startat=0):
        self.filename = filename
        self.position = position
        self.vtype = vtype
        self.startat = startat

    def get_input_line(self):
        if self.vtype == 'file':
            if self.startat:
                return ' -itsoffset {0} -i {1}'.format(str(self.startat),
                    self.filename)
            return ' -i {0}'.format(self.filename)
        if self.vtype == 'noise':
            return ' -f rawvideo -video_size 320x140 -pixel_format yuv420p -framerate 25 -i /dev/urandom '
        if self.vtype == 'testimage':
            return  ' -f lavfi -i testsrc '
        if self.vtype == 'black':
            return  ' -f lavfi -i color=black'
        if self.vtype =='concat':
            return ' -i "concat:' + self.filename+ '" '

    def __repr__(self):
        return '[{0}:: {1}]'.format(self.filename, self.vtype)

class AudioFile(VideoFile):
    def __init__(self, filename, vtype='file', startat=0):
        self.filename = filename
        self.vtype = vtype
        self.startat = startat

    def get_input_line(self):
        if self.vtype == 'file':
            return ' -i {0}'.format(self.filename)

        if self.vtype == 'noise':
            return '  -ar 48000 -ac 2 -f s16le -i /dev/urandom '
