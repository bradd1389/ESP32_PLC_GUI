from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtGui import QPainterPath, QPen, QColor
from PyQt6.QtCore import Qt, QPointF
import math

class AutoRoutedWire(QGraphicsPathItem):
    def __init__(self, start_point, end_point, parent=None):
        super().__init__(parent)
        self.start_point = start_point
        self.end_point = end_point
        self.setPen(QPen(QColor("black"), 3))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(2)
        
        # Connection information
        from typing import Optional, TYPE_CHECKING
        if TYPE_CHECKING:
            from editor.draggable_block import DraggableBlock
        self.from_block: Optional['DraggableBlock'] = None
        self.from_port: Optional[str] = None
        self.to_block: Optional['DraggableBlock'] = None
        self.to_port: Optional[str] = None
        
        self.update_path()

    def update_path(self):
        """Create an auto-routed path with rounded 90-degree corners"""
        path = QPainterPath()
        
        start = self.start_point
        end = self.end_point
        
        # Calculate the routing path
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        
        # Minimum routing distance to avoid too sharp turns
        min_route_distance = 30
        corner_radius = 15  # Radius for rounded corners
        
        # If points are too close or aligned, use direct line
        if abs(dx) < 10 and abs(dy) < 10:
            path.moveTo(start)
            path.lineTo(end)
        elif abs(dx) < 10:  # Vertically aligned
            path.moveTo(start)
            path.lineTo(end)
        elif abs(dy) < 10:  # Horizontally aligned
            path.moveTo(start)
            path.lineTo(end)
        else:
            # Create L-shaped or Z-shaped routing
            path.moveTo(start)
            
            # Determine routing strategy based on relative positions
            if abs(dx) > abs(dy):
                # Route horizontally first
                mid_x = start.x() + dx * 0.6  # 60% of the way
                mid_point1 = QPointF(mid_x, start.y())
                mid_point2 = QPointF(mid_x, end.y())
                
                # Add rounded corners
                self._add_rounded_path(path, start, mid_point1, mid_point2, end, corner_radius)
            else:
                # Route vertically first
                mid_y = start.y() + dy * 0.6  # 60% of the way
                mid_point1 = QPointF(start.x(), mid_y)
                mid_point2 = QPointF(end.x(), mid_y)
                
                # Add rounded corners
                self._add_rounded_path(path, start, mid_point1, mid_point2, end, corner_radius)
        
        self.setPath(path)

    def _add_rounded_path(self, path, p1, p2, p3, p4, radius):
        """Add a path with rounded corners between four points"""
        # Line from p1 towards p2
        if (p2 - p1).manhattanLength() > radius * 2:
            # Calculate point before corner
            direction = p2 - p1
            length = math.sqrt(direction.x()**2 + direction.y()**2)
            if length > 0:
                unit_dir = QPointF(direction.x() / length, direction.y() / length)
                corner_start = QPointF(p2.x() - unit_dir.x() * radius, p2.y() - unit_dir.y() * radius)
                path.lineTo(corner_start)
                
                # Add rounded corner from p2 to p3
                if (p3 - p2).manhattanLength() > radius * 2:
                    direction2 = p3 - p2
                    length2 = math.sqrt(direction2.x()**2 + direction2.y()**2)
                    if length2 > 0:
                        unit_dir2 = QPointF(direction2.x() / length2, direction2.y() / length2)
                        corner_end = QPointF(p2.x() + unit_dir2.x() * radius, p2.y() + unit_dir2.y() * radius)
                        
                        # Create rounded corner
                        path.quadTo(p2, corner_end)
                        
                        # Continue to p3
                        if (p4 - p3).manhattanLength() > radius * 2:
                            direction3 = p4 - p3
                            length3 = math.sqrt(direction3.x()**2 + direction3.y()**2)
                            if length3 > 0:
                                unit_dir3 = QPointF(direction3.x() / length3, direction3.y() / length3)
                                corner_start2 = QPointF(p3.x() - unit_dir2.x() * radius, p3.y() - unit_dir2.y() * radius)
                                path.lineTo(corner_start2)
                                
                                # Final rounded corner
                                corner_end2 = QPointF(p3.x() + unit_dir3.x() * radius, p3.y() + unit_dir3.y() * radius)
                                path.quadTo(p3, corner_end2)
                                path.lineTo(p4)
                            else:
                                path.lineTo(p3)
                                path.lineTo(p4)
                        else:
                            path.lineTo(p3)
                            path.lineTo(p4)
                    else:
                        path.lineTo(p2)
                        path.lineTo(p3)
                        path.lineTo(p4)
                else:
                    path.lineTo(p2)
                    path.lineTo(p3)
                    path.lineTo(p4)
            else:
                path.lineTo(p2)
                path.lineTo(p3)
                path.lineTo(p4)
        else:
            # Too short for rounded corners, use straight lines
            path.lineTo(p2)
            path.lineTo(p3)
            path.lineTo(p4)

    def update_endpoints(self, start_point, end_point):
        """Update the wire endpoints and regenerate the path"""
        self.start_point = start_point
        self.end_point = end_point
        self.update_path()
