# Special StartBlock class

# Place StartBlock definition after DraggableBlock

from PyQt6.QtWidgets import QPushButton

# Minimal DraggableButton implementation for Toolbox
class DraggableButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(False)
        self._drag_start_pos = None

    def mousePressEvent(self, e):
        from PyQt6.QtCore import Qt
        if e is not None and hasattr(e, 'button') and e.button() == Qt.MouseButton.LeftButton:
            if hasattr(e, 'pos') and e.pos() is not None:
                self._drag_start_pos = e.pos()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, a0):
        if a0 is not None and hasattr(a0, 'pos') and a0.pos() is not None and self._drag_start_pos is not None:
            if (a0.pos() - self._drag_start_pos).manhattanLength() > 10:
                from PyQt6.QtGui import QDrag
                from PyQt6.QtCore import QMimeData
                drag = QDrag(self)
                mime = QMimeData()
                mime.setText(self.text())
                drag.setMimeData(mime)
                drag.exec()
                self._drag_start_pos = None
        super().mouseMoveEvent(a0)
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem
from PyQt6.QtGui import QColor, QPen, QBrush
from PyQt6.QtCore import QPointF, QTimer, QRectF
from PyQt6.QtCore import QLineF
from PyQt6.QtCore import Qt

# PortEllipse definition (add if missing)
class PortEllipse(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, parent, which):
        super().__init__(x, y, w, h, parent)
        self.setBrush(QColor("darkblue"))
        self.setZValue(parent.zValue() + 1)
        self.setAcceptHoverEvents(True)
        self.block = parent
        self.which = which

    def hoverEnterEvent(self, event):
        # Only show hover if port is available (darkblue)
        current_brush = self.brush()
        if current_brush.color() == QColor("darkblue"):
            self.setBrush(QColor("lightblue"))
        QGraphicsEllipseItem.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        # Restore original color from parent block
        if hasattr(self.block, 'update_port_colors'):
            self.block.update_port_colors()
        QGraphicsEllipseItem.hoverLeaveEvent(self, event)
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtCore import QPointF, QTimer

from PyQt6.QtWidgets import QGraphicsItem

