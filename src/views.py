from PySide6.QtWidgets import QTableView, QHeaderView
from src.delegates import CheckBoxDelegate, ConnectionIconDelegate, StatusIconDelegate, FloatValidatorDelegate, StringDelegate


import logging
import sys

log = logging.getLogger(__name__)

class DeviceTableView(QTableView):

    def __init__(self, configuration, data=[], parent=None):
        super(DeviceTableView, self).__init__(parent)
        self.configuration = configuration
        self.darkMode = self.configuration["global"]["darkMode"]
        self.setSelectionBehavior(self.SelectRows)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)

        self.nameCheckBoxDelegate = CheckBoxDelegate("name")
        self.stringDelegate = StringDelegate()
        self.connectionIconDelegate = ConnectionIconDelegate() 
        self.connectionIconDelegate.setIcon(self.darkMode)
        self.statusIconDelegate = StatusIconDelegate()
        self.statusIconDelegate.setIcon(self.darkMode) 

        self.setItemDelegateForColumn(0, self.nameCheckBoxDelegate)
        self.setItemDelegateForColumn(1, self.stringDelegate)
        self.setItemDelegateForColumn(2, self.connectionIconDelegate)
        self.setItemDelegateForColumn(3, self.stringDelegate)
        self.setItemDelegateForColumn(4, self.statusIconDelegate)

class AcquisitionTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super(AcquisitionTableView, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)

        self.channelCheckBoxDelegate = CheckBoxDelegate("channel")
        self.stringDelegate = StringDelegate()
        self.floatValidatorDelegate = FloatValidatorDelegate()
        self.checkBoxDelegate = CheckBoxDelegate()

        self.setItemDelegateForColumn(0, self.channelCheckBoxDelegate)
        self.setItemDelegateForColumn(1, self.stringDelegate)
        self.setItemDelegateForColumn(2, self.stringDelegate)
        self.setItemDelegateForColumn(3, self.floatValidatorDelegate)
        self.setItemDelegateForColumn(4, self.floatValidatorDelegate)
        self.setItemDelegateForColumn(5, self.checkBoxDelegate)

class ChannelsTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super(ChannelsTableView, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        
        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.hide()
        horizontalHeader.setStretchLastSection(True)

        self.channelCheckBoxDelegate = CheckBoxDelegate()

        self.setItemDelegateForColumn(0, self.channelCheckBoxDelegate)

class ColourPickerTableView(QTableView):

    def __init__(self, data=[], parent=None):
        super(ColourPickerTableView, self).__init__(parent)
        self.setSelectionMode(self.SingleSelection)
        self.setShowGrid(False)
        
        verticalHeader = self.verticalHeader()
        verticalHeader.hide()
        verticalHeader.setDefaultSectionSize(25)
        horizontalHeader = self.horizontalHeader()
        horizontalHeader.hide()
        horizontalHeader.setDefaultSectionSize(25)






        