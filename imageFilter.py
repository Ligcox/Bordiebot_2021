from module import *


class imageFilter(module):
    name = "Empty Filter Control"

    def process(self, frame):
        return frame


class colorFilter(imageFilter):
    def __init__(self, hide_controls=True):
        self.controls = channel_filter_controls
        self.name = "ColorFilter"
        super().__init__(hide_controls)

    def process(self, frame):
        # Hard code channel number
        NUM_CHANNEL = 3
        if not frame.shape[2] == NUM_CHANNEL:
            # deal with BGR color frames only
            return frame
        target_color = [self.getControlVal('blueTarget'), self.getControlVal(
            'greenTarget'), self.getControlVal('redTarget')]
        tolerance = [self.getControlVal('blueTolerance'), self.getControlVal(
            'greenTolerance'), self.getControlVal('redTolerance')]
        channel_target = [
            [
                max(0, target_color[i]-tolerance[i]),
                min(255, target_color[i]+tolerance[i])
            ]
            for i in range(NUM_CHANNEL)]
        channel_masks = []
        final_mask = np.ones(frame.shape[:2], np.uint8)*255
        methods = self.getControlVal('maskMethod')
        for channel in range(NUM_CHANNEL):
            _, low_mask = cv2.threshold(
                frame[:, :, channel], channel_target[channel][0], 255, methods[0])
            _, high_mask = cv2.threshold(
                frame[:, :, channel], channel_target[channel][1], 255, methods[1])
            channel_masks.append(cv2.bitwise_and(low_mask, high_mask))
            final_mask = cv2.bitwise_and(final_mask, channel_masks[channel])
        output = cv2.bitwise_and(frame, frame, mask=final_mask)
        self.updateProcess(final_mask, channel_masks)
        return output

    def updateProcess(self, final_mask, channel_masks):
        if not (self.getControlVal('silent') or (final_mask is None)):
            blueMask = channel_masks[0].copy()
            cv2.putText(blueMask, 'BlueChannelMask', (0, 20),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            greenMask = channel_masks[1].copy()
            cv2.putText(greenMask, 'GreenChannelMask', (0, 20),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            redMask = channel_masks[2].copy()
            cv2.putText(redMask, 'RedChannelMask', (0, 20),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            finalMask = final_mask.copy()
            cv2.putText(finalMask, 'FinalMask', (0, 20),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
            row1 = np.concatenate((finalMask, blueMask), axis=1)
            row2 = np.concatenate((greenMask, redMask), axis=1)
            img = np.concatenate((row1, row2), axis=0)
        else:
            img = BLANK_IMG
        cv2.imshow(self.control_window_name, img)
