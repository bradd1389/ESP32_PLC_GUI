from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem, QGraphicsSceneMouseEvent
from PyQt6.QtGui import QPainterPath, QPen, QColor
from PyQt6.QtCore import Qt, QPointF

class WireSegment(QGraphicsPathItem):
    def __init__(self, points, parent=None):
        super().__init__(parent)
        self.points = points[:]  # List of QPointF
        self.setPen(QPen(QColor("black"), 3))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(2)
        self.update_path()
        self._selected_handle = None
        # Connection information
        from typing import Optional, TYPE_CHECKING
        if TYPE_CHECKING:
            from editor.draggable_block import DraggableBlock
        self.from_block: Optional['DraggableBlock'] = None
        self.from_port: Optional[str] = None
        self.to_block: Optional['DraggableBlock'] = None
        self.to_port: Optional[str] = None

    def update_path(self):
        path = QPainterPath()
        if self.points:
            path.moveTo(self.points[0])
            for pt in self.points[1:]:
                path.lineTo(pt)
        self.setPath(path)

    def mousePressEvent(self, event):
        # Select nearest handle (bend point)
        min_dist = 16
        self._selected_handle = None
        if event is not None:
            for i, pt in enumerate(self.points):
                if (pt - event.scenePos()).manhattanLength() < min_dist:
                    self._selected_handle = i
                    break
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._selected_handle is not None and event is not None:
            self.points[self._selected_handle] = event.scenePos()
            self.update_path()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._selected_handle = None
        super().mouseReleaseEvent(event)

    def add_bend(self, pt: QPointF):
        self.points.append(pt)
        self.update_path()

    def set_endpoints(self, start: QPointF, end: QPointF):
        if len(self.points) < 2:
            self.points = [start, end]
        else:
            self.points[0] = start
            self.points[-1] = end
        self.update_path()
