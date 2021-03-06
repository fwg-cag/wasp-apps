import wasp
import icons
import time

class StopwatchApp():
    """Simple Timer.
    """
    NAME = 'Timer'
    ICON = icons.app

    def __init__(self):
        self.last_press = -1
        self.time = 0
        self.state = 0

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def tick(self, ticks):
        if self.state < 0:
            self.update()

    def foreground(self):
        """Activate the application."""
        self.on_screen = ( -1, -1, -1, -1, -1, -1 )
        self.draw()
        wasp.system.request_tick(97)
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.BUTTON)

    def press(self, button, state):
        if (time.time() - self.last_press) <= 0.5:
            self.new()
            self.last_press = -1
        else:
            self.stop()
            self.last_press = time.time()

    def touch(self, event):
        if (time.time() - self.last_press) <= 0.5:
            self.new()
            self.last_press = -1
        else:
            self.stop()
            self.last_press = time.time()

    def new(self):
        self.state = 0
        self.update()

    def stop(self):
        if self.state < 0:
            self.state = time.time() - self.time
        else:
            self.time = time.time() - self.state
            self.state = -1
        self.update()

    def draw(self, init=False):
        """Redraw the display from scratch."""
        wasp.watch.display.mute(True)
        draw = wasp.watch.drawable
        draw.fill()
        draw.string('Timer', 0, 6, width=240)
        self.update()
        wasp.watch.display.mute(False)

    def convert(self, seconds):
        m = seconds // 60
        s = seconds % 60 // 1
        ms = seconds % 60 % 1 // 0.01
        return '{:02.0f}:{:02.0f}:{:02.0f}'.format(m, s, ms)

    def update(self):
        draw = wasp.watch.drawable
        if self.state < 0:
            if((time.time() - self.time) > 99*60):
                self.new()
            draw.string('{}'.format(self.convert(time.time() - self.time)), 0, 108, width=240)
        else:
            draw.string('{}'.format(self.convert(self.state)), 0, 108, width=240)
