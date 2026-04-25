import sys
import uuid
import json
from enum import Enum
from typing import List, Optional, Any, Dict
from abc import ABC, abstractmethod
from typing import Set, Tuple
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QColorDialog, QApplication,
    QLabel, QSpinBox, QGroupBox, QFormLayout, QMessageBox, QMenuBar, QFileDialog, QMenu,
    QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF, QKeyEvent, QMouseEvent, QPaintEvent, QAction

# Дерево обьектов
class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Any = None) -> None:
        pass


class Observable(QObject):
    def __init__(self):
        super().__init__()
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, event_type: str, data: Any = None) -> None:
        for observer in self._observers:
            observer.update(event_type, data)


class Direction(Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    BOTH = "both"


class ShapeType(Enum):
    CIRCLE = "Круг"
    SQUARE = "Квадрат"
    ELLIPSE = "Эллипс"
    RECTANGLE = "Прямоугольник"
    TRIANGLE = "Треугольник"
    LINE = "Линия"


class Shape:
    def __init__(self, shape_type: ShapeType, pos: QPointF, color: QColor = Qt.GlobalColor.gray):
        self.id = str(uuid.uuid4())
        self.type = shape_type
        self.position = QPointF(pos)
        self.color = QColor(color)
        self._selected = False
        self._size = QSizeF(100, 100)

    def is_selected(self) -> bool:
        return self._selected

    def set_selected(self, selected: bool) -> None:
        self._selected = selected

    def get_bounding_rect(self) -> QRectF:
        raise NotImplementedError

    def contains_point(self, point: QPointF) -> bool:
        raise NotImplementedError

    def move(self, delta: QPointF, bounds: QRectF) -> bool:
        new_rect = self.get_bounding_rect().translated(delta)
        if bounds.contains(new_rect):
            self.position += delta
            return True
        return False

    def resize(self, delta_width: float, delta_height: float, bounds: QRectF) -> bool:
        new_width = max(10, self._size.width() + delta_width)
        new_height = max(10, self._size.height() + delta_height)
        old_width, old_height = self._size.width(), self._size.height()
        self._size = QSizeF(new_width, new_height)
        if bounds.contains(self.get_bounding_rect()):
            return True
        else:
            self._size = QSizeF(old_width, old_height)
            return False

    def set_color(self, color: QColor) -> None:
        self.color = QColor(color)

    def draw(self, painter: QPainter) -> None:
        painter.setBrush(QBrush(self.color))
        if self._selected:
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
        else:
            painter.setPen(QPen(Qt.GlobalColor.black, 1))

    def draw_selection_rect(self, painter: QPainter) -> None:
        pass

    def copy(self):
        raise NotImplementedError

    def to_dict(self) -> Dict:
        return {
            'class': self.__class__.__name__,
            'id': str(self.id),
            'type': self.type.value,
            'position_x': self.position.x(),
            'position_y': self.position.y(),
            'color_r': self.color.red(),
            'color_g': self.color.green(),
            'color_b': self.color.blue(),
            'color_a': self.color.alpha(),
            'size_w': self._size.width(),
            'size_h': self._size.height(),
        }

    def from_dict(self, data: Dict) -> None:
        id_str = data.get('id', str(uuid.uuid4()))
        self.id = id_str if isinstance(id_str, str) else str(id_str)
        self.position = QPointF(data['position_x'], data['position_y'])
        self.color = QColor(data['color_r'], data['color_g'], data['color_b'], data['color_a'])
        self._size = QSizeF(data['size_w'], data['size_h'])


class Circle(Shape):
    def __init__(self, pos: QPointF, color: QColor = Qt.GlobalColor.gray):
        super().__init__(ShapeType.CIRCLE, pos, color)
        self._size = QSizeF(60, 60)

    def get_bounding_rect(self) -> QRectF:
        return QRectF(self.position.x() - self._size.width() / 2,
                      self.position.y() - self._size.height() / 2,
                      self._size.width(), self._size.height())

    def contains_point(self, point: QPointF) -> bool:
        center = self.position
        radius = self._size.width() / 2
        return (point.x() - center.x()) ** 2 + (point.y() - center.y()) ** 2 <= radius ** 2

    def draw(self, painter: QPainter) -> None:
        super().draw(painter)
        painter.drawEllipse(self.get_bounding_rect())

    def resize(self, delta_width: float, delta_height: float, bounds: QRectF) -> bool:
        delta = delta_width if abs(delta_width) > abs(delta_height) else delta_height
        new_size = max(10, self._size.width() + delta)
        old_size = self._size.width()
        self._size = QSizeF(new_size, new_size)
        if bounds.contains(self.get_bounding_rect()):
            return True
        else:
            self._size = QSizeF(old_size, old_size)
            return False

    def copy(self):
        new_shape = Circle(self.position + QPointF(20, 20), QColor(self.color))
        new_shape._size = QSizeF(self._size)
        new_shape.id = str(uuid.uuid4())
        new_shape.set_selected(False)
        return new_shape


class Square(Shape):
    def __init__(self, pos: QPointF, color: QColor = Qt.GlobalColor.gray):
        super().__init__(ShapeType.SQUARE, pos, color)
        self._size = QSizeF(80, 80)

    def get_bounding_rect(self) -> QRectF:
        return QRectF(self.position.x() - self._size.width() / 2,
                      self.position.y() - self._size.height() / 2,
                      self._size.width(), self._size.height())

    def contains_point(self, point: QPointF) -> bool:
        return self.get_bounding_rect().contains(point)

    def draw(self, painter: QPainter) -> None:
        super().draw(painter)
        painter.drawRect(self.get_bounding_rect())

    def resize(self, delta_width: float, delta_height: float, bounds: QRectF) -> bool:
        delta = delta_width if abs(delta_width) > abs(delta_height) else delta_height
        new_size = max(10, self._size.width() + delta)
        old_size = self._size.width()
        self._size = QSizeF(new_size, new_size)
        if bounds.contains(self.get_bounding_rect()):
            return True
        else:
            self._size = QSizeF(old_size, old_size)
            return False

    def copy(self):
        new_shape = Square(self.position + QPointF(20, 20), QColor(self.color))
        new_shape._size = QSizeF(self._size)
        new_shape.id = str(uuid.uuid4())
        new_shape.set_selected(False)
        return new_shape


class Ellipse(Shape):
    def __init__(self, pos: QPointF, color: QColor = Qt.GlobalColor.gray):
        super().__init__(ShapeType.ELLIPSE, pos, color)
        self._size = QSizeF(100, 60)

    def get_bounding_rect(self) -> QRectF:
        return QRectF(self.position.x() - self._size.width() / 2,
                      self.position.y() - self._size.height() / 2,
                      self._size.width(), self._size.height())

    def contains_point(self, point: QPointF) -> bool:
        return self.get_bounding_rect().contains(point)

    def draw(self, painter: QPainter) -> None:
        super().draw(painter)
        painter.drawEllipse(self.get_bounding_rect())

    def copy(self):
        new_shape = Ellipse(self.position + QPointF(20, 20), QColor(self.color))
        new_shape._size = QSizeF(self._size)
        new_shape.id = str(uuid.uuid4())
        new_shape.set_selected(False)
        return new_shape


class Rectangle(Shape):
    def __init__(self, pos: QPointF, color: QColor = Qt.GlobalColor.gray):
        super().__init__(ShapeType.RECTANGLE, pos, color)
        self._size = QSizeF(120, 80)

    def get_bounding_rect(self) -> QRectF:
        return QRectF(self.position.x() - self._size.width() / 2,
                      self.position.y() - self._size.height() / 2,
                      self._size.width(), self._size.height())

    def contains_point(self, point: QPointF) -> bool:
        return self.get_bounding_rect().contains(point)

    def draw(self, painter: QPainter) -> None:
        super().draw(painter)
        painter.drawRect(self.get_bounding_rect())

    def copy(self):
        new_shape = Rectangle(self.position + QPointF(20, 20), QColor(self.color))
        new_shape._size = QSizeF(self._size)
        new_shape.id = str(uuid.uuid4())
        new_shape.set_selected(False)
        return new_shape


class Triangle(Shape):
    def __init__(self, pos: QPointF, color: QColor = Qt.GlobalColor.gray):
        super().__init__(ShapeType.TRIANGLE, pos, color)
        self._size = QSizeF(80, 80)

    def get_bounding_rect(self) -> QRectF:
        return QRectF(self.position.x() - self._size.width() / 2,
                      self.position.y() - self._size.height() / 2,
                      self._size.width(), self._size.height())

    def get_polygon(self) -> QPolygonF:
        w, h = self._size.width(), self._size.height()
        return QPolygonF([
            QPointF(self.position.x(), self.position.y() - h / 2),
            QPointF(self.position.x() - w / 2, self.position.y() + h / 2),
            QPointF(self.position.x() + w / 2, self.position.y() + h / 2)
        ])

    def contains_point(self, point: QPointF) -> bool:
        return self.get_polygon().containsPoint(point, Qt.FillRule.OddEvenFill)

    def draw(self, painter: QPainter) -> None:
        super().draw(painter)
        painter.drawPolygon(self.get_polygon())

    def copy(self):
        new_shape = Triangle(self.position + QPointF(20, 20), QColor(self.color))
        new_shape._size = QSizeF(self._size)
        new_shape.id = str(uuid.uuid4())
        new_shape.set_selected(False)
        return new_shape


class Line(Shape):
    def __init__(self, pos: QPointF, color: QColor = Qt.GlobalColor.gray):
        super().__init__(ShapeType.LINE, pos, color)
        self._size = QSizeF(100, 2)

    def get_bounding_rect(self) -> QRectF:
        half_length = self._size.width() / 2
        return QRectF(
            self.position.x() - half_length,
            self.position.y() - 2,
            self._size.width(),
            4
        )

    def get_end_point(self) -> QPointF:
        half_length = self._size.width() / 2
        return QPointF(self.position.x() + half_length, self.position.y())

    def get_start_point(self) -> QPointF:
        half_length = self._size.width() / 2
        return QPointF(self.position.x() - half_length, self.position.y())

    def contains_point(self, point: QPointF) -> bool:
        import math
        start = self.get_start_point()
        end = self.get_end_point()
        x1, y1 = start.x(), start.y()
        x2, y2 = end.x(), end.y()
        px, py = point.x(), point.y()

        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            dist = math.hypot(px - x1, py - y1)
        else:
            t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
            t = max(0.0, min(1.0, t))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            dist = math.hypot(px - proj_x, py - proj_y)
        return dist <= 8

    def move(self, delta: QPointF, bounds: QRectF) -> bool:
        new_pos = self.position + delta
        temp_line = Line(new_pos, self.color)
        temp_line._size = QSizeF(self._size)
        if bounds.contains(temp_line.get_bounding_rect()):
            self.position = new_pos
            return True
        return False

    def resize(self, delta_width: float, delta_height: float, bounds: QRectF) -> bool:
        new_width = max(10, self._size.width() + delta_width)
        old_width = self._size.width()
        self._size.setWidth(new_width)
        if bounds.contains(self.get_bounding_rect()):
            return True
        else:
            self._size.setWidth(old_width)
            return False

    def draw(self, painter: QPainter) -> None:
        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self._selected:
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
        else:
            painter.setPen(QPen(self.color, 2))
        painter.drawLine(self.get_start_point(), self.get_end_point())

    def copy(self):
        new_shape = Line(self.position + QPointF(20, 20), QColor(self.color))
        new_shape._size = QSizeF(self._size)
        new_shape.id = str(uuid.uuid4())
        new_shape.set_selected(False)
        return new_shape


class Arrow(Shape):
    def __init__(self, source: 'Shape', target: 'Shape', direction: Direction = Direction.FORWARD):
        super().__init__(ShapeType.LINE, QPointF(0, 0), QColor(0, 0, 0))
        self.source = source
        self.target = target
        self.direction = direction
        self.start_point = QPointF(0, 0)
        self.end_point = QPointF(0, 0)
        self._update_arrow_position()

    def _update_arrow_position(self) -> None:
        if not self.source or not self.target:
            return
        source_center = self._get_shape_center(self.source)
        target_center = self._get_shape_center(self.target)
        source_point = self._get_edge_point(self.source, target_center)
        target_point = self._get_edge_point(self.target, source_center)
        self.start_point = source_point
        self.end_point = target_point
        min_x = min(source_point.x(), target_point.x())
        min_y = min(source_point.y(), target_point.y())
        max_x = max(source_point.x(), target_point.x())
        max_y = max(source_point.y(), target_point.y())
        self.position = QPointF((min_x + max_x) / 2, (min_y + max_y) / 2)
        self._size = QSizeF(max_x - min_x + 10, max_y - min_y + 10)

    def _get_shape_center(self, shape: Shape) -> QPointF:
        if isinstance(shape, Group):
            return shape.position
        return shape.position

    def _get_edge_point(self, shape: Shape, towards: QPointF) -> QPointF:
        center = self._get_shape_center(shape)
        direction = towards - center
        if direction.x() == 0 and direction.y() == 0:
            return center
        length = (direction.x() ** 2 + direction.y() ** 2) ** 0.5
        if length == 0:
            return center
        unit = QPointF(direction.x() / length, direction.y() / length)
        if isinstance(shape, Group):
            rect = shape.get_bounding_rect()
            return self._ray_rect_intersection(center, unit, rect)
        elif isinstance(shape, Circle):
            radius = shape._size.width() / 2
            return QPointF(center.x() + unit.x() * radius, center.y() + unit.y() * radius)
        elif isinstance(shape, (Square, Rectangle)):
            rect = shape.get_bounding_rect()
            return self._ray_rect_intersection(center, unit, rect)
        elif isinstance(shape, Triangle):
            poly = shape.get_polygon()
            return self._ray_polygon_intersection(center, unit, poly)
        elif isinstance(shape, Line):
            return shape.get_end_point() if direction.x() > 0 else shape.get_start_point()
        else:
            rect = shape.get_bounding_rect()
            return self._ray_rect_intersection(center, unit, rect)

    def _ray_rect_intersection(self, origin: QPointF, direction: QPointF, rect: QRectF) -> QPointF:
        t_min = -float('inf')
        t_max = float('inf')
        if direction.x() != 0:
            t1 = (rect.left() - origin.x()) / direction.x()
            t2 = (rect.right() - origin.x()) / direction.x()
            if t1 > t2:
                t1, t2 = t2, t1
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
        elif origin.x() < rect.left() or origin.x() > rect.right():
            return origin
        if direction.y() != 0:
            t1 = (rect.top() - origin.y()) / direction.y()
            t2 = (rect.bottom() - origin.y()) / direction.y()
            if t1 > t2:
                t1, t2 = t2, t1
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
        elif origin.y() < rect.top() or origin.y() > rect.bottom():
            return origin
        if t_min > t_max:
            return origin
        t = max(0, t_min)
        return QPointF(origin.x() + direction.x() * t, origin.y() + direction.y() * t)

    def _ray_polygon_intersection(self, origin: QPointF, direction: QPointF, polygon: QPolygonF) -> QPointF:
        best_t = float('inf')
        best_point = origin
        for i in range(polygon.size()):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % polygon.size()]
            intersection = self._ray_segment_intersection(origin, direction, p1, p2)
            if intersection:
                t = (intersection.x() - origin.x()) / direction.x() if direction.x() != 0 else \
                    (intersection.y() - origin.y()) / direction.y()
                if 0 < t < best_t:
                    best_t = t
                    best_point = intersection
        return best_point if best_t != float('inf') else origin

    def _ray_segment_intersection(self, origin: QPointF, direction: QPointF,
                                  p1: QPointF, p2: QPointF) -> Optional[QPointF]:
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        x3, y3 = origin.x(), origin.y()
        x4, y4 = origin.x() + direction.x(), origin.y() + direction.y()
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        if 0 <= t <= 1 and u >= 0:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return QPointF(x, y)
        return None

    def update_connection(self) -> None:
        self._update_arrow_position()

    def get_bounding_rect(self) -> QRectF:
        if not hasattr(self, 'start_point') or not hasattr(self, 'end_point'):
            return QRectF(0, 0, 0, 0)
        min_x = min(self.start_point.x(), self.end_point.x())
        min_y = min(self.start_point.y(), self.end_point.y())
        max_x = max(self.start_point.x(), self.end_point.x())
        max_y = max(self.start_point.y(), self.end_point.y())
        return QRectF(min_x - 5, min_y - 5, max_x - min_x + 10, max_y - min_y + 10)

    def contains_point(self, point: QPointF) -> bool:
        if not hasattr(self, 'start_point') or not hasattr(self, 'end_point'):
            return False
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        px, py = point.x(), point.y()
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            dist = ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        else:
            t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
            t = max(0.0, min(1.0, t))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            dist = ((px - proj_x) ** 2 + (py - proj_y) ** 2) ** 0.5
        return dist <= 8

    def move(self, delta: QPointF, bounds: QRectF) -> bool:
        return True

    def resize(self, delta_width: float, delta_height: float, bounds: QRectF) -> bool:
        return True

    def draw(self, painter: QPainter) -> None:
        if not hasattr(self, 'start_point') or not hasattr(self, 'end_point'):
            return
        if self._selected:
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
        else:
            painter.setPen(QPen(self.color, 2))
        painter.drawLine(self.start_point, self.end_point)
        self._draw_arrowhead(painter, self.start_point, self.end_point)
        if self.direction == Direction.BOTH:
            self._draw_arrowhead(painter, self.end_point, self.start_point)
        elif self.direction == Direction.BACKWARD:
            self._draw_arrowhead(painter, self.end_point, self.start_point)

    def _draw_arrowhead(self, painter: QPainter, from_point: QPointF, to_point: QPointF) -> None:
        angle = self._get_angle(from_point, to_point)
        arrow_size = 15
        arrow_point1 = QPointF(to_point.x() - arrow_size * 0.5, to_point.y() - arrow_size * 0.5)
        arrow_point2 = QPointF(to_point.x() - arrow_size * 0.5, to_point.y() + arrow_size * 0.5)
        import math
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        rotated_point1 = QPointF(
            to_point.x() + (arrow_point1.x() - to_point.x()) * cos_a - (arrow_point1.y() - to_point.y()) * sin_a,
            to_point.y() + (arrow_point1.x() - to_point.x()) * sin_a + (arrow_point1.y() - to_point.y()) * cos_a
        )
        rotated_point2 = QPointF(
            to_point.x() + (arrow_point2.x() - to_point.x()) * cos_a - (arrow_point2.y() - to_point.y()) * sin_a,
            to_point.y() + (arrow_point2.x() - to_point.x()) * sin_a + (arrow_point2.y() - to_point.y()) * cos_a
        )
        painter.setBrush(QBrush(self.color))
        painter.drawPolygon([to_point, rotated_point1, rotated_point2])

    def _get_angle(self, from_point: QPointF, to_point: QPointF) -> float:
        import math
        dx = to_point.x() - from_point.x()
        dy = to_point.y() - from_point.y()
        return math.atan2(dy, dx)

    def copy(self):
        new_arrow = Arrow(self.source, self.target, self.direction)
        new_arrow.id = str(uuid.uuid4())
        new_arrow.set_selected(False)
        return new_arrow

    def to_dict(self) -> Dict:
        return {
            'class': 'Arrow',
            'id': str(self.id),
            'source_id': str(self.source.id) if self.source else None,
            'target_id': str(self.target.id) if self.target else None,
            'direction': self.direction.value,
            'color_r': self.color.red(),
            'color_g': self.color.green(),
            'color_b': self.color.blue()
        }


