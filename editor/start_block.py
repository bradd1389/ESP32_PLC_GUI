from PyQt6.QtCore import QRectF
from .draggable_block import DraggableBlock

class StartBlock(DraggableBlock):
    def __init__(self, parent=None):
        rect = QRectF(0, 0, 80, 40)
        super().__init__(rect, "START", parent)
        # Remove all ports except bottom output
        for name in list(self.ports.keys()):
            if name != 'bottom':
                self.ports[name].setVisible(False)
        # Adjust the output port (bottom)
        self.ports['bottom'].setRect(rect.width()/2-7, rect.height()-4, 14, 14)
