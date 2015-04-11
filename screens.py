class Screen(object):
    def __init__(self, cfg):
        self.name = cfg['screen']
        self.width = cfg['width']
        self.height = cfg['height']

    def __str__(self):
        return '{0}, {1}x{2}'.format(self.name, self.width, self.height)

    def __repr__(self):
        return self.__str__()

class Screens(object):
    def __init__(self, cfg, basepath):
        self.totalheight = 0
        self.totalwidth = 0
        self.totalscreens = 0
        cfg = cfg['screens']
        self.screens = []
        rowcount = 0
        for row in cfg['rows']:
            rowwidth = 0
            rowheight = 0
            for screen in row['row']:
                rowwidth += screen['width']
                rowheight = max(rowheight, screen['height'])
                self.totalscreens += 1
                scr = Screen(screen)
                scr.row = rowcount
                self.screens.append(scr)
            rowcount += 1

            self.totalheight += rowheight
            self.totalwidth = max(self.totalwidth, rowwidth)

    def get_total_width(self):
        return self.totalwidth
    def get_total_height(self):
        return self.totalheight
    def total_screens(self):
        return self.totalscreens

    def get_screen_row_size(self, scr):
        row = [s for s in self.screens if s.row == scr.row ]
        return max(s.width for s in row), max(s.height for s in row)