class Group(Shape):
    def __init__(self, pos: QPointF = QPointF(0, 0)):
        super().__init__(ShapeType.CIRCLE, pos)
        self.type = None
        self._shapes: List[Shape] = []
        self._relative_positions: List[QPointF] = []

    def add_shape(self, shape: Shape) -> None:
        self._shapes.append(shape)
        self._update_bounding_rect()

    def add_shapes(self, shapes: List[Shape]) -> None:
        for shape in shapes:
            self._shapes.append(shape)
        self._update_bounding_rect()

    def remove_shape(self, shape: Shape) -> bool:
        if shape in self._shapes:
            idx = self._shapes.index(shape)
            self._shapes.remove(shape)
            self._relative_positions.pop(idx)
            self._update_bounding_rect()
            return True
        return False

    def get_shapes(self) -> List[Shape]:
        return self._shapes.copy()

    def is_empty(self) -> bool:
        return len(self._shapes) == 0

    def _update_bounding_rect(self) -> None:
        if not self._shapes:
            self._size = QSizeF(0, 0)
            return
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        for shape in self._shapes:
            rect = shape.get_bounding_rect()
            min_x = min(min_x, rect.left())
            min_y = min(min_y, rect.top())
            max_x = max(max_x, rect.right())
            max_y = max(max_y, rect.bottom())
        new_center_x = (min_x + max_x) / 2
        new_center_y = (min_y + max_y) / 2
        self.position = QPointF(new_center_x, new_center_y)
        self._size = QSizeF(max_x - min_x, max_y - min_y)
        self._update_relative_positions()

    def get_bounding_rect(self) -> QRectF:
        if not self._shapes:
            return QRectF(self.position.x() - 50, self.position.y() - 50, 100, 100)
        min_x = float('inf')
        min_y = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        for shape in self._shapes:
            rect = shape.get_bounding_rect()
            min_x = min(min_x, rect.left())
            min_y = min(min_y, rect.top())
            max_x = max(max_x, rect.right())
            max_y = max(max_y, rect.bottom())
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def contains_point(self, point: QPointF) -> bool:
        for shape in self._shapes:
            if shape.contains_point(point):
                return True
        return False

    def move(self, delta: QPointF, bounds: QRectF) -> bool:
        new_rect = self.get_bounding_rect().translated(delta)
        if bounds.contains(new_rect):
            self.position += delta
            for i, shape in enumerate(self._shapes):
                shape.move(delta, bounds)
                self._relative_positions[i] = shape.position - self.position
            return True
        return False

    def resize(self, delta_width: float, delta_height: float, bounds: QRectF) -> bool:
        if not self._shapes:
            return False
        old_group_size = QSizeF(self._size)
        old_group_pos = QPointF(self.position)
        old_sizes = []
        old_positions = []
        old_rel_positions = []
        for i, shape in enumerate(self._shapes):
            old_sizes.append(QSizeF(shape._size))
            old_positions.append(QPointF(shape.position))
            old_rel_positions.append(QPointF(self._relative_positions[i]))
        old_rect = self.get_bounding_rect()
        old_width = old_rect.width()
        old_height = old_rect.height()
        new_width = max(10, old_width + delta_width)
        new_height = max(10, old_height + delta_height)
        scale_x = new_width / old_width if old_width > 0 else 1
        scale_y = new_height / old_height if old_height > 0 else 1
        for i, shape in enumerate(self._shapes):
            new_w = max(10, shape._size.width() * scale_x)
            new_h = max(10, shape._size.height() * scale_y)
            dw = new_w - shape._size.width()
            dh = new_h - shape._size.height()
            shape.resize(dw, dh, bounds)
            new_rel_x = old_rel_positions[i].x() * scale_x
            new_rel_y = old_rel_positions[i].y() * scale_y
            self._relative_positions[i] = QPointF(new_rel_x, new_rel_y)
            shape.position = self.position + self._relative_positions[i]
        self._size = QSizeF(new_width, new_height)
        if bounds.contains(self.get_bounding_rect()):
            return True
        else:
            for i, shape in enumerate(self._shapes):
                shape._size = old_sizes[i]
                shape.position = old_positions[i]
                self._relative_positions[i] = old_rel_positions[i]
                if isinstance(shape, Group):
                    shape._update_bounding_rect()
            self.position = old_group_pos
            self._size = old_group_size
            return False

    def set_color(self, color: QColor) -> None:
        for shape in self._shapes:
            shape.set_color(color)

    def draw(self, painter: QPainter) -> None:
        for shape in self._shapes:
            shape.draw(painter)

    def draw_selection_rect(self, painter: QPainter) -> None:
        if self._selected:
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.get_bounding_rect())
    
        for shape in self._shapes:
            if isinstance(shape, Group):
                shape.draw_selection_rect(painter)

    def copy(self):
        new_group = Group(self.position + QPointF(20, 20))
        for shape in self._shapes:
            new_group.add_shape(shape.copy())
        new_group.id = str(uuid.uuid4())
        new_group.set_selected(False)
        return new_group

    def set_selected(self, selected: bool) -> None:
        self._selected = selected

    def to_dict(self) -> Dict:
        return {
            'class': 'Group',
            'id': str(self.id),
            'position_x': self.position.x(),
            'position_y': self.position.y(),
            'size_w': self._size.width(),
            'size_h': self._size.height(),
            'shapes': [shape.to_dict() for shape in self._shapes]
        }

    def from_dict(self, data: Dict) -> None:
        id_str = data.get('id', str(uuid.uuid4()))
        self.id = str(id_str) if isinstance(id_str, str) else str(id_str)
        self.position = QPointF(data['position_x'], data['position_y'])
        self._size = QSizeF(data['size_w'], data['size_h'])
        self._shapes.clear()
        self._relative_positions.clear()
        for shape_data in data.get('shapes', []):
            shape = ShapeFactory.create_from_dict(shape_data)
            if shape:
                self._shapes.append(shape)
                self._relative_positions.append(shape.position - self.position)

    def _update_relative_positions(self) -> None:
        self._relative_positions = []
        for shape in self._shapes:
            self._relative_positions.append(shape.position - self.position)


