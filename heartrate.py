import wasp
import icons
from watch import i2c

class HeartrateApp():
    """Simple Heartrate App.
    """
    NAME = 'BPM'
    ICON = icons.app

    def __init__(self):
        self.address = 0x44
        self.en = 0

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        self.update()

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self._enable()
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.BUTTON)

    def press(self, button, state):
        if state == 0:
           return
        if self.en:
            self._disable()
        else:
            self._enable()
        self.update()

    def draw(self, init=False):
        """Redraw the display from scratch."""
        wasp.watch.display.mute(True)
        draw = wasp.watch.drawable
        draw.fill()
        draw.string('BPM', 0, 6, width=240)
        self.update()
        wasp.watch.display.mute(False)

    def update(self):
        draw = wasp.watch.drawable
        hrs, als = self._read_hrs(), self._read_als()
        if self.en and hrs and als:
            draw.string('{} bpm'.format(int(hrs / als)), 0, 108, width=240)
        else:
            draw.string('-- bpm', 0, 108, width=240)

    def _enable(self):
        buf = [[0x16, 0x66], [0x17, 0x10], [0x0c, 0x68], [0x01, 0xe8]]
        for i in range(len(buf)):
            i2c.writeto_mem(self.address, buf[i][0], bytearray([buf[i][1]]))
        self.en = 1

    def _set_adc_res(self, res=6):
        i2c.writeto_mem(self.address, 0x16, bytearray([(0x60 | (res << 2))]))

    def _set_hrs_gain(self, gain=4):
        i2c.writeto_mem(self.address, 0x17, bytearray([(gain << 2)]))

    def _read_hrs(self):
        val = 0
        buf = bytearray(1)
        try:
            i2c.readfrom_mem_into(self.address, 0x09, buf)
            val |= ((buf[0] & 0xffff) << 8)
            i2c.readfrom_mem_into(self.address, 0x0a, buf)
            val |= (buf[0] << 4)
            i2c.readfrom_mem_into(self.address, 0x0f, buf)
            val = ((val | buf[0]) << 2)
            return val
        except OSError:
            return None

    def _read_als(self):
        val = 0
        buf = bytearray(1)
        try:
            i2c.readfrom_mem_into(self.address, 0x0d, buf)
            val |= (buf[0] << 8)
            i2c.readfrom_mem_into(self.address, 0x08, buf)
            val |= (buf[0] << 3)
            i2c.readfrom_mem_into(self.address, 0x0e, buf)
            val |= buf[0]
            return val
        except OSError:
            return None

    def _disable(self):
        i2c.writeto_mem(self.address, 0x01, bytearray([0x68]))
        self.en = 0
