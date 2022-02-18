from PySide6.QtWidgets import QItemDelegate, QStyledItemDelegate, QStyle, QLineEdit, QListWidget, QListWidgetItem, \
    QComboBox, QApplication, QAbstractItemView
from PySide6.QtGui import QIcon, QDoubleValidator, QPixmap, QColor
from PySide6.QtCore import Qt, QEvent, QRect, QLocale, Signal

import logging
log = logging.getLogger(__name__)

class CheckBoxDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox cell into the column to which it's applied.
    """
    def __init__(self, key = None):
        super().__init__()
        self._key = key


    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def paint(self, painter, option, index):
        """
        Paint a checkbox with a label and adjust the lateral positioning.
        """
        if self._key == None:
            # If no key is supplied then draw a centred checkbox.
            self.drawCheck(painter, option, option.rect, Qt.Unchecked if index.data() == False else Qt.Checked)
        else:
            # If a key is supplied, draw the text and (manually) re-centre everything.
            x1, y1, x2, y2 = option.rect.getCoords()
            adjRect = QRect()
            adjRect.setCoords(x1, y1, x2, y2)
            dx = -25
            adjRect.adjust(dx,0,dx,0)
            self.drawCheck(painter, option, adjRect, Qt.Unchecked if index.data() == False else Qt.Checked)
            model = index.model()
            item = model._data[index.row()]
            string = item[self._key]
            adjRect = QRect()
            adjRect.setCoords(x1, y1, x2, y2)
            dx = -int((x1-x2)/2)-10
            adjRect.adjust(dx,0,dx,0)
            self.drawDisplay(painter, option, adjRect, string)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton and this cell is editable. Otherwise do nothing.
        '''
        if not int(index.flags() & Qt.ItemIsEditable) > 0:
            return False

        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            # Change the checkbox-state.
            self.setModelData(None, model, index)
            return True

        return False

    def setModelData (self, editor, model, index):
        '''
        Change the underlying data model.
        '''
        model.setData(index, not index.data(), Qt.EditRole)

class ConnectionIconDelegate(QStyledItemDelegate):
    """
    Show the appropriate connection icon.
    """
    def __init__(self):
        super().__init__()
    
    def paint(self, painter, option, index):
<<<<<<< HEAD
        if self.darkmode == True:
=======
        model = index.model()
        if self.darkmode == True: # 0-4 are Labjack Devices, 10-14 are Mbed Devices 
>>>>>>> ef201362b9151a380c985dd5acef6b7b21de82f9
            if index.data(Qt.DisplayRole) == 0:
                icon = QIcon("assets/sensors_off_white_24dp.svg")
            elif index.data(Qt.DisplayRole) == 1:
                icon = QIcon("assets/usb_white_24dp.svg")
            elif index.data(Qt.DisplayRole) == 3:
                icon = QIcon("assets/cable_white_24dp.svg")
            elif index.data(Qt.DisplayRole) == 4:
                icon = QIcon("assets/wifi_white_24dp.svg")
<<<<<<< HEAD

=======
            
>>>>>>> ef201362b9151a380c985dd5acef6b7b21de82f9
            # Following are Mbed Devices 
            elif index.data(Qt.DisplayRole) == 10:
                icon = QIcon("assets/sensors_off_white_24dp.svg")
            elif index.data(Qt.DisplayRole) == 11: 
                icon = QIcon("assets/usb_white_24dp.svg")  # Mbed USB Device 
            elif index.data(Qt.DisplayRole) == 13:
                icon = QIcon("assets/cable_white_24dp.svg")
            elif index.data(Qt.DisplayRole) == 14:
                icon = QIcon("assets/wifi_white_24dp.svg")
        else:
            if index.data(Qt.DisplayRole) == 0:
                icon = QIcon("assets/sensors_off_black_24dp.svg")
            elif index.data(Qt.DisplayRole) == 1:
                icon = QIcon("assets/usb_black_24dp.svg")
            elif index.data(Qt.DisplayRole) == 3:
                icon = QIcon("assets/cable_black_24dp.svg")
            elif index.data(Qt.DisplayRole) == 4:
                icon = QIcon("assets/wifi_black_24dp.svg")
<<<<<<< HEAD

=======
            
>>>>>>> ef201362b9151a380c985dd5acef6b7b21de82f9
            # Following are Mbed Devices 
            elif index.data(Qt.DisplayRole) == 10: 
                icon = QIcon("assets/sensors_off_black_24dp.svg")
            elif index.data(Qt.DisplayRole) == 11: 
                icon = QIcon("assets/usb_black_24dp.svg")  # Mbed USB Device 
            elif index.data(Qt.DisplayRole) == 13:
                icon = QIcon("assets/cable_black_24dp.svg")
            elif index.data(Qt.DisplayRole) == 14:
                icon = QIcon("assets/wifi_black_24dp.svg")
<<<<<<< HEAD
=======

>>>>>>> ef201362b9151a380c985dd5acef6b7b21de82f9
        icon.paint(painter, option.rect, Qt.AlignCenter)

    def setIcon(self, darkmode):
        self.darkmode = darkmode

class StatusIconDelegate(QStyledItemDelegate):
    """
    Show the appropriate status icon.
    """
    def __init__(self):
        super().__init__()

    def paint(self, painter, option, index):
        if self.darkmode == True:
            if index.data(Qt.DisplayRole) == True:
                icon = QIcon("assets/link_white_24dp.svg")
            elif index.data(Qt.DisplayRole) == False:
                icon = QIcon("assets/link_off_white_24dp.svg")
        else:
            if index.data(Qt.DisplayRole) == True:
                icon = QIcon("assets/link_black_24dp.svg")
            elif index.data(Qt.DisplayRole) == False:
                icon = QIcon("assets/link_off_black_24dp.svg")
        icon.paint(painter, option.rect, Qt.AlignCenter)
    
    def setIcon(self, darkmode):
        self.darkmode = darkmode

class FloatValidatorDelegate(QItemDelegate):
    """
    A delegate that validates float input from a table cell.
    """
    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        linedit = QLineEdit(parent)
        linedit.setAlignment(Qt.AlignCenter)
        validator = QDoubleValidator(self, decimals=3)
        validator.setNotation(QDoubleValidator.StandardNotation)
        locale = QLocale("en")
        locale.setNumberOptions(QLocale.IncludeTrailingZeroesAfterDot)
        validator.setLocale(locale)
        linedit.setValidator(validator)
        return linedit

    def setModelData (self, editor, model, index):
        '''
        Change the underlying data model by updating the value as a float.
        '''
        value = float(editor.text())        
        model.setData(index, value, Qt.EditRole)

class StringDelegate(QItemDelegate):
    """
    A delegate that returns a string from a line edit.
    """
    def __init__(self):
        super().__init__()

    def createEditor(self, parent, option, index):
        linedit = QLineEdit(parent)
        linedit.setAlignment(Qt.AlignCenter)
        return linedit

    def setModelData (self, editor, model, index):
        '''
        Update the edited text in the model after validation by checking the string length is greater than zero.
        '''
        value = editor.text()
        if len(value) != 0:
            model = index.model()
            model.setData(index, value, Qt.EditRole)

class ComboBoxDelegate(QStyledItemDelegate):
    """
    A delegate that displays a combobox populated with the supplied items.
    """
    def __init__(self, items):
        super().__init__()
        self.items = items

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.currentIndexChanged.connect(self.commit_editor)
        editor.addItems(self.items)
        return editor

    def commit_editor(self):
        editor = self.sender()
        self.commitData.emit(editor)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentIndex(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        value = index.model().data(index)
        text = self.items[value]
        option.text = text
        option.displayAlignment = Qt.AlignCenter
        QApplication.style().drawControl(QStyle.CE_ItemViewItem, option, painter)

class ColouredBackgroundDelegate(QStyledItemDelegate):
    """
    A delegate that displays a coloured square.
    """
    def __init__(self, parent=None):
        super(ColouredBackgroundDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        painter.save()
        color = index.data(Qt.DecorationRole)
        painter.fillRect(option.rect, QColor(color))
        painter.restore()
