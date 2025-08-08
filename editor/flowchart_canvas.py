from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QGraphicsPathItem, QGraphicsLineItem
from PyQt6.QtGui import QPainter, QColor, QPen, QKeySequence
from PyQt6.QtCore import Qt, QPointF, QTimer, QLineF, QRectF, pyqtSignal
import json
import os

from editor.draggable_block import DraggableBlock
from editor.wire_segment import WireSegment
from editor.auto_routed_wire import AutoRoutedWire

class FlowchartCanvas(QGraphicsView):
    # Signal emitted when project is modified
    project_modified = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._wire_arrows = {}
        self._dragging_from_port = None
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)
        vp = self.viewport()
        if vp is not None:
            vp.setAcceptDrops(True)

        self.cell_size = 50
        self.cols, self.rows = 78, 130
        self.drawn_cols, self.drawn_rows = 78, 130
        self.pen = QPen(QColor(220, 220, 220))

        scene = QGraphicsScene(self)
        scene.setSceneRect(0, 0,
            (self.cols+1)*self.cell_size,
            (self.rows+1)*self.cell_size
        )
        self.setScene(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(Qt.GlobalColor.white)

        # Ensure scene is initialized before grid/expansion
        if self.scene() is not None:
            self._draw_grid()
        self._copy_buffer = []

        # Note: Block configuration is loaded dynamically in get_block_size()

        # Add always-present StartBlock at row 1, column A
        from editor.start_block import StartBlock
        scene = self.scene()
        if scene is not None:
            start_block = StartBlock()
            scene.addItem(start_block)
            cs = self.cell_size
            start_block.setPos(QPointF(cs, cs))

        # wiring state
        self._temp_wire: WireSegment | AutoRoutedWire | None = None
        self._wire_start_point: QPointF | None = None
        self._wire_points = []
        self._dragging_from: DraggableBlock | None = None
        self._dragging_from_port: str | None = None

    def load_block_config(self):
        """Load block configuration from JSON file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "templates", "block_config.json")
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback configuration if file not found
            return {
                "block_types": {
                    "Wire Router": {"width": 75, "height": 40},
                    "default": {"width": 150, "height": 40}
                }
            }

    def get_block_size(self, block_name):
        """Get the size for a specific block type"""
        # Load configuration dynamically to pick up JSON file changes
        block_config = self.load_block_config()
        block_types = block_config.get("block_types", {})
        if block_name in block_types:
            config = block_types[block_name]
            return config.get("width", 150), config.get("height", 40)
        return 150, 40  # Default size

    def dragEnterEvent(self, event):
        if event is not None and hasattr(event, 'mimeData'):
            mime = event.mimeData()
            if mime and hasattr(mime, 'hasText') and mime.hasText():
                event.acceptProposedAction()
            else:
                event.ignore()

    def dragMoveEvent(self, event):
        if event is not None and hasattr(event, 'mimeData'):
            mime = event.mimeData()
            if mime and hasattr(mime, 'hasText') and mime.hasText():
                event.acceptProposedAction()
            else:
                event.ignore()

    def dropEvent(self, event):
        if event is None:
            return super().dropEvent(event)
        mime = event.mimeData() if hasattr(event, 'mimeData') else None
        has_text = hasattr(mime, 'hasText') and mime.hasText() if mime else False
        if not has_text:
            return super().dropEvent(event)
        if self.scene() is None:
            return
        text = ''
        if mime and hasattr(mime, 'text') and callable(mime.text):
            text = mime.text()
        pt = self.mapToScene(event.position().toPoint()) if hasattr(event, 'position') and event.position() is not None else QPointF(0, 0)
        
        # Get size from configuration
        width, height = self.get_block_size(text)
        rect = QRectF(0, 0, width, height)
            
        blk = DraggableBlock(rect)
        # Set text by searching for QGraphicsTextItem child
        from PyQt6.QtWidgets import QGraphicsTextItem
        text_item = next((c for c in blk.childItems() if isinstance(c, QGraphicsTextItem)), None)
        if text_item:
            text_item.setPlainText(text)
        # Prevent overlap: check if new block would overlap any existing block
        new_rect = blk.mapRectToScene(blk.boundingRect())
        scene = self.scene()
        if scene is None:
            return
        for item in scene.items():
            if isinstance(item, DraggableBlock) and item != blk:
                if item.mapRectToScene(item.boundingRect()).intersects(new_rect):
                    # Find a non-overlapping position nearby
                    offset = QPointF(blk.boundingRect().width() + 10, 0)
                    pt += offset
                    blk.setPos(pt - QPointF(75, 20))
                    new_rect = blk.mapRectToScene(blk.boundingRect())
        scene.addItem(blk)
        blk.setPos(pt - QPointF(75, 20))
        
        # Emit project modified signal
        self.project_modified.emit()

        sr = scene.sceneRect() if scene is not None else QRectF(0,0,1000,1000)
        cs = self.cell_size
        w, h = blk.boundingRect().width(), blk.boundingRect().height()
        # Clamp to scene boundaries
        x = min(max(blk.x(), cs), sr.width() - w)
        y = min(max(blk.y(), cs), sr.height() - h)
        blk.setPos(QPointF(x, y))
        # Prevent overlap with other blocks
        for item in scene.items():
            if isinstance(item, DraggableBlock) and item != blk:
                if item.mapRectToScene(item.boundingRect()).intersects(blk.mapRectToScene(blk.boundingRect())):
                    # Hard stop: revert to previous position
                    blk.setPos(blk.pos())
                    break

        self._expand_scene()
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event is None:
            return
        
        # Right-click cancels wire creation
        if event.button() == Qt.MouseButton.RightButton:
            if self._temp_wire:
                scene = self.scene()
                if scene is not None:
                    scene.removeItem(self._temp_wire)
                self._temp_wire = None
                self._wire_points = []
                self._wire_start_point = None
                self._dragging_from = None
                self._dragging_from_port = None
            return
            
        scene_pt = self.mapToScene(event.pos())
        scene = self.scene()
        items = scene.items(scene_pt) if scene is not None else []
        
        for it in items:
            if isinstance(it, QGraphicsEllipseItem):
                blk = it.parentItem()
                if isinstance(blk, DraggableBlock):
                    # Find which port was clicked
                    clicked_port = None
                    for port_name, port in blk.ports.items():
                        if port == it:
                            clicked_port = port_name
                            break
                    
                    if clicked_port:
                        # Check if this port already has a wire connected and user wants to delete it
                        if (clicked_port == blk.output_port and blk.out_wires) or (clicked_port in blk.input_ports and blk.in_wires):
                            # Delete existing wire by clicking on connected port
                            if clicked_port == blk.output_port and blk.out_wires:
                                self._disconnect_wire(blk.out_wires[0])
                            elif clicked_port in blk.input_ports and blk.in_wires:
                                # Find the wire connected to this specific input port
                                for wire in blk.in_wires[:]:  # Copy list to avoid modification during iteration
                                    if hasattr(wire, 'to_port') and wire.to_port == clicked_port:
                                        self._disconnect_wire(wire)
                                        break
                            return
                        
                        # Check if this can be an output port (start wire from here)
                        if blk.assign_output_port(clicked_port):
                            # This is a new output port assignment, start wire creation
                            self._dragging_from = blk
                            self._dragging_from_port = clicked_port
                            p0 = it.mapToScene(it.rect().center())
                            if p0 is not None:
                                # Start with auto-routed wire for preview
                                self._wire_start_point = p0
                                self._temp_wire = AutoRoutedWire(p0, p0)
                                scene = self.scene()
                                if scene is not None:
                                    scene.addItem(self._temp_wire)
                            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event is None:
            return
        if self._temp_wire:
            p = self.mapToScene(event.pos())
            # Update auto-routed wire preview
            if isinstance(self._temp_wire, AutoRoutedWire) and self._wire_start_point is not None:
                self._temp_wire.update_endpoints(self._wire_start_point, p)
            elif isinstance(self._temp_wire, WireSegment):
                # Fallback for legacy wire segments
                preview_points = self._wire_points + [p]
                self._temp_wire.points = preview_points
                self._temp_wire.update_path()
        else:
            super().mouseMoveEvent(event)
            # Enforce boundaries and prevent overlap for all selected blocks
            scene = self.scene()
            if scene is not None:
                sr = scene.sceneRect()
                cs = self.cell_size
                blocks = [i for i in scene.selectedItems() if isinstance(i, DraggableBlock)]
                for blk in blocks:
                    w, h = blk.boundingRect().width(), blk.boundingRect().height()
                    x = min(max(blk.x(), cs), sr.width() - w)
                    y = min(max(blk.y(), cs), sr.height() - h)
                    blk.setPos(QPointF(x, y))
                    # Prevent overlap with other blocks
                    for item in scene.items():
                        if isinstance(item, DraggableBlock) and item != blk:
                            while item.mapRectToScene(item.boundingRect()).intersects(blk.mapRectToScene(blk.boundingRect())):
                                blk.setPos(blk.pos() + QPointF(w + 10, 0))
                                x = min(max(blk.x(), cs), sr.width() - w)
                                blk.setPos(QPointF(x, y))
                # Dynamically update wires for all blocks during move
                for item in scene.items():
                    if isinstance(item, DraggableBlock):
                        # Update input wires
                        for wire in getattr(item, 'in_wires', []):
                            if isinstance(wire, WireSegment) and hasattr(wire, 'to_port') and wire.to_port:
                                if wire.to_port in item.ports:
                                    p_in = item.ports[wire.to_port].mapToScene(item.ports[wire.to_port].rect().center())
                                    if p_in is not None and len(wire.points) > 0:
                                        wire.points[-1] = p_in
                                        wire.update_path()
                        # Update output wires
                        for wire in getattr(item, 'out_wires', []):
                            if isinstance(wire, WireSegment) and hasattr(wire, 'from_port') and wire.from_port:
                                if wire.from_port in item.ports:
                                    p_out = item.ports[wire.from_port].mapToScene(item.ports[wire.from_port].rect().center())
                                    if p_out is not None and len(wire.points) > 0:
                                        wire.points[0] = p_out
                                        wire.update_path()

    def mouseReleaseEvent(self, event):
        # Ensure _wire_arrows is always available
        if not hasattr(self, '_wire_arrows'):
            self._wire_arrows = {}
        if event is None:
            return
        if self._temp_wire and self._dragging_from:
            scene_pt = self.mapToScene(event.pos())
            scene = self.scene()
            placed = False
            if scene is not None:
                # Check items at the specific mouse position first
                items_at_pos = scene.items(scene_pt)
                port_found = False
                
                # First try: exact position match
                for item in items_at_pos:
                    if isinstance(item, QGraphicsEllipseItem):
                        dst = item.parentItem()
                        if isinstance(dst, DraggableBlock) and dst != self._dragging_from:
                            # Find which port this is
                            clicked_port = None
                            for port_name, port in dst.ports.items():
                                if port == item:
                                    clicked_port = port_name
                                    break
                            
                            if clicked_port:
                                # Check if this can be an input port (complete wire here)
                                if dst.assign_input_port(clicked_port):
                                    p1 = item.mapToScene(item.rect().center())
                                    if self._temp_wire:
                                        # Handle auto-routed wire completion
                                        if isinstance(self._temp_wire, AutoRoutedWire) and self._wire_start_point is not None:
                                            self._temp_wire.update_endpoints(self._wire_start_point, p1)
                                        elif isinstance(self._temp_wire, WireSegment) and len(self._wire_points) > 0:
                                            # Legacy segment wire completion
                                            self._wire_points.append(p1)
                                            self._temp_wire.points = self._wire_points
                                            self._temp_wire.update_path()
                                        
                                        # Set up wire relationships
                                        self._temp_wire.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
                                        self._temp_wire.from_block = self._dragging_from
                                        self._temp_wire.from_port = self._dragging_from_port
                                        self._temp_wire.to_block = dst
                                        self._temp_wire.to_port = clicked_port
                                        
                                        # Add to wire lists
                                        if self._dragging_from:
                                            self._dragging_from.out_wires.append(self._temp_wire)
                                        dst.in_wires.append(self._temp_wire)
                                        
                                        # Update port colors
                                        if self._dragging_from:
                                            self._dragging_from.update_port_colors()
                                        dst.update_port_colors()
                                        
                                        # Emit project modified signal
                                        self.project_modified.emit()
                                        
                                        placed = True
                                        port_found = True
                                        # Wire is complete, clear temp state
                                        self._temp_wire = None
                                        self._wire_points = []
                                        self._wire_start_point = None
                                        self._dragging_from = None
                                        self._dragging_from_port = None
                                        break
                
                # Second try: nearby ports if no exact match (for segmented wires)
                if not port_found:
                    tolerance = 25  # Increased tolerance for segmented wires
                    for item in scene.items():
                        if isinstance(item, QGraphicsEllipseItem):
                            dst = item.parentItem()
                            if isinstance(dst, DraggableBlock) and dst != self._dragging_from:
                                # Check if mouse is near this port
                                port_center = item.mapToScene(item.rect().center())
                                mouse_distance = (scene_pt - port_center).manhattanLength()
                                
                                if mouse_distance <= tolerance:
                                    # Find which port this is
                                    clicked_port = None
                                    for port_name, port in dst.ports.items():
                                        if port == item:
                                            clicked_port = port_name
                                            break
                                    
                                    if clicked_port:
                                        # Check if this can be an input port (complete wire here)
                                        if dst.assign_input_port(clicked_port):
                                            p1 = port_center
                                            if self._temp_wire:
                                                # Handle auto-routed wire completion
                                                if isinstance(self._temp_wire, AutoRoutedWire) and self._wire_start_point is not None:
                                                    self._temp_wire.update_endpoints(self._wire_start_point, p1)
                                                elif isinstance(self._temp_wire, WireSegment) and len(self._wire_points) > 0:
                                                    # Legacy segment wire completion
                                                    self._wire_points.append(p1)
                                                    self._temp_wire.points = self._wire_points
                                                    self._temp_wire.update_path()
                                                
                                                # Set up wire relationships
                                                self._temp_wire.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
                                                self._temp_wire.from_block = self._dragging_from
                                                self._temp_wire.from_port = self._dragging_from_port
                                                self._temp_wire.to_block = dst
                                                self._temp_wire.to_port = clicked_port
                                                
                                                # Add to wire lists
                                                if self._dragging_from:
                                                    self._dragging_from.out_wires.append(self._temp_wire)
                                                dst.in_wires.append(self._temp_wire)
                                                
                                                # Update port colors
                                                if self._dragging_from:
                                                    self._dragging_from.update_port_colors()
                                                dst.update_port_colors()
                                                
                                                placed = True
                                                # Wire is complete, clear temp state
                                                self._temp_wire = None
                                                self._wire_points = []
                                                self._wire_start_point = None
                                                self._dragging_from = None
                                                self._dragging_from_port = None
                                                break
            # Don't remove wire if not placed - keep it active for more bend points
            # User can right-click or press Escape to cancel
        else:
            super().mouseReleaseEvent(event)
    def mouseDoubleClickEvent(self, event):
        # Auto-routed wires don't need manual bend points
        # Double-click is disabled for wire creation
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if event is None:
            return
        if event.key() == Qt.Key.Key_Escape:
            # Cancel wire creation on Escape
            if self._temp_wire:
                scene = self.scene()
                if scene is not None:
                    scene.removeItem(self._temp_wire)
                self._temp_wire = None
                self._wire_points = []
                self._wire_start_point = None
                self._dragging_from = None
                self._dragging_from_port = None
            return
        if event.key() == Qt.Key.Key_Delete:
            scene = self.scene()
            if scene is not None:
                from editor.start_block import StartBlock
                for itm in list(scene.selectedItems()):
                    if isinstance(itm, QGraphicsPathItem):
                        self._disconnect_wire(itm)
                    elif isinstance(itm, StartBlock):
                        continue  # Prevent StartBlock deletion
                    else:
                        scene.removeItem(itm)
            self._expand_scene()
            return
        if event.matches(QKeySequence.StandardKey.Copy):
            scene = self.scene()
            from editor.start_block import StartBlock
            sel = [i for i in scene.selectedItems() if isinstance(i, DraggableBlock) and not isinstance(i, StartBlock)] if scene is not None else []
            self._copy_buffer = []
            self._wire_buffer = []
            
            # Store selected blocks with their text and positions
            for blk in sel:
                text = blk.text_item.toPlainText()
                pos = blk.pos()
                self._copy_buffer.append((text, pos))
                
            # Store wire connections between selected blocks
            for i, src_blk in enumerate(sel):
                for wire in getattr(src_blk, 'out_wires', []):
                    if hasattr(wire, 'to_block'):
                        for j, dst_blk in enumerate(sel):
                            if wire.to_block == dst_blk:
                                self._wire_buffer.append((i, j, wire.from_port, wire.to_port))
                                break
            return

        if event.matches(QKeySequence.StandardKey.Paste):
            if not hasattr(self, '_copy_buffer') or not self._copy_buffer:
                return
                
            new_blocks = []
            scene = self.scene()
            
            # Create new blocks
            for text, pos in self._copy_buffer:
                # Get size from configuration
                width, height = self.get_block_size(text)
                blk = DraggableBlock(QRectF(0,0,width,height), text)
                if scene is not None:
                    scene.addItem(blk)
                # Offset paste position
                blk.setPos(pos + QPointF(50, 50))
                new_blocks.append(blk)
            
            # Recreate wire connections
            for src_i, dst_i, from_port, to_port in getattr(self, '_wire_buffer', []):
                if src_i < len(new_blocks) and dst_i < len(new_blocks):
                    src_blk = new_blocks[src_i]
                    dst_blk = new_blocks[dst_i]
                    
                    # Set up port assignments
                    src_blk.assign_output_port(from_port)
                    dst_blk.assign_input_port(to_port)
                    
                    # Create wire
                    p_out = src_blk.ports[from_port].mapToScene(src_blk.ports[from_port].rect().center())
                    p_in = dst_blk.ports[to_port].mapToScene(dst_blk.ports[to_port].rect().center())
                    
                    if p_out and p_in:
                        # Use auto-routed wire for better routing
                        wire = AutoRoutedWire(p_out, p_in)
                        wire.from_block = src_blk
                        wire.from_port = from_port
                        wire.to_block = dst_blk
                        wire.to_port = to_port
                        
                        # Add to wire lists
                        src_blk.out_wires.append(wire)
                        dst_blk.in_wires.append(wire)
                        
                        if scene is not None:
                            scene.addItem(wire)
            
            # Update port colors for all new blocks
            for blk in new_blocks:
                blk.update_port_colors()
            return
    def _disconnect_wire(self, wire):
        scene = self.scene()
        if scene is None:
            return
        # Remove wire and any arrowheads from block wire lists and scene
        if wire is not None:
            # Remove arrowhead and mid_arrow if present
            if hasattr(self, '_wire_arrows') and wire in self._wire_arrows:
                arrowhead, mid_arrow = self._wire_arrows[wire]
                if scene is not None:
                    if arrowhead is not None:
                        scene.removeItem(arrowhead)
                    if mid_arrow is not None:
                        scene.removeItem(mid_arrow)
                self._wire_arrows.pop(wire)
            scene.removeItem(wire)
            
            # Remove wire from blocks and reset ports if no wires remain
            for blk in scene.items() if scene is not None else []:
                if isinstance(blk, DraggableBlock):
                    wire_removed = False
                    
                    # Handle input wire removal
                    if wire in getattr(blk, 'in_wires', []):
                        blk.in_wires.remove(wire)
                        wire_removed = True
                        # Remove the specific input port that was disconnected
                        if hasattr(wire, 'to_port') and wire.to_port in blk.input_ports:
                            blk.remove_input_port(wire.to_port)
                    
                    # Handle output wire removal
                    if wire in getattr(blk, 'out_wires', []):
                        blk.out_wires.remove(wire)
                        wire_removed = True
                    
                    # Reset port configuration if all wires are removed
                    if wire_removed and not blk.in_wires and not blk.out_wires:
                        blk.reset_ports()
                    else:
                        # Just update colors for partial disconnections
                        blk.update_port_colors()
            
            # Emit project modified signal when wire is removed
            self.project_modified.emit()
    def _draw_grid(self):
        scene = self.scene()
        if scene is None:
            return
        for x in range(1, self.drawn_cols+1):
            lbl = ""
            col = x
            while col:
                col, r = divmod(col-1, 26)
                lbl = chr(65+r) + lbl
            t = scene.addText(lbl)
            if t:
                t.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
                t.setPos(x*self.cell_size, 0)
                t.setZValue(-1)
            ln = scene.addLine(
                x*self.cell_size, 0,
                x*self.cell_size, (self.drawn_rows+1)*self.cell_size,
                self.pen
            )
            if ln:
                ln.setZValue(-1)

        for y in range(1, self.drawn_rows+1):
            t = scene.addText(str(y))
            if t:
                t.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
                t.setPos(0, y*self.cell_size)
                t.setZValue(-1)
            ln = scene.addLine(
                0, y*self.cell_size,
                (self.drawn_cols+1)*self.cell_size, y*self.cell_size,
                self.pen
            )
            if ln:
                ln.setZValue(-1)

    def _expand_scene(self):
        scene = self.scene()
        if scene is None:
            return
        blocks = [i for i in scene.items() if isinstance(i, DraggableBlock)]
        max_x = max((b.pos().x()+b.boundingRect().width()) for b in blocks) if blocks else 0
        max_y = max((b.pos().y()+b.boundingRect().height()) for b in blocks) if blocks else 0
        req_c = max(self.cols, int(max_x//self.cell_size)+1)
        req_r = max(self.rows, int(max_y//self.cell_size)+1)
        tgt_c = req_c + 10
        tgt_r = req_r + 50
        old_c, old_r = self.drawn_cols, self.drawn_rows

        if tgt_c > old_c:
            old_w = (old_c+1)*self.cell_size
            new_w = (tgt_c+1)*self.cell_size
            for x in range(old_c+1, tgt_c+1):
                lbl = ""; col = x
                while col:
                    col, r = divmod(col-1, 26)
                    lbl = chr(65+r) + lbl
                t = scene.addText(lbl)
                if t:
                    t.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
                    t.setPos(x*self.cell_size, 0)
                    t.setZValue(-1)
                ln = scene.addLine(
                    x*self.cell_size, 0,
                    x*self.cell_size, (tgt_r+1)*self.cell_size,
                    self.pen
                )
                if ln:
                    ln.setZValue(-1)
            for y in range(1, old_r+1):
                ln = scene.addLine(
                    old_w, y*self.cell_size,
                    new_w, y*self.cell_size,
                    self.pen
                )
                if ln:
                    ln.setZValue(-1)
            self.drawn_cols = tgt_c

        if tgt_r > old_r:
            old_h = (old_r+1)*self.cell_size
            new_h = (tgt_r+1)*self.cell_size
            for y in range(old_r+1, tgt_r+1):
                t = scene.addText(str(y))
                if t:
                    t.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
                    t.setPos(0, y*self.cell_size)
                    t.setZValue(-1)
                ln = scene.addLine(
                    0, y*self.cell_size,
                    (self.drawn_cols+1)*self.cell_size, y*self.cell_size,
                    self.pen
                )
                if ln:
                    ln.setZValue(-1)
            for x in range(1, self.drawn_cols+1):
                ln = scene.addLine(
                    x*self.cell_size, old_h,
                    x*self.cell_size, new_h,
                    self.pen
                )
                if ln:
                    ln.setZValue(-1)
            self.drawn_rows = tgt_r

        w = (self.drawn_cols+1)*self.cell_size
        h = (self.drawn_rows+1)*self.cell_size
        scene.setSceneRect(0, 0, w, h)

    # Project Management Methods
    def clear_canvas(self):
        """Clear all blocks and wires from the canvas"""
        scene = self.scene()
        if scene is not None:
            # Remove all items except grid elements
            for item in scene.items():
                if isinstance(item, (DraggableBlock, WireSegment, AutoRoutedWire)):
                    scene.removeItem(item)
            
            # Clear wire tracking
            self._wire_arrows.clear()
            self._temp_wire = None
            self._dragging_from = None
            self._dragging_from_port = None
            
            # Re-add the start block
            from editor.start_block import StartBlock
            start_block = StartBlock()
            scene.addItem(start_block)
            start_block.setPos(self.cell_size, self.cell_size)  # Position at A1

    def get_project_data(self):
        """Export current canvas state to a dictionary"""
        scene = self.scene()
        if scene is None:
            return {"blocks": [], "wires": [], "version": "1.0"}
        
        blocks_data = []
        wires_data = []
        
        # Export blocks
        for item in scene.items():
            if isinstance(item, DraggableBlock):
                block_data = {
                    "id": id(item),  # Use object id as unique identifier
                    "type": item.__class__.__name__,
                    "text": item.text_item.toPlainText() if item.text_item else "",
                    "position": [item.pos().x(), item.pos().y()],
                    "input_ports": list(item.input_ports),
                    "output_port": item.output_port,
                    "size": [item._rect.width(), item._rect.height()]
                }
                blocks_data.append(block_data)
        
        # Export wires  
        for item in scene.items():
            if isinstance(item, (WireSegment, AutoRoutedWire)):
                if hasattr(item, 'from_block') and hasattr(item, 'to_block'):
                    wire_data = {
                        "type": item.__class__.__name__,
                        "from_block": id(item.from_block),
                        "from_port": item.from_port,
                        "to_block": id(item.to_block),
                        "to_port": item.to_port
                    }
                    # Add specific data for different wire types
                    if isinstance(item, WireSegment) and hasattr(item, 'points'):
                        wire_data["points"] = [[p.x(), p.y()] for p in item.points]
                    elif isinstance(item, AutoRoutedWire):
                        wire_data["start_point"] = [item.start_point.x(), item.start_point.y()]
                        wire_data["end_point"] = [item.end_point.x(), item.end_point.y()]
                    
                    wires_data.append(wire_data)
        
        return {
            "version": "1.0",
            "blocks": blocks_data,
            "wires": wires_data,
            "canvas_size": [self.cols, self.rows]
        }

    def load_project(self, project_data):
        """Load project data into the canvas"""
        scene = self.scene()
        if scene is None:
            return
        
        # Clear existing content
        self.clear_canvas()
        
        # Validate project data
        if not isinstance(project_data, dict) or "blocks" not in project_data:
            raise ValueError("Invalid project file format")
        
        # Track loaded blocks by their original IDs for wire connections
        block_id_map = {}
        
        # Load blocks
        for block_data in project_data.get("blocks", []):
            try:
                block_type = block_data.get("type", "DraggableBlock")
                
                # Create block based on type
                if block_type == "StartBlock":
                    from editor.start_block import StartBlock
                    block = StartBlock()
                else:
                    # Create regular draggable block with proper size from config
                    text = block_data.get("text", "")
                    if text:
                        # Get the proper size from JSON config for this block type
                        width, height = self.get_block_size(text)
                        rect = QRectF(0, 0, width, height)
                        block = DraggableBlock(rect, text)
                    else:
                        # Fallback for blocks without text
                        block = DraggableBlock()
                        if "text" in block_data:
                            block.setText(block_data["text"])
                
                # Set position
                if "position" in block_data:
                    pos = block_data["position"]
                    block.setPos(pos[0], pos[1])
                
                # Restore block size (fallback if different from config)
                if "size" in block_data:
                    size = block_data["size"]
                    current_size = [block._rect.width(), block._rect.height()]
                    if current_size != size:
                        # Only update if different from current size
                        block._rect.setWidth(size[0])
                        block._rect.setHeight(size[1])
                        # Update port positions after size change
                        if hasattr(block, 'update_port_positions'):
                            block.update_port_positions()
                        # Update the text centering after size change
                        if hasattr(block, '_center_text'):
                            block._center_text()
                
                # Restore port assignments
                if "input_ports" in block_data:
                    block.input_ports = set(block_data["input_ports"])
                if "output_port" in block_data:
                    block.output_port = block_data["output_port"]
                
                # Add to scene and track ID mapping
                scene.addItem(block)
                block_id_map[block_data.get("id")] = block
                
            except Exception as e:
                print(f"Error loading block: {e}")
                continue
        
        # Load wires
        for wire_data in project_data.get("wires", []):
            try:
                from_block = block_id_map.get(wire_data.get("from_block"))
                to_block = block_id_map.get(wire_data.get("to_block"))
                
                if from_block and to_block:
                    # Create wire based on type
                    wire_type = wire_data.get("type", "AutoRoutedWire")
                    
                    if wire_type == "AutoRoutedWire":
                        # Create with default points, then update
                        start = QPointF(0, 0)
                        end = QPointF(0, 0)
                        if "start_point" in wire_data and "end_point" in wire_data:
                            start = QPointF(wire_data["start_point"][0], wire_data["start_point"][1])
                            end = QPointF(wire_data["end_point"][0], wire_data["end_point"][1])
                        wire = AutoRoutedWire(start, end)
                    else:
                        # Create with default points, then update
                        points = [QPointF(0, 0), QPointF(100, 100)]
                        if "points" in wire_data:
                            points = [QPointF(p[0], p[1]) for p in wire_data["points"]]
                        wire = WireSegment(points)
                    
                    # Set wire relationships
                    wire.from_block = from_block
                    wire.from_port = wire_data.get("from_port")
                    wire.to_block = to_block
                    wire.to_port = wire_data.get("to_port")
                    
                    # Add wire to blocks' wire lists
                    if not hasattr(from_block, 'out_wires'):
                        from_block.out_wires = []
                    if not hasattr(to_block, 'in_wires'):
                        to_block.in_wires = []
                    
                    from_block.out_wires.append(wire)
                    to_block.in_wires.append(wire)
                    
                    # Update port assignments
                    from_block.assign_output_port(wire.from_port)
                    to_block.assign_input_port(wire.to_port)
                    
                    scene.addItem(wire)
                    
            except Exception as e:
                print(f"Error loading wire: {e}")
                continue
        
        # Update all block colors after loading
        for block in block_id_map.values():
            if hasattr(block, 'update_port_colors'):
                block.update_port_colors()
        
        print(f"Project loaded: {len(block_id_map)} blocks, {len(project_data.get('wires', []))} wires")
