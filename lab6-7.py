import sys
import uuid
from enum import Enum
from typing import List, Optional, Any, Dict
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QColorDialog, QApplication, QLabel,
    QMessageBox, QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSizeF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF, QAction, QKeyEvent, QMouseEvent


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

    def set_color(self, color: QColor) -> None:
        self.color = QColor(color)

    def draw(self, painter: QPainter) -> None:
        painter.setBrush(QBrush(self.color))
        if self._selected:
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
        else:
            painter.setPen(QPen(Qt.GlobalColor.black, 1))

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
        self.id = str(data.get('id', str(uuid.uuid4())))
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
        return QRectF(self.position.x() - half_length, self.position.y() - 2, self._size.width(), 4)

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


class Group(Shape):
    def __init__(self, pos: QPointF = QPointF(0, 0)):
        super().__init__(ShapeType.CIRCLE, pos)
        self.type = None
        self._shapes: List[Shape] = []
        self._relative_positions: List[QPointF] = []

    def add_shape(self, shape: Shape) -> None:
        self._shapes.append(shape)
        self._update_bounding_rect()

    def get_shapes(self) -> List[Shape]:
        return self._shapes.copy()

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

    def copy(self):
        new_group = Group(self.position + QPointF(20, 20))
        for shape in self._shapes:
            new_group.add_shape(shape.copy())
        new_group.id = str(uuid.uuid4())
        new_group.set_selected(False)
        return new_group

    def _update_relative_positions(self) -> None:
        self._relative_positions = []
        for shape in self._shapes:
            self._relative_positions.append(shape.position - self.position)

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
        self.id = str(data.get('id', str(uuid.uuid4())))
        self.position = QPointF(data['position_x'], data['position_y'])
        self._size = QSizeF(data['size_w'], data['size_h'])
        self._shapes.clear()
        for shape_data in data.get('shapes', []):
            shape = ShapeFactory.create_from_dict(shape_data)
            if shape:
                self._shapes.append(shape)
        self._update_relative_positions()        

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

class MyStorage:
    def __init__(self, capacity: int = 1000):
        self._array: List[Optional[Any]] = [None] * capacity
        self._count: int = 0
        self._capacity: int = capacity

    def add(self, obj: Any) -> bool:
        if self._count < self._capacity:
            self._array[self._count] = obj
            self._count += 1
            return True
        return False

    def remove_at(self, index: int) -> bool:
        if 0 <= index < self._count:
            for i in range(index, self._count - 1):
                self._array[i] = self._array[i + 1]
            self._array[self._count - 1] = None
            self._count -= 1
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

    def get_selected_indices(self) -> List[int]:
        return [i for i in range(self._count) if self._array[i] and self._array[i].is_selected()]

    def get_all_objects(self) -> List[Any]:
        return [self._array[i] for i in range(self._count) if self._array[i]]

    def __iter__(self):
        for i in range(self._count):
            if self._array[i]:
                yield self._array[i]

    def save_to_file(self, filename: str) -> bool:
        try:
            data = {'objects': []}
            for obj in self.get_all_objects():
                data['objects'].append(obj.to_dict())
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    def load_from_file(self, filename: str) -> bool:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._array = [None] * self._capacity
            self._count = 0
            for obj_data in data.get('objects', []):
                shape = ShapeFactory.create_from_dict(obj_data)
                if shape:
                    self.add(shape)
            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False