class ShapeFactory:
    _shape_classes = {
        'Circle': Circle,
        'Square': Square,
        'Ellipse': Ellipse,
        'Rectangle': Rectangle,
        'Triangle': Triangle,
        'Line': Line,
        'Group': Group,
    }

    @classmethod
    def create_from_dict(cls, data: Dict) -> Optional[Shape]:
        class_name = data.get('class')
        shape_class = cls._shape_classes.get(class_name)
        if shape_class:
            if class_name == 'Group':
                shape = Group()
                shape.from_dict(data)
                return shape
            else:
                shape = shape_class(QPointF(0, 0))
                shape.from_dict(data)
                return shape
        return None


class Command(ABC):
    @abstractmethod    
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass

    @abstractmethod
    def redo(self) -> None:
        pass


class AddShapeCommand(Command):
    def __init__(self, canvas, shape: Shape):
        self.canvas = canvas
        self.shape = shape
        self.added = False

    def execute(self) -> None:
        if not self.added:
            self.canvas.shapes.add(self.shape)
            self.added = True
            self.canvas.update()

    def undo(self) -> None:
        if self.added:
            for i in range(self.canvas.shapes.get_count()):
                obj = self.canvas.shapes.get_object(i)
                if obj and obj.id == self.shape.id:
                    self.canvas.shapes.remove_at(i)
                    break
            self.added = False
            self.canvas.update()

    def redo(self) -> None:
        self.execute()


