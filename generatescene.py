import random
def calculate_screen(screencfg):
    screencfg = screencfg['screens']
    totalheight = 0
    totalwidth = 0
    totalscreens = 0
    for row in screencfg['rows']:
        rowwidth = 0
        rowheight = 0
        for screen in row['row']:
            rowwidth += screen['width']
            rowheight = max(rowheight, screen['height'])
            totalscreens += 1
        row['width'] = rowwidth
        row['height'] = rowheight
        totalheight += rowheight
        totalwidth = max(totalwidth, rowwidth)
    return totalwidth, totalheight, totalscreens

def generate_complex_video(screencfg, audioinputs, basenoise=False,
    originalaudio=False, fullscreen=False, videoscnt=0):

    screenwidth, screenheight, totalscreens = calculate_screen(screencfg)
    cofilter = []
    cofilter.append(' -filter_complex ')
    #generate total screen
    cofilter.append('"nullsrc=size=' + repr(screenwidth) + 'x' + repr(screenheight
        ) + ' [base]')

    #we should have enough inputs in the correct place
    videocount = 0
    rowcount = 0
    rowposcount = 0

    if fullscreen:
        cofilter.append('[0:v] setpts=PTS-STARTPTS, scale=' + repr(screenwidth) +
        'x' + repr(screenheight) + ' [row0place0]')
    else:
        #scale all our videos according to the screen cfg
        for row in screencfg['screens']['rows']:
            for actrow in row['row']:
                cofilter.append('[' + repr(videocount
                    ) + ':v] setpts=PTS-STARTPTS, scale=' + repr(actrow['width'
                    ]) + 'x' + repr(actrow['height']) + ' [row' + repr(rowcount)
                    + 'place' + repr(rowposcount) + ']')
                videocount += 1
                rowposcount += 1
            rowposcount = 0
            rowcount += 1

    videocount = 0
    rowcount = 0
    rowposcount = 0

    #put the videos in the correct place on the overlay
    if fullscreen:
        cofilter.append('[base][row0place0] overlay=shortest:x=0:y=0 ')
        videocount = 1
    else:
        currlast = '[base]'
        currcount = 0
        heightoffset = 0
        widthoffset = 0
        for row in screencfg['screens']['rows']:
            for actrow in row['row']:
                newcurr = '[tmp' + repr(currcount) + ']'
                cofilter.append(currlast +'[row' + repr(rowcount) + 'place' +
                    repr(rowposcount) + '] overlay=shortest=1:x=' + repr(widthoffset)
                    + ':y=' + repr(heightoffset) + ' ')
                cofilter[-1] += newcurr
                widthoffset += actrow['width']

                currcount += 1
                currlast = newcurr
                videocount += 1
                rowposcount += 1
            heightoffset += row['height']
            widthoffset = 0
            rowposcount = 0
            rowcount += 1
        cofilter[-1] = cofilter[-1][:-len(currlast)]

    #put the audio in the correct place
    #end of videocount is start of audiocount
    audiocount = videocount

    #remove basenoise from inputs
    if basenoise:
        audioinputs = audioinputs[:-1]

    audioout = 'audioout' if basenoise else 'finalaudio'
    audioconcat = []
    audiostr = ''
    #you can't mix original audio with audiofiles yet
    if videoscnt > 1:
        if originalaudio:
            for x in xrange(videoscnt):
                audiostr += '[' + repr(x) + ':a]'
                print x
            audiostr += ' amerge=inputs=' + repr(videoscnt-1) + ' [' + audioout + ']'
        else:
            for audio in audioinputs:
                audiostr += '[' + repr(audiocount) + ':0]'
                audiocount += 1
            audiostr += (' concat=n=' + repr(audiocount-videocount) + ':v=0:a=1 [' +
                audioout + ']')
        audioconcat.append(audiostr)

    print basenoise, videocount
    if basenoise and videocount == 1:
        audioconcat.append('[0:a][' + repr(audiocount) +
            ':a] amerge=inputs=2 [finalaudio]')
    elif basenoise:
        audioconcat.append('[audioout][' + repr(audiocount) +
            ':a] amerge=inputs=2 [finalaudio]')



    cofilter += audioconcat

    cofilter.append(' " ')
    return cofilter




def generate_scene(scenecfg, screencfg, basepath):
    screenwidth, screenheight, totalscreens =  calculate_screen(screencfg)
    totalvideoinput = len(scenecfg['video']['files'])
    inputstring = ''
    fullscreen = False
    #video inputs
    if totalvideoinput != totalscreens:
        fillin = scenecfg['video'].get('fillin', 'noise')
    inputlist = []
    filedesclistn = [ fd for fd in scenecfg['video']['files'] if fd['position'].isdigit() ]
    inputlist = [None] * totalscreens

    #put videos in fixed position
    for filedesc in filedesclistn:
        inputstring = ' -i ' + basepath + filedesc['filename']
        pos = filedesc.get('position')
        if pos.isdigit():
            inputlist[int(pos)-1] = inputstring

    for filedesc in [fd for fd in scenecfg['video']['files'] if not
            fd['position'].isdigit()]:
        inputstring = ' -i ' + basepath + filedesc['filename']
        pos = filedesc.get('position')
        if pos == 'fullscreen':
            if totalvideoinput > 1:
                raise Exception("Only one file allowed for fullscreen")
            fullscreen = True
        if pos == 'random':
            while pos:
                pos = random.randint(0,len(inputlist)-1)
                if not inputlist[pos]:
                    inputlist[pos] = inputstring
                    pos = None


    if not fullscreen:
        for x in xrange(len(inputlist)):
            if not inputlist[x]:
                if fillin == 'noise':
                    inputlist[x] = ' -f rawvideo -video_size 320x140 -pixel_format yuv420p -framerate 25 -i /dev/urandom '
                if fillin == 'testimage':
                    inputlist[x] = ' -f lavfi -i testsrc '
                if fillin == 'black':
                    inputlist[x] = ' -f lavfi -i color=black'
    inputstring = ''.join(inputlist)

    #audio inputs
    audioinputs = []
    audionoise = False
    originalaudio = False
    if 'sound' in scenecfg:
        if 'files' in scenecfg['sound']:
            for filedesc in scenecfg['sound']['files']:
                audioinputs.append(' -i ' + basepath + filedesc['filename'])
        if scenecfg['sound'].get('options'):
            if scenecfg['sound']['options'].get('original'):
                originalaudio = True
            if scenecfg['sound']['options'].get('sort') == 'random':
                random.shuffle(audioinputs)
            if scenecfg['sound']['options'].get('add_base_noise'):
                audioinputs.append('  -ar 48000 -ac 2 -f s16le -i /dev/urandom ')
        audionoise = scenecfg['sound']['options'].get('add_base_noise')


    inputstring += ' '.join(audioinputs)
    complexfilter = generate_complex_video(screencfg, audioinputs, audionoise,
        originalaudio, fullscreen, totalvideoinput)
    endstr = []
    if audioinputs or (originalaudio and audionoise):
        endstr.append(" -map '[finalaudio]'")
    if scenecfg['length'] == 'shortest':
        endstr.append(" -shortest ")
    else:
        endstr.append(" -t " + scenecfg['length'])
    for item, rep in [('video', 'v'), ('sound', 'a')]:
        distort = scenecfg[item].get('distort')
        if distort:
            endstr.append(' -bsf:{0} noise={1}'.format(rep, distort)  )
    endstr.append(' -c:v libx264 -threads 4')

    #assemble final string
    return inputstring, complexfilter, endstr

