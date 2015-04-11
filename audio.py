from vatypes import AudioFile, VideoFile
import random
class Audio(object):
    def __init__(self, audiocfg, basepath, videocfg):
        self.distort = audiocfg.get('distort')
        self.fillin = audiocfg.get('fillin')
        self.basenoise = audiocfg.get('options', {}).get('add_base_noise')
        self.sort = audiocfg.get('options', {}).get('sort')
        self.original = audiocfg.get('options', {}).get('original')
        self.files = []
        self.audioout = False
        if not self.original:
            if 'files' in audiocfg:
                for fil in audiocfg['files']:
                    self.files.append(AudioFile(basepath + fil['filename']))
        else:
            for fil in [f for f in videocfg.files if f.vtype == 'file']:
                self.files.append(AudioFile(fil.filename, startat=int(fil.startat *
                1000)))
        if self.basenoise:
            self.files.append(AudioFile('', vtype='noise'))

    def get_input_list(self):
        inputlist = []
        for fil in self.files:
            if fil.vtype != 'noise':
                inputlist.append(fil.get_input_line())
        if self.sort == 'random':
            random.shuffle(inputlist)

        if self.basenoise:
            inputlist += [ fil.get_input_line() for fil in self.files if fil.vtype
                == 'noise' ]

        return inputlist

    def get_distort_line(self):
        if self.distort:
            return ' -bsf:a noise={0}'.format(self.distort)
        return ''

    def get_audio_layers(self, videofiles):
        layers = []
        vcount = origcount = len(videofiles)
        if self.basenoise:
            self.audioout = 'audioout'
        else:
            self.audioout = 'finalaudio'
        audioinputs = []
        if self.original:
            for audfil in [ fil for fil in self.files if fil.vtype == 'file']:
                if audfil.startat:
                    layers.append('[' + repr(vcount) + (':a] aformat=sample_fmts='
                    'fltp:sample_rates=44100:channel_layouts=mono,'
                    'adelay={0} [audio{1}]').format( str(audfil.startat),
                    str(vcount)))
                else:
                    layers.append('[' + repr(vcount) + (':a] aformat=sample_fmts='
                    'fltp:sample_rates=44100:channel_layouts=mono'
                    ' [audio{0}]').format(str(vcount)))
                audioinputs.append('[audio' + repr(vcount) + ']')
                vcount += 1
            layers.append('{0} amix=inputs={1} [{2}]'.format(
                ''.join(audioinputs), len(audioinputs), self.audioout))
        else:
            for audfil in [ fil for fil in self.files if fil.vtype == 'file']:
                audioinputs.append('[' + repr(vcount) + ':0]')
                vcount += 1

            print 'no original', audioinputs
            if len(audioinputs) > 1:
                layers.append(''.join(audioinputs) + ' concat=n=' + repr(
                len(audioinputs)) + ':v=0:a=1 [' + self.audioout + ']')
            else:
                self.audioout = False

        if self.basenoise:
            self.basenoisepos = self.files.index([fil for fil in self.files if
                fil.vtype == 'noise'][0]) + len(videofiles)

        if self.audioout and self.basenoise:
            layers.append('[' + self.audioout + '][' + str(self.basenoisepos)
                + ':a] amerge=inputs=2 [finalaudio]')

        return layers

    def get_finish_line(self):
        if not self.audioout and self.basenoise:
            return ' -map ' + str(self.basenoisepos ) + ':0'
        elif self.audioout:
            return " -map '[finalaudio]' "
        else:
            return ''