class DeleteWithArrowsCommand(Command):
    def __init__(self, canvas, shapes: List[Shape], arrows: List[Arrow]):
        self.canvas = canvas
        self.shapes = shapes
        self.arrows = arrows
        self.shapes_data = []
        self.arrows_data = []

    def execute(self) -> None:
        self.shapes_data = []
        for shape in self.shapes:
            self.shapes_data.append(shape.copy())
        self.arrows_data = []
        for arrow in self.arrows:
            arrow_copy = Arrow(arrow.source, arrow.target, arrow.direction)
            arrow_copy.id = arrow.id
            arrow_copy.color = QColor(arrow.color)
            self.arrows_data.append(arrow_copy)
        for arrow in self.arrows:
            self.canvas.arrow_manager.remove_arrow(arrow)
            for i in range(self.canvas.shapes.get_count()):
                obj = self.canvas.shapes.get_object(i)
                if obj and obj.id == arrow.id:
                    self.canvas.shapes.remove_at(i)
                    break
        for shape in self.shapes:
            for i in range(self.canvas.shapes.get_count()):
                obj = self.canvas.shapes.get_object(i)
                if obj and obj.id == shape.id:
                    self.canvas.shapes.remove_at(i)
                    break
        self.canvas.update()
        if self.canvas.main_window:
            self.canvas.main_window.update_size_spins()

    def undo(self) -> None:
        for shape_data in self.shapes_data:
            self.canvas.shapes.add(shape_data)
        for arrow_data in self.arrows_data:
            self.canvas.arrow_manager.add_arrow(arrow_data)
            self.canvas.shapes.add(arrow_data)
        self.canvas.update()
        if self.canvas.main_window:
            self.canvas.main_window.update_size_spins()
            self.canvas.main_window.tree_view.refresh_tree()

    def redo(self) -> None:
        for arrow_data in self.arrows_data:
            self.canvas.arrow_manager.remove_arrow(arrow_data)
            for i in range(self.canvas.shapes.get_count()):
                obj = self.canvas.shapes.get_object(i)
                if obj and obj.id == arrow_data.id:
                    self.canvas.shapes.remove_at(i)
                    break
        for shape_data in self.shapes_data:
            for i in range(self.canvas.shapes.get_count()):
                obj = self.canvas.shapes.get_object(i)
                if obj and obj.id == shape_data.id:
                    self.canvas.shapes.remove_at(i)
                    break
        self.canvas.update()
        if self.canvas.main_window:
            self.canvas.main_window.update_size_spins()
            self.canvas.main_window.tree_view.refresh_tree()


class CommandManager:
    def __init__(self, max_history: int = 100):
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = max_history

    def execute_command(self, command: Command) -> None:
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()
        while len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

    def undo(self) -> bool:
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
            return True
        return False

    def redo(self) -> bool:
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.redo()
            self.undo_stack.append(command)
            return True
        return False

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0