class DraggableBlock(QGraphicsItem):
    # Context menu and port selection logic removed for simplicity

    def __init__(self, rect=QRectF(0,0,150,40), text="", parent=None):
        super().__init__(parent)
        self._rect = rect
        self._brush = QBrush(QColor(220, 220, 220))
        self._pen = QPen(QColor(60, 60, 60), 2)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | 
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        # Add text label
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(QColor(30, 30, 30))
        self._center_text()
        
        # Four port system: top, left, right, bottom
        port_size = 12
        self.ports = {
            'top': PortEllipse(rect.width()/2-port_size/2, -port_size/2, port_size, port_size, self, 'top'),
            'left': PortEllipse(-port_size/2, rect.height()/2-port_size/2, port_size, port_size, self, 'left'),
            'right': PortEllipse(rect.width()-port_size/2, rect.height()/2-port_size/2, port_size, port_size, self, 'right'),
            'bottom': PortEllipse(rect.width()/2-port_size/2, rect.height()-port_size/2, port_size, port_size, self, 'bottom')
        }
        
        # Initially all ports are available, none assigned as input/output
        self.input_ports = set()  # Multiple input ports allowed
        self.output_port = None  # Only one output port allowed
        self.in_wires = []
        self.out_wires = []
        self.update_port_colors()

    def update_port_positions(self):
        """Update port positions based on current rect size"""
        port_size = 12
        rect = self._rect
        
        # Update port positions
        self.ports['top'].setRect(rect.width()/2-port_size/2, -port_size/2, port_size, port_size)
        self.ports['left'].setRect(-port_size/2, rect.height()/2-port_size/2, port_size, port_size)
        self.ports['right'].setRect(rect.width()-port_size/2, rect.height()/2-port_size/2, port_size, port_size)
        self.ports['bottom'].setRect(rect.width()/2-port_size/2, rect.height()-port_size/2, port_size, port_size)

    def set_active_ports(self, in_port, out_port):
        pass  # No port selection

    def assign_input_port(self, port_name):
        """Assign an input port - multiple inputs allowed once output is set"""
        if port_name in self.ports and port_name != self.output_port:
            # If output port is assigned, any remaining port can be input
            # If no output port yet, any port can be first input
            self.input_ports.add(port_name)
            self.update_port_colors()
            return True
        return False

    def assign_output_port(self, port_name):
        """Assign the output port - only one output allowed"""
        # Can use any port except already assigned input ports as output
        if port_name in self.ports and port_name not in self.input_ports:
            # If we already have an output port and it's different, 
            # we need to replace it (single output rule)
            self.output_port = port_name
            self.update_port_colors()
            return True
        return False

    def get_available_ports(self):
        """Get list of ports that can still be used"""
        used_ports = set(self.input_ports)  # Start with all input ports
        if self.output_port:
            used_ports.add(self.output_port)
        return [name for name in self.ports.keys() if name not in used_ports]

    def reset_ports(self):
        """Reset port assignments completely when all wires are removed"""
        if not self.in_wires:
            self.input_ports.clear()
            # When inputs are disconnected, output port can be reassigned to any of the 4 positions
        if not self.out_wires:
            self.output_port = None
        self.update_port_colors()

    def remove_input_port(self, port_name):
        """Remove a specific input port when its wire is disconnected"""
        if port_name in self.input_ports:
            self.input_ports.discard(port_name)
            self.update_port_colors()

    def update_port_colors(self):
        for name, port in self.ports.items():
            if name in self.input_ports and self.in_wires:
                port.setBrush(QColor("orange"))  # Input port with wire
            elif name == self.output_port and self.out_wires:
                port.setBrush(QColor("green"))   # Output port with wire
            else:
                port.setBrush(QColor("darkblue"))  # Available port


    def _center_text(self):
        """Center text within the block bounds"""
        if self.text_item:
            text_bounds = self.text_item.boundingRect()
            x = (self._rect.width() - text_bounds.width()) / 2
            y = (self._rect.height() - text_bounds.height()) / 2
            self.text_item.setPos(x, y)

    def setText(self, text):
        self.text_item.setPlainText(text)
        self._center_text()

    def _update_wires(self):
        # TODO: Implement wire update logic if needed
        pass

    def portScenePos(self, which, port_name=None):
        # which: 'in' or 'out', port_name: specific port for input
        if which == 'in' and port_name and port_name in self.input_ports:
            port = self.ports.get(port_name)
            if port:
                return port.mapToScene(port.rect().center())
        elif which == 'out' and self.output_port:
            port = self.ports.get(self.output_port)
            if port:
                return port.mapToScene(port.rect().center())
        elif which == 'in' and self.input_ports and not port_name:
            # Return first input port if no specific port requested
            first_input = next(iter(self.input_ports))
            port = self.ports.get(first_input)
            if port:
                return port.mapToScene(port.rect().center())
        return None

    def itemChange(self, change, value):
        """Handle item changes, specifically position changes to update connected wires"""
        result = super().itemChange(change, value)
        
        # Update wires both during position change and after it completes
        if change in (QGraphicsItem.GraphicsItemChange.ItemPositionChange, 
                     QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged):
            # Use QTimer to defer wire updates to avoid issues during drag operations
            QTimer.singleShot(0, self._update_connected_wires)
        
        return result

    def _update_connected_wires(self):
        """Update all wires connected to this block"""
        # Import here to avoid circular imports
        from editor.auto_routed_wire import AutoRoutedWire
        from editor.wire_segment import WireSegment
        
        # Update all outgoing wires (this block is the source)
        for wire in self.out_wires:
            if isinstance(wire, AutoRoutedWire):
                # Get current positions
                start_pos = self.portScenePos('out')
                if hasattr(wire, 'to_block') and wire.to_block and hasattr(wire, 'to_port') and wire.to_port:
                    end_port = wire.to_block.ports.get(wire.to_port)
                    if end_port and start_pos is not None:
                        end_pos = end_port.mapToScene(end_port.rect().center())
                        wire.update_endpoints(start_pos, end_pos)
            elif isinstance(wire, WireSegment):
                # Handle legacy WireSegment wires by updating their points
                start_pos = self.portScenePos('out')
                if hasattr(wire, 'to_block') and wire.to_block and hasattr(wire, 'to_port') and wire.to_port:
                    end_port = wire.to_block.ports.get(wire.to_port)
                    if end_port and start_pos is not None:
                        end_pos = end_port.mapToScene(end_port.rect().center())
                        wire.points = [start_pos, end_pos]
                        wire.update_path()
        
        # Update all incoming wires (this block is the destination)
        for wire in self.in_wires:
            if isinstance(wire, AutoRoutedWire):
                # Get current positions
                if hasattr(wire, 'from_block') and wire.from_block and hasattr(wire, 'from_port') and wire.from_port:
                    start_port = wire.from_block.ports.get(wire.from_port)
                    end_pos = self.portScenePos('in')
                    if start_port and end_pos is not None:
                        start_pos = start_port.mapToScene(start_port.rect().center())
                        wire.update_endpoints(start_pos, end_pos)
            elif isinstance(wire, WireSegment):
                # Handle legacy WireSegment wires by updating their points
                if hasattr(wire, 'from_block') and wire.from_block and hasattr(wire, 'from_port') and wire.from_port:
                    start_port = wire.from_block.ports.get(wire.from_port)
                    end_pos = self.portScenePos('in')
                    if start_port and end_pos is not None:
                        start_pos = start_port.mapToScene(start_port.rect().center())
                        wire.points = [start_pos, end_pos]
                        wire.update_path()

    def boundingRect(self):
        return self._rect

    def paint(self, painter, option, widget=None):
        if painter is None:
            return
        radius = 16
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawRoundedRect(self._rect, radius, radius)
        if self.isSelected():
            sel_pen = QPen(QColor(0, 120, 215), 3, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.drawRoundedRect(self._rect, radius, radius)
