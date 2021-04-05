Y_CENTRE = 0
X_CENTRE = 1
X_BBOX = 0
Y_BBOX = 0


class Decision(object):

    def __init__(self, name):
        self.centre = (240, 320)
        self.name = name
        self.x_preoffset = None
        self.y_preoffset = None

    def offset(self, rect):
        x_offset, y_offset = 0, 0


        w, h = rect[0][1]
        area = w*h
        print(w, h, area)

        # if 2000<= area <= 5000 and (40<h<130 and 60<w<100 or 40<w<130 and 60<h<100) :
        x_offset = rect[0][0][X_BBOX] - self.centre[X_CENTRE]
        y_offset = rect[0][0][Y_BBOX] - self.centre[Y_CENTRE]

        print(x_offset)

        if x_offset == 0:
            x_offset+=0.00001
        if y_offset == 0:
            y_offset+=0.00001


        if abs(x_offset) >= 80:
            x_offset = 2 * x_offset / abs(x_offset)
        elif abs(x_offset) >= 15:
            x_offset = 1 * x_offset / abs(x_offset)
        else:
            x_offset = 0 * x_offset / abs(x_offset)

        if abs(y_offset) >= 80:
            y_offset = 2 * y_offset / abs(y_offset)
        elif abs(y_offset) >= 15:
            y_offset = 1 * y_offset / abs(y_offset)
        else:
            y_offset = 0 * y_offset / abs(y_offset)

        x_offset = int(x_offset)
        y_offset = int(y_offset)
        print(x_offset, y_offset)
        return x_offset, y_offset

    def filtration(self, x_offset, y_offset, w, h):
        '''
        过滤偏移量，保证输出数据平滑
        '''
        area = h*w
        # print(area)
        # print(h, w)
        if self.x_preoffset is None and self.y_preoffset is None:
            pass
        else:
            self.x_preoffset = x_offset
            self.y_preoffset = y_offset

        if abs(x_offset - self.x_preoffset) <= 50 and abs(y_offset - self.y_preoffset) <= 50:
            return x_offset, y_offset
        else:
            return self.x_preoffset, self.y_preoffset


        if 3000<= area <= 5000 and (40<h<70 and 80<w<160 or 40<w<70 and 80<h<160) :
            armro_x = int((armro_x-480/2)*1)
            armro_y = int((armro_y-640/2)*1)
            # print(armro_x, armro_y)
        
        
#         h, w = i[0][1]