class Canvas(QWidget):
    selection_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shapes = MyStorage(1000)
        self.arrow_manager = ArrowManager()
        self.current_tool = None
        self.dragging = False
        self.drag_start_pos = None
        self.drag_start_shape_positions = []
        self.clipboard = []
        self.setMinimumSize(400, 400)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.main_window = parent
        self._selection_rect_start = None
        self._selection_rect = None
        self.command_manager = CommandManager()
        self._arrow_creation_mode = False
        self._arrow_source = None
        self._arrow_direction = Direction.FORWARD

    def load_from_file(self, filename: str) -> bool:
        if self.shapes.load_from_file(filename):
            self.arrow_manager.clear()
            for shape in self.shapes.get_all_objects():
                if isinstance(shape, Arrow):
                    self.arrow_manager.add_arrow(shape)
            self.update()
            if self.main_window:
                self.main_window.tree_view.refresh_tree()
            return True
        return False

    def update_object_position(self, obj: Shape, new_pos: QPointF) -> None:
        obj.position = new_pos
        self.arrow_manager.update_arrows_for_shape(obj)
        for shape in self.shapes:
            if isinstance(shape, Group) and obj in shape.get_shapes():
                shape._update_bounding_rect()
                break
        self.update()

    def start_arrow_creation_bidirectional(self) -> None:
        if not self.get_selected_shapes():
            self._arrow_creation_mode = True
            self._arrow_source = None
            self._arrow_direction = Direction.BOTH
            if self.main_window:
                self.main_window.show_status("Выберите исходный объект для двунаправленной стрелки")
        else:
            if self.main_window:
                self.main_window.show_status("Сначала снимите выделение")

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        for shape in self.shapes:
            shape.draw(painter)
        for shape in self.shapes:
            shape.draw_selection_rect(painter)
        if self._selection_rect:
            painter.setPen(QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._selection_rect)

    def get_selected_shapes(self) -> List[Shape]:
        return [self.shapes.get_object(i) for i in self.shapes.get_selected_indices()]

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()

            if self._arrow_creation_mode:
                for i in range(self.shapes.get_count() - 1, -1, -1):
                    shape = self.shapes.get_object(i)
                    if shape and shape.contains_point(pos) and not isinstance(shape, Arrow):
                        if self._arrow_source is None:
                            self._arrow_source = shape
                            self.update()
                        else:
                            arrow = Arrow(self._arrow_source, shape, self._arrow_direction)
                            self.arrow_manager.add_arrow(arrow)
                            self.shapes.add(arrow)
                            self._arrow_creation_mode = False
                            self._arrow_source = None
                            if self.main_window:
                                self.main_window.show_status("Стрелка создана")
                            self.update()
                            if self.main_window and self.main_window.tree_view:
                                self.main_window.tree_view.refresh_tree()
                        return
                self._arrow_creation_mode = False
                self._arrow_source = None
                self.update()
                return

            ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
            clicked_shape = None
            for i in range(self.shapes.get_count() - 1, -1, -1):
                shape = self.shapes.get_object(i)
                if shape and shape.contains_point(pos):
                    clicked_shape = shape
                    break

            if clicked_shape:
                if ctrl_pressed:
                    clicked_shape.set_selected(not clicked_shape.is_selected())
                else:
                    self.shapes.clear_selection()
                    clicked_shape.set_selected(True)
                self.dragging = True
                self.drag_start_pos = pos
                self.drag_start_shape_positions = []
                for shape in self.get_selected_shapes():
                    self.drag_start_shape_positions.append((shape, QPointF(shape.position)))
                self._selection_rect = None
                self.update()
                self.selection_changed.emit()
                if self.main_window:
                    self.main_window.tree_view.sync_selection_from_storage()
                    self.main_window.property_window.set_object(clicked_shape)
            else:
                if not ctrl_pressed:
                    self.shapes.clear_selection()
                    self.update()
                    self.selection_changed.emit()
                    if self.main_window:
                        self.main_window.property_window.set_object(None)
                        self.main_window.tree_view.sync_selection_from_storage()
                if self.current_tool is not None:
                    self.create_shape_at(pos)
                else:
                    self._selection_rect_start = pos
                    self._selection_rect = QRectF(pos, pos)

    def create_shape_at(self, pos: QPointF) -> None:
        shape_map = {
            ShapeType.CIRCLE: Circle,
            ShapeType.SQUARE: Square,
            ShapeType.ELLIPSE: Ellipse,
            ShapeType.RECTANGLE: Rectangle,
            ShapeType.TRIANGLE: Triangle,
            ShapeType.LINE: Line,
        }
        shape_class = shape_map.get(self.current_tool)
        if shape_class:
            new_shape = shape_class(pos)
            self.add_shape_with_undo(new_shape)
            if self.main_window:
                self.main_window.show_status(f"Создан {self.current_tool.value}")

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.dragging and self.drag_start_pos:
            delta = event.position() - self.drag_start_pos
            if delta != QPointF(0, 0):
                bounds = QRectF(0, 0, self.width(), self.height())
                selected = self.get_selected_shapes()
                affected_shapes = set()
                for shape in selected:
                    affected_shapes.update(self.arrow_manager.get_affected_shapes(shape))
                can_move = True
                for shape in affected_shapes:
                    new_rect = shape.get_bounding_rect().translated(delta)
                    if not bounds.contains(new_rect):
                        can_move = False
                        break
                if can_move:
                    for shape in affected_shapes:
                        shape.move(delta, bounds)
                    for shape in affected_shapes:
                        self.arrow_manager.update_arrows_for_shape(shape)
                    self.drag_start_pos = event.position()
                    self.drag_start_shape_positions = []
                    for shape in selected:
                        self.drag_start_shape_positions.append((shape, QPointF(shape.position)))
                    self.update()
        elif self._selection_rect_start:
            self._selection_rect = QRectF(self._selection_rect_start, event.position()).normalized()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._selection_rect_start and self._selection_rect:
            ctrl_pressed = event.modifiers() & Qt.KeyboardModifier.ControlModifier
            if not ctrl_pressed:
                self.shapes.clear_selection()
            for shape in self.shapes:
                if self._selection_rect.intersects(shape.get_bounding_rect()):
                    shape.set_selected(True)
            if self.main_window and self.main_window.tree_view:
                self.main_window.tree_view.sync_selection_from_storage()
            selected = self.get_selected_shapes()
            if self.main_window:
                if selected:
                    self.main_window.property_window.set_object(selected[0])
                else:
                    self.main_window.property_window.set_object(None)
            self._selection_rect_start = None
            self._selection_rect = None
            self.update()
            self.selection_changed.emit()
        self.dragging = False
        self.drag_start_pos = None
        self.drag_start_shape_positions = []

    def move_selected(self, delta: QPointF) -> None:
        selected = self.get_selected_shapes()
        if not selected:
            return
        bounds = QRectF(0, 0, self.width(), self.height())
        affected_shapes = set()
        for shape in selected:
            affected_shapes.update(self.arrow_manager.get_affected_shapes(shape))
        can_move = True
        for shape in affected_shapes:
            new_rect = shape.get_bounding_rect().translated(delta)
            if not bounds.contains(new_rect):
                can_move = False
                break
        if can_move and delta != QPointF(0, 0):
            for shape in affected_shapes:
                shape.move(delta, bounds)
            for shape in affected_shapes:
                self.arrow_manager.update_arrows_for_shape(shape)
            self.drag_start_shape_positions = []
            for shape in self.get_selected_shapes():
                self.drag_start_shape_positions.append((shape, QPointF(shape.position)))
            self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.command_manager.undo():
                self.update()
                if self.main_window:
                    self.main_window.update_size_spins()
                    self.main_window.show_status("Отменено")
                    self.main_window.tree_view.refresh_tree()
            return
        if event.key() == Qt.Key.Key_Y and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if self.command_manager.redo():
                self.update()
                if self.main_window:
                    self.main_window.update_size_spins()
                    self.main_window.show_status("Повторено")
            return
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
            return
        if event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.resize_selected(10, 10)
            return
        if event.key() == Qt.Key.Key_Minus:
            self.resize_selected(-10, -10)
            return
        selected = self.get_selected_shapes()
        if not selected:
            super().keyPressEvent(event)
            return
        delta = QPointF(0, 0)
        step = 5
        if event.key() == Qt.Key.Key_Left:
            delta = QPointF(-step, 0)
        elif event.key() == Qt.Key.Key_Right:
            delta = QPointF(step, 0)
        elif event.key() == Qt.Key.Key_Up:
            delta = QPointF(0, -step)
        elif event.key() == Qt.Key.Key_Down:
            delta = QPointF(0, step)
        else:
            super().keyPressEvent(event)
            return
        self.move_selected(delta)

    def resize_selected(self, dw: float, dh: float) -> None:
        selected = self.get_selected_shapes()
        if not selected:
            return
        bounds = QRectF(0, 0, self.width(), self.height())
        for shape in selected:
            command = ResizeShapeCommand(shape, dw, dh, bounds)
            self.command_manager.execute_command(command)
        self.update()
        if self.main_window:
            self.main_window.update_size_spins()

    def delete_selected(self) -> None:
        if self.get_selected_shapes():
            selected = self.get_selected_shapes()
            selected_arrows = [s for s in selected if isinstance(s, Arrow)]
            selected_shapes = [s for s in selected if not isinstance(s, Arrow)]
            selected_shape_ids = {shape.id for shape in selected_shapes}
            arrows_to_remove = list(selected_arrows)
            for arrow in self.arrow_manager.get_arrows():
                if arrow.source.id in selected_shape_ids or arrow.target.id in selected_shape_ids:
                    if arrow not in arrows_to_remove:
                        arrows_to_remove.append(arrow)
            if selected_shapes or arrows_to_remove:
                command = DeleteWithArrowsCommand(self, selected_shapes, arrows_to_remove)
                self.command_manager.execute_command(command)
            self.selection_changed.emit()
            if self.main_window:
                self.main_window.tree_view.refresh_tree()
                self.main_window.update_size_spins()

    def copy_selected(self) -> None:
        selected = self.get_selected_shapes()
        if selected:
            self.clipboard = []
            for shape in selected:
                if not isinstance(shape, Arrow):
                    self.clipboard.append(shape.copy())
            if self.main_window:
                self.main_window.show_status(f"Скопировано {len(self.clipboard)} фигур")

    def paste_shapes(self) -> None:
        if self.clipboard:
            new_shapes = []
            for shape in self.clipboard:
                if not isinstance(shape, Arrow):
                    new_shapes.append(shape.copy())
            bounds = QRectF(0, 0, self.width(), self.height())
            for shape in new_shapes:
                if bounds.contains(shape.get_bounding_rect()):
                    self.shapes.add(shape)
                else:
                    rect = shape.get_bounding_rect()
                    new_x = max(0, min(self.width() - rect.width(), rect.x()))
                    new_y = max(0, min(self.height() - rect.height(), rect.y()))
                    shape.position = QPointF(new_x + rect.width() / 2, new_y + rect.height() / 2)
                    self.shapes.add(shape)
            self.update()
            self.selection_changed.emit()
            if self.main_window:
                self.main_window.show_status(f"Вставлено {len(new_shapes)} фигур")

    def group_selected(self) -> None:
        selected = self.get_selected_shapes()
        if len(selected) < 2:
            if self.main_window:
                self.main_window.show_status("Выберите хотя бы 2 объекта для группировки")
            return
        command = GroupCommand(self, selected)
        self.command_manager.execute_command(command)
        self.selection_changed.emit()
        if self.main_window:
            self.main_window.show_status(f"Сгруппировано {len(selected)} объектов")

    def ungroup_selected(self) -> None:
        selected = self.get_selected_shapes()
        groups = [s for s in selected if isinstance(s, Group)]
        if not groups:
            if self.main_window:
                self.main_window.show_status("Выберите группу для разгруппировки")
            return
        arrows_to_remove = []
        for group in groups:
            group_shapes = set(group.get_shapes())
            group_shapes.add(group)
            for arrow in self.arrow_manager.get_arrows():
                if arrow.source in group_shapes or arrow.target in group_shapes:
                    arrows_to_remove.append(arrow)
        if arrows_to_remove:
            command = DeleteWithArrowsCommand(self, [], arrows_to_remove)
            self.command_manager.execute_command(command)
        command = UngroupCommand(self, groups)
        self.command_manager.execute_command(command)
        self.selection_changed.emit()
        if self.main_window:
            self.main_window.show_status(f"Разгруппировано {len(groups)} групп")
            self.main_window.tree_view.refresh_tree()

    def add_shape(self, shape: Shape) -> None:
        bounds = QRectF(0, 0, self.width(), self.height())
        if bounds.contains(shape.get_bounding_rect()):
            self.shapes.add(shape)
        else:
            rect = shape.get_bounding_rect()
            new_x = max(0, min(self.width() - rect.width(), rect.x()))
            new_y = max(0, min(self.height() - rect.height(), rect.y()))
            shape.position = QPointF(new_x + rect.width() / 2, new_y + rect.height() / 2)
            self.shapes.add(shape)
        self.update()

    def change_selected_color(self, color: QColor) -> None:
        for shape in self.get_selected_shapes():
            shape.set_color(color)
        self.update()

    def add_shape_with_undo(self, shape: Shape) -> None:
        command = AddShapeCommand(self, shape)
        self.command_manager.execute_command(command)

    def start_arrow_creation(self) -> None:
        if not self.get_selected_shapes():
            self._arrow_creation_mode = True
            self._arrow_source = None
            self._arrow_direction = Direction.FORWARD
            if self.main_window:
                self.main_window.show_status("Выберите исходный объект для однонаправленной стрелки")
        else:
            if self.main_window:
                self.main_window.show_status("Сначала снимите выделение")

    def cut_selected(self) -> None:
        self.copy_selected()
        self.delete_selected()

    def select_all(self) -> None:
        for shape in self.shapes:
            shape.set_selected(True)
        self.update()
        self.selection_changed.emit()

    def set_tool(self, tool: ShapeType) -> None:
        self.current_tool = tool
        if self.main_window:
            self.main_window.show_status(f"Выбран инструмент: {tool.value}")