class Canvas(QWidget):
    selection_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shapes = MyStorage(1000)
        self.current_tool = None
        self.dragging = False
        self.drag_start_pos = None
        self.setMinimumSize(400, 400)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.main_window = parent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        for shape in self.shapes:
            shape.draw(painter)
        for shape in self.shapes:
            shape.draw_selection_rect(painter)

    def get_selected_shapes(self) -> List[Shape]:
        return [self.shapes.get_object(i) for i in self.shapes.get_selected_indices()]

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
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
                self.update()
                self.selection_changed.emit()
            else:
                if not ctrl_pressed:
                    self.shapes.clear_selection()
                    self.update()
                    self.selection_changed.emit()
                if self.current_tool is not None:
                    self.create_shape_at(pos)

    def create_shape_at(self, pos):
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
            self.shapes.add(new_shape)
            self.update()
            if self.main_window:
                self.main_window.show_status(f"Создан {self.current_tool.value}")

    def mouseMoveEvent(self, event):
        if self.dragging and self.drag_start_pos:
            delta = event.position() - self.drag_start_pos
            if delta != QPointF(0, 0):
                bounds = QRectF(0, 0, self.width(), self.height())
                for shape in self.get_selected_shapes():
                    shape.move(delta, bounds)
                self.drag_start_pos = event.position()
                self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.drag_start_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
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

    def move_selected(self, delta):
        if not self.get_selected_shapes():
            return
        bounds = QRectF(0, 0, self.width(), self.height())
        for shape in self.get_selected_shapes():
            shape.move(delta, bounds)
        self.update()

    def delete_selected(self):
        if self.get_selected_shapes():
            selected = self.get_selected_shapes()
            for shape in selected:
                for i in range(self.shapes.get_count()):
                    obj = self.shapes.get_object(i)
                    if obj and obj.id == shape.id:
                        self.shapes.remove_at(i)
                        break
            self.update()
            self.selection_changed.emit()

    def group_selected(self):
        selected = self.get_selected_shapes()
        if len(selected) < 2:
            if self.main_window:
                self.main_window.show_status("Выберите хотя бы 2 объекта")
            return
        group = Group()
        for shape in selected:
            group.add_shape(shape)
        for shape in selected:
            for i in range(self.shapes.get_count()):
                obj = self.shapes.get_object(i)
                if obj and obj.id == shape.id:
                    self.shapes.remove_at(i)
                    break
        self.shapes.add(group)
        group.set_selected(True)
        self.update()
        self.selection_changed.emit()
        if self.main_window:
            self.main_window.show_status(f"Сгруппировано {len(selected)} объектов")

    def ungroup_selected(self):
        selected = self.get_selected_shapes()
        groups = [s for s in selected if isinstance(s, Group)]
        if not groups:
            if self.main_window:
                self.main_window.show_status("Выберите группу")
            return
        for group in groups:
            for shape in group.get_shapes():
                self.shapes.add(shape)
                shape.set_selected(True)
            for i in range(self.shapes.get_count()):
                obj = self.shapes.get_object(i)
                if obj and obj.id == group.id:
                    self.shapes.remove_at(i)
                    break
        self.update()
        self.selection_changed.emit()
        if self.main_window:
            self.main_window.show_status(f"Разгруппировано {len(groups)} групп")

    def change_selected_color(self, color):
        for shape in self.get_selected_shapes():
            shape.set_color(color)
        self.update()

    def set_tool(self, tool):
        self.current_tool = tool
        if self.main_window:
            self.main_window.show_status(f"Выбран инструмент: {tool.value}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Векторный редактор")
        self.setMinimumSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = Canvas(self)
        layout.addWidget(self.canvas)

        toolbar = QToolBar()
        self.addToolBar(toolbar)

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
        color_action = QAction("Цвет", self)
        color_action.triggered.connect(self.change_color)
        toolbar.addAction(color_action)

        toolbar.addSeparator()
        group_action = QAction("Группировать", self)
        group_action.triggered.connect(self.canvas.group_selected)
        toolbar.addAction(group_action)

        ungroup_action = QAction("Разгруппировать", self)
        ungroup_action.triggered.connect(self.canvas.ungroup_selected)
        toolbar.addAction(ungroup_action)

        self.statusBar().showMessage("Готов")
        toolbar.addSeparator()
        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self.save_to_file)
        toolbar.addAction(save_action)

        load_action = QAction("Загрузить", self)
        load_action.triggered.connect(self.load_from_file)
        toolbar.addAction(load_action)


# Добавить методы в MainWindow:
    def save_to_file(self):
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить проект", "", "JSON Files (*.json)")
        if filename:
            if self.canvas.shapes.save_to_file(filename):
                self.show_status(f"Сохранено в {filename}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить")

    def load_from_file(self):
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Загрузить проект", "", "JSON Files (*.json)")
        if filename:
            if self.canvas.shapes.load_from_file(filename):
                self.canvas.update()
                self.show_status(f"Загружено из {filename}")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить")

    def change_color(self):
        selected = self.canvas.get_selected_shapes()
        if not selected:
            QMessageBox.information(self, "Информация", "Нет выбранных фигур")
            return
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.change_selected_color(color)
            self.show_status("Цвет изменён")

    def show_status(self, message):
        self.statusBar().showMessage(message, 2000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())