class ResizeShapeCommand(Command):
    def __init__(self, shape: Shape, dw: float, dh: float, bounds: QRectF):
        self.shape = shape
        self.dw = dw
        self.dh = dh
        self.bounds = bounds
        self.old_width = shape._size.width()
        self.old_height = shape._size.height()
        self.old_position = QPointF(shape.position)

    def execute(self) -> None:
        self.shape.resize(self.dw, self.dh, self.bounds)

    def undo(self) -> None:
        self.shape._size = QSizeF(self.old_width, self.old_height)
        self.shape.position = self.old_position
        if isinstance(self.shape, Group):
            self.shape._update_bounding_rect()
            self.shape._update_relative_positions()

    def redo(self) -> None:
        self.shape.resize(self.dw, self.dh, self.bounds)


class GroupCommand(Command):
    def __init__(self, canvas, shapes: List[Shape]):
        self.canvas = canvas
        self.shapes = shapes
        self.group = None
        self.indices = []

    def execute(self) -> None:
        if not self.group:
            self.group = Group()
            for shape in self.shapes:
                self.group._shapes.append(shape)
            self.group._relative_positions = []
            for shape in self.group._shapes:
                self.group._relative_positions.append(shape.position - self.group.position)
            self.group._update_bounding_rect()
            self.indices = []
            for shape in self.shapes:
                for i in range(self.canvas.shapes.get_count()):
                    obj = self.canvas.shapes.get_object(i)
                    if obj and obj.id == shape.id:
                        self.indices.append(i)
                        break
            for index in sorted(self.indices, reverse=True):
                self.canvas.shapes.remove_at(index)
            self.canvas.shapes.add(self.group)
            self.group.set_selected(True)
        else:
            self.canvas.shapes.add(self.group)
            self.group.set_selected(True)
        self.canvas.update()

    def undo(self) -> None:
        for i in range(self.canvas.shapes.get_count()):
            obj = self.canvas.shapes.get_object(i)
            if obj and obj.id == self.group.id:
                self.canvas.shapes.remove_at(i)
                break
        for shape in self.shapes:
            self.canvas.shapes.add(shape)
        self.canvas.update()

    def redo(self) -> None:
        self.execute()


class UngroupCommand(Command):
    def __init__(self, canvas, groups: List[Group]):
        self.canvas = canvas
        self.groups = groups
        self.all_shapes = []
        self.group_indices = []

    def execute(self) -> None:
        self.all_shapes = []
        self.group_indices = []
        for group in self.groups:
            for shape in group.get_shapes():
                self.all_shapes.append(shape)
            for i in range(self.canvas.shapes.get_count()):
                obj = self.canvas.shapes.get_object(i)
                if obj and obj.id == group.id:
                    self.group_indices.append(i)
                    break
        for index in sorted(self.group_indices, reverse=True):
            self.canvas.shapes.remove_at(index)
        for shape in self.all_shapes:
            shape.set_selected(True)
            self.canvas.shapes.add(shape)
        self.canvas.update()

    def undo(self) -> None:
        for shape in self.all_shapes:
            for i in range(self.canvas.shapes.get_count()):
                obj = self.canvas.shapes.get_object(i)
                if obj and obj.id == shape.id:
                    self.canvas.shapes.remove_at(i)
                    break
        for group in self.groups:
            self.canvas.shapes.add(group)
            group.set_selected(True)
        self.canvas.update()

    def redo(self) -> None:
        self.execute()


class MyStorage:
    def __init__(self, capacity: int = 1000):
        self._array: List[Optional[Any]] = [None] * capacity
        self._count: int = 0
        self._capacity: int = capacity
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, event_type: str, data: Any = None) -> None:
        for observer in self._observers:
            observer.update(event_type, data)

    def add(self, obj: Any) -> bool:
        if self._count < self._capacity:
            self._array[self._count] = obj
            self._count += 1
            self.notify_observers('add', obj)
            return True
        return False

    def remove_at(self, index: int) -> bool:
        if 0 <= index < self._count:
            obj = self._array[index]
            for i in range(index, self._count - 1):
                self._array[i] = self._array[i + 1]
            self._array[self._count - 1] = None
            self._count -= 1
            self.notify_observers('remove', obj)
            return True
        return False

    def get_count(self) -> int:
        return self._count

    def get_object(self, index: int) -> Optional[Any]:
        if 0 <= index < self._count:
            return self._array[index]
        return None

    def clear_selection(self) -> None:
        for i in range(self._count):
            if self._array[i]:
                self._array[i].set_selected(False)
        self.notify_observers('selection_changed')

    def get_selected_indices(self) -> List[int]:
        return [i for i in range(self._count) if self._array[i] and self._array[i].is_selected()]

    def remove_selected(self) -> None:
        indices = self.get_selected_indices()
        for index in sorted(indices, reverse=True):
            self.remove_at(index)

    def get_all_objects(self) -> List[Any]:
        return [self._array[i] for i in range(self._count) if self._array[i]]

    def __iter__(self):
        for i in range(self._count):
            if self._array[i]:
                yield self._array[i]

    def save_to_file(self, filename: str) -> bool:
        try:
            data = {
                'count': self._count,
                'objects': []
            }
            for obj in self.get_all_objects():
                try:
                    obj_dict = obj.to_dict()
                    data['objects'].append(obj_dict)
                except Exception as e:
                    print(f"Ошибка при сохранении объекта {type(obj)}: {e}")
                    continue
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    def load_from_file(self, filename: str) -> bool:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return False
            self._array = [None] * self._capacity
            self._count = 0
            self._observers.clear()
            temp_objects = []
            arrow_data_list = []
            for obj_data in data.get('objects', []):
                if obj_data.get('class') != 'Arrow':
                    shape = ShapeFactory.create_from_dict(obj_data)
                    if shape:
                        self.add(shape)
                        temp_objects.append(shape)
                else:
                    arrow_data_list.append(obj_data)
            shape_map = {str(obj.id): obj for obj in temp_objects}
            for arrow_data in arrow_data_list:
                source_id_str = str(arrow_data.get('source_id'))
                target_id_str = str(arrow_data.get('target_id'))
                if source_id_str and target_id_str:
                    source = shape_map.get(source_id_str)
                    target = shape_map.get(target_id_str)
                    if source and target:
                        direction = Direction(arrow_data.get('direction', 'forward'))
                        arrow = Arrow(source, target, direction)
                        arrow.id = str(arrow_data.get('id', str(uuid.uuid4())))
                        arrow.color = QColor(
                            arrow_data['color_r'],
                            arrow_data['color_g'],
                            arrow_data['color_b']
                        )
                        self.add(arrow)
            self.notify_observers('load_complete')
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False


class ArrowManager:
    def __init__(self):
        self._arrows: List[Arrow] = []

    def remove_arrows_for_shape(self, shape: Shape) -> List[Arrow]:
        removed = []
        for arrow in self._arrows[:]:
            if arrow.source == shape or arrow.target == shape:
                self._arrows.remove(arrow)
                removed.append(arrow)
        return removed

    def get_all_connected_shapes(self, shape: Shape, visited: Set[str] = None, direction_from: str = None) -> Set[Shape]:
        if visited is None:
            visited = set()
        if shape.id in visited:
            return set()
        visited.add(shape.id)
        result = {shape}
        for arrow in self._arrows:
            try:
                if arrow.source and arrow.target:
                    if arrow.source.id == shape.id:
                        result.update(self.get_all_connected_shapes(arrow.target, visited, 'forward'))
                    if arrow.direction == Direction.BOTH and arrow.target.id == shape.id:
                        result.update(self.get_all_connected_shapes(arrow.source, visited, 'backward'))
            except:
                pass
        return result

    def add_arrow(self, arrow: Arrow) -> None:
        self._arrows.append(arrow)

    def remove_arrow(self, arrow: Arrow) -> None:
        if arrow in self._arrows:
            self._arrows.remove(arrow)

    def get_arrows(self) -> List[Arrow]:
        return self._arrows.copy()

    def update_arrows_for_shape(self, shape: Shape) -> None:
        for arrow in self._arrows:
            if arrow.source == shape or arrow.target == shape:
                arrow.update_connection()

    def get_affected_shapes(self, shape: Shape, visited: Set[str] = None) -> Set[Shape]:
        return self.get_all_connected_shapes(shape, visited)

    def clear(self) -> None:
        self._arrows.clear()


class TreeViewObserver(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Объекты")
        self.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self._storage: Optional[MyStorage] = None
        self._updating = False
        self.main_window = None

    def set_storage(self, storage: MyStorage) -> None:
        self._storage = storage
        self._storage.add_observer(self)
        self.refresh_tree()

    def update(self, event_type: str, data: Any = None) -> None:
        if self._updating:
            return
        try:
            if event_type in ['add', 'remove', 'load_complete']:
                self.refresh_tree()
            elif event_type == 'selection_changed':
                self.sync_selection_from_storage()
        except:
            pass

    def refresh_tree(self) -> None:
        if self._updating or not self._storage:
            return
        self._updating = True
        self.clear()
        for obj in self._storage.get_all_objects():
            self._add_object_to_tree(None, obj)
        self.expandAll()
        self._updating = False

    def _add_object_to_tree(self, parent: Optional[QTreeWidgetItem], obj: Any) -> QTreeWidgetItem:
        item = QTreeWidgetItem(parent if parent else self)
        if isinstance(obj, Group):
            name = f"Группа ({len(obj.get_shapes())} объектов)"
        elif isinstance(obj, Arrow):
            name = "Стрелка"
        else:
            name = f"{obj.type.value}"
        item.setText(0, name)
        item.setData(0, Qt.ItemDataRole.UserRole, obj.id)
        if isinstance(obj, Group):
            for child in obj.get_shapes():
                self._add_object_to_tree(item, child)
        return item

    def _get_object_name(self, obj: Any) -> str:
        if obj is None:
            return "None"
        if isinstance(obj, Group):
            return "Группа"
        if isinstance(obj, Arrow):
            return "Стрелка"
        return obj.type.value[:4]

    def on_tree_selection_changed(self) -> None:
        if self._updating or not self._storage:
            return
        self._updating = True
        selected_ids = set()
        for item in self.selectedItems():
            obj_id = item.data(0, Qt.ItemDataRole.UserRole)
            if obj_id:
                selected_ids.add(obj_id)
        for obj in self._storage.get_all_objects():
            should_be_selected = obj.id in selected_ids
            if obj.is_selected() != should_be_selected:
                obj.set_selected(should_be_selected)
        self._storage.notify_observers('selection_changed')
        if self.main_window:
            self.main_window.canvas.update()
            selected = self.main_window.canvas.get_selected_shapes()
            if selected:
                self.main_window.property_window.set_object(selected[0])
            else:
                self.main_window.property_window.set_object(None)
        self._updating = False

    def sync_selection_from_storage(self) -> None:
        if self._updating or not self._storage:
            return
        self._updating = True
        self.clearSelection()
        selected_ids = {obj.id for obj in self._storage.get_all_objects() if obj.is_selected()}
        def select_items(item: QTreeWidgetItem):
            obj_id = item.data(0, Qt.ItemDataRole.UserRole)
            if obj_id and obj_id in selected_ids:
                item.setSelected(True)
            for i in range(item.childCount()):
                select_items(item.child(i))
        for i in range(self.topLevelItemCount()):
            select_items(self.topLevelItem(i))
        self._updating = False


class PropertyWindow(QWidget):
    property_changed = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Свойства")
        layout = QVBoxLayout(self)
        
        # Информационная метка
        self.info_label = QLabel("Выберите объект")
        layout.addWidget(self.info_label)
        
        # Таблица свойств (только для чтения)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Свойство", "Значение"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Группа для редактирования
        edit_group = QGroupBox("Редактирование")
        edit_layout = QFormLayout()
        
        self.x_spin = QSpinBox()
        self.x_spin.setRange(-5000, 5000)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(-5000, 5000)
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 5000)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 5000)
        
        self.color_btn = QPushButton("Выбрать цвет")
        self.color_btn.clicked.connect(self.choose_color)
        
        edit_layout.addRow("X:", self.x_spin)
        edit_layout.addRow("Y:", self.y_spin)
        edit_layout.addRow("Ширина:", self.width_spin)
        edit_layout.addRow("Высота:", self.height_spin)
        edit_layout.addRow("", self.color_btn)
        
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)
        
        # Подключаем сигналы
        self.x_spin.valueChanged.connect(self.on_coord_changed)
        self.y_spin.valueChanged.connect(self.on_coord_changed)
        self.width_spin.valueChanged.connect(self.on_size_changed)
        self.height_spin.valueChanged.connect(self.on_size_changed)
        
        self.current_object = None
        self._updating = False

    def choose_color(self):
        if self.current_object is None:
            return
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_object.set_color(color)
            self.set_object(self.current_object)
            if hasattr(self.parent(), 'canvas'):
                self.parent().canvas.update()

    def on_coord_changed(self):
        if self.current_object is None or self._updating:
            return
        self.current_object.position.setX(self.x_spin.value())
        self.current_object.position.setY(self.y_spin.value())
        if hasattr(self.parent(), 'canvas'):
            self.parent().canvas.arrow_manager.update_arrows_for_shape(self.current_object)
            self.parent().canvas.update()
        self.set_object(self.current_object)

    def on_size_changed(self):
        if self.current_object is None or self._updating:
            return
        bounds = QRectF(0, 0, 2000, 2000)
        new_w = self.width_spin.value()
        new_h = self.height_spin.value()
        dw = new_w - self.current_object._size.width()
        dh = new_h - self.current_object._size.height()
        self.current_object.resize(dw, dh, bounds)
        if hasattr(self.parent(), 'canvas'):
            self.parent().canvas.update()
        self.set_object(self.current_object)

    def set_object(self, obj: Any) -> None:
        self._updating = True
        try:
            self.current_object = obj
            if obj is None:
                self.info_label.setText("Выберите объект")
                self.table.setRowCount(0)
                self.x_spin.setEnabled(False)
                self.y_spin.setEnabled(False)
                self.width_spin.setEnabled(False)
                self.height_spin.setEnabled(False)
                self.color_btn.setEnabled(False)
                self._updating = False
                return
            
            # Включаем поля редактирования
            self.x_spin.setEnabled(True)
            self.y_spin.setEnabled(True)
            self.width_spin.setEnabled(True)
            self.height_spin.setEnabled(True)
            self.color_btn.setEnabled(True)
            
            # Заполняем спиннеры
            self.x_spin.blockSignals(True)
            self.y_spin.blockSignals(True)
            self.width_spin.blockSignals(True)
            self.height_spin.blockSignals(True)
            
            self.x_spin.setValue(int(obj.position.x()))
            self.y_spin.setValue(int(obj.position.y()))
            self.width_spin.setValue(int(obj._size.width()))
            self.height_spin.setValue(int(obj._size.height()))
            
            self.x_spin.blockSignals(False)
            self.y_spin.blockSignals(False)
            self.width_spin.blockSignals(False)
            self.height_spin.blockSignals(False)
            
            # Заполняем информационную таблицу
            if isinstance(obj, Group):
                type_name = "Группа"
            elif isinstance(obj, Arrow):
                type_name = "Стрелка"
            else:
                type_name = obj.type.value
            self.info_label.setText(f"Объект: {type_name}")
            
            properties = []
            properties.append(("ID", str(obj.id)[:8] + "...", "readonly"))
            properties.append(("Позиция X", round(obj.position.x(), 1), float))
            properties.append(("Позиция Y", round(obj.position.y(), 1), float))
            
            if not isinstance(obj, Arrow):
                properties.append(("Ширина", round(obj._size.width(), 1), float))
                properties.append(("Высота", round(obj._size.height(), 1), float))
            
            if hasattr(obj, 'color'):
                properties.append(("Цвет", f"RGB({obj.color.red()},{obj.color.green()},{obj.color.blue()})", str))
            
            if isinstance(obj, Arrow):
                properties.append(("Направление", obj.direction.value, "readonly"))
                source_name = self._get_short_name(obj.source)
                target_name = self._get_short_name(obj.target)
                properties.append(("Источник", source_name, "readonly"))
                properties.append(("Цель", target_name, "readonly"))
            
            if isinstance(obj, Group):
                properties.append(("Количество объектов", len(obj.get_shapes()), "readonly"))
            
            self.table.setRowCount(len(properties))
            for i, (name, value, value_type) in enumerate(properties):
                self.table.setItem(i, 0, QTableWidgetItem(name))
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, 1, item)
        except Exception as e:
            print(f"Ошибка в PropertyWindow: {e}")
            self.table.setRowCount(0)
            self.info_label.setText("Ошибка при загрузке свойств")
        finally:
            self._updating = False

    def _get_short_name(self, obj: Any) -> str:
        if obj is None:
            return "None"
        if isinstance(obj, Group):
            return f"Группа ({len(obj.get_shapes())})"
        if isinstance(obj, Arrow):
            return "Стрелка"
        return obj.type.value[:8]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Векторный редактор")
        self.setMinimumSize(1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Левая панель: дерево объектов и свойства
        left_panel = QWidget()
        left_panel.setMinimumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Вертикальный сплиттер для дерева и свойств
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Дерево объектов
        tree_group = QGroupBox()
        tree_group.setTitle("Дерево объектов")
        tree_layout = QVBoxLayout()
        self.tree_view = TreeViewObserver()
        self.tree_view.main_window = self
        tree_layout.addWidget(self.tree_view)
        tree_group.setLayout(tree_layout)
        left_splitter.addWidget(tree_group)
        
        # Окно свойств
        self.property_window = PropertyWindow()
        left_splitter.addWidget(self.property_window)
        
        left_splitter.setSizes([350, 400])
        left_layout.addWidget(left_splitter)
        splitter.addWidget(left_panel)

        # Холст
        self.canvas = Canvas(self)
        splitter.addWidget(self.canvas)

        splitter.setSizes([400, 800])

        # Панель инструментов
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Сохранение и загрузка
        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_to_file)
        toolbar.addAction(save_action)

        load_action = QAction("Загрузить", self)
        load_action.triggered.connect(self.load_from_file)
        toolbar.addAction(load_action)

        toolbar.addSeparator()

        # Фигуры
        shapes = [
            (ShapeType.CIRCLE, "Круг"),
            (ShapeType.SQUARE, "Квадрат"),
            (ShapeType.ELLIPSE, "Эллипс"),
            (ShapeType.RECTANGLE, "Прямоугольник"),
            (ShapeType.TRIANGLE, "Треугольник"),
            (ShapeType.LINE, "Линия")
        ]

        for shape_type, label in shapes:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, st=shape_type: self.canvas.set_tool(st))
            toolbar.addAction(action)

        toolbar.addSeparator()

        # Цвет
        color_action = QAction("Цвет", self)
        color_action.triggered.connect(self.change_color)
        toolbar.addAction(color_action)

        toolbar.addSeparator()

        # Стрелки
        arrow_one_way_action = QAction("Однонаправленная стрелка", self)
        arrow_one_way_action.triggered.connect(self.start_arrow_creation)
        toolbar.addAction(arrow_one_way_action)

        arrow_both_action = QAction("Двунаправленная стрелка", self)
        arrow_both_action.triggered.connect(self.start_arrow_creation_bidirectional)
        toolbar.addAction(arrow_both_action)

        toolbar.addSeparator()

        # Группировка
        group_action = QAction("Группировать", self)
        group_action.triggered.connect(self.group_selected)
        toolbar.addAction(group_action)

        ungroup_action = QAction("Разгруппировать", self)
        ungroup_action.triggered.connect(self.ungroup_selected)
        toolbar.addAction(ungroup_action)

        # Статусная строка
        self.statusBar().showMessage("Готов. Выберите инструмент и кликните на холсте для создания фигуры")

        # Подключение сигналов
        self.canvas.selection_changed.connect(self.update_size_spins)
        self.canvas.selection_changed.connect(self.on_canvas_selection_changed)

        try:
            self.tree_view.set_storage(self.canvas.shapes)
        except:
            pass

        # Спиннеры для размера (скрыты, но оставлены для функциональности)
        self.size_spin_width = QSpinBox()
        self.size_spin_width.setRange(10, 5000)
        self.size_spin_width.setFixedWidth(100)
        self.size_spin_width.valueChanged.connect(self.on_size_value_changed)

        self.size_spin_height = QSpinBox()
        self.size_spin_height.setRange(10, 5000)
        self.size_spin_height.setFixedWidth(100)
        self.size_spin_height.valueChanged.connect(self.on_size_value_changed)

        self.update_size_spins()

    def start_arrow_creation(self):
        self.canvas.start_arrow_creation()
        self.canvas.current_tool = None

    def start_arrow_creation_bidirectional(self):
        self.canvas.start_arrow_creation_bidirectional()
        self.canvas.current_tool = None

    def cut_selected(self):
        self.canvas.cut_selected()
        self.tree_view.refresh_tree()

    def group_selected(self):
        self.canvas.group_selected()
        self.tree_view.refresh_tree()

    def ungroup_selected(self):
        self.canvas.ungroup_selected()
        self.tree_view.refresh_tree()

    def update_size_spins(self):
        selected = self.canvas.get_selected_shapes()
        if len(selected) == 1:
            shape = selected[0]
            self.size_spin_width.setValue(int(shape._size.width()))
            self.size_spin_height.setValue(int(shape._size.height()))
            self.size_spin_width.setEnabled(True)
            self.size_spin_height.setEnabled(True)
        else:
            self.size_spin_width.setEnabled(False)
            self.size_spin_height.setEnabled(False)
            self.size_spin_width.clear()
            self.size_spin_height.clear()

    def on_size_value_changed(self):
        selected = self.canvas.get_selected_shapes()
        if len(selected) != 1:
            return
        sender = self.sender()
        shape = selected[0]
        bounds = QRectF(0, 0, self.canvas.width(), self.canvas.height())
        old_width = shape._size.width()
        old_height = shape._size.height()
        if sender == self.size_spin_width:
            new_width = self.size_spin_width.value()
            dw = new_width - old_width
            shape.resize(dw, 0, bounds)
            if abs(shape._size.width() - new_width) > 0.1:
                self.size_spin_width.blockSignals(True)
                self.size_spin_width.setValue(int(shape._size.width()))
                self.size_spin_width.blockSignals(False)
        elif sender == self.size_spin_height:
            new_height = self.size_spin_height.value()
            dh = new_height - old_height
            shape.resize(0, dh, bounds)
            if abs(shape._size.height() - new_height) > 0.1:
                self.size_spin_height.blockSignals(True)
                self.size_spin_height.setValue(int(shape._size.height()))
                self.size_spin_height.blockSignals(False)
        self.canvas.update()

    def change_color(self):
        selected = self.canvas.get_selected_shapes()
        if not selected:
            QMessageBox.information(self, "Информация", "Нет выбранных фигур")
            return
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.change_selected_color(color)
            self.show_status("Цвет изменён")

    def delete_selected(self):
        if self.canvas.get_selected_shapes():
            self.canvas.delete_selected()
            self.show_status("Удалены выбранные фигуры")

    def copy_selected(self):
        self.canvas.copy_selected()

    def paste_shapes(self):
        self.canvas.paste_shapes()

    def show_status(self, message: str):
        self.statusBar().showMessage(message, 2000)

    def save_to_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить проект", "", "JSON Files (*.json)")
        if filename:
            if self.canvas.shapes.save_to_file(filename):
                self.show_status(f"Проект сохранён в {filename}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить файл")

    def load_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Загрузить проект", "", "JSON Files (*.json)")
        if filename:
            if self.canvas.load_from_file(filename):
                self.canvas.update()
                self.update_size_spins()
                self.tree_view.refresh_tree()
                self.show_status(f"Проект загружен из {filename}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить файл")

    def on_canvas_selection_changed(self):
        selected = self.canvas.get_selected_shapes()
        if selected:
            self.property_window.set_object(selected[0])
        else:
            self.property_window.set_object(None)

    def undo(self):
        if self.canvas.command_manager.undo():
            self.canvas.update()
            self.tree_view.refresh_tree()
            self.update_size_spins()
            self.show_status("Отменено")

    def redo(self):
        if self.canvas.command_manager.redo():
            self.canvas.update()
            self.tree_view.refresh_tree()
            self.update_size_spins()
            self.show_status("Повторено")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())