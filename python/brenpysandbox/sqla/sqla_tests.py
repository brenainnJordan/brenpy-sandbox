'''
Created on 17 Sep 2018

@author: Bren
'''

import os
import sys
import math
import subprocess
from collections import OrderedDict

import sqlalchemy as sqla
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import scandir

from PySide import QtGui, QtCore
from sqla_qt_tests import DirEntryModel
from re import search

Base = declarative_base()

print "declaring DirEntry..."


class Filters():
    """expanded sql alchemy comparisons"""
    @staticmethod
    def contains(attr, value):
        return attr.like("%{0}%".format(value))

    @staticmethod
    def wildcard(attr, value):
        return attr.like(value.replace("*", "%"))

    @staticmethod
    def search(attr, value):

        search_terms = [
            "%{0}%".format(
                i.replace("*", "%")
            ) for i in value.split(" ")
        ]

        print search_terms

        for i in search_terms:
            if attr.like(i):
                return True

        return False
        return any([
            attr.like(i) for i in search_terms
        ])


SQL_COMPARISONS = OrderedDict([
    ("", None),
    #     ("contains", "__contains__"), # NotImplementedError
    ("like", "like"),
    ("==", "__eq__"),
    ("!=", "__ne__"),
    (">", "__gt__"),
    (">=", "__ge__"),
    ("<", "__lt__"),
    ("<=", "__le__"),
    ("is", "is_"),
    ("in", "in_"),
    #     ("not_in", "not_in"), # NotImplementedError
    ("ilike", "ilike"),
    # ("is not", "is_not"), # NotImplementedError
]
)

NUMERIC_COMPARISONS = OrderedDict([
    ("", None),
    ("==", "__eq__"),
    ("!=", "__ne__"),
    (">", "__gt__"),
    (">=", "__ge__"),
    ("<", "__lt__"),
    ("<=", "__le__"),
    ("is", "is_"),
])

STRING_COMPARISONS = OrderedDict([
    ("", None),
    ("==", "__eq__"),
    ("!=", "__ne__"),
    ("contains", Filters.contains),
    ("wildcard", Filters.wildcard),
    ("like", "like"),
])


COMPARISON_METHODS = OrderedDict([
    ("contains", Filters.contains),
    ("wildcard", Filters.wildcard),
    ("search", Filters.search),
])


class DirEntry(Base):
    __tablename__ = "dirs"

    id = sqla.Column(sqla.Integer, primary_key=True, unique=True)
    name = sqla.Column(sqla.String, unique=False)
    path = sqla.Column(sqla.String, unique=True)
    parent_path = sqla.Column(sqla.String, unique=False)
    is_file = sqla.Column(sqla.Boolean, unique=False)
    is_dir = sqla.Column(sqla.Boolean, unique=False)
    size = sqla.Column(sqla.Integer, unique=False)
    sizeKB = sqla.Column(sqla.Float, unique=False)
    sizeMB = sqla.Column(sqla.Float, unique=False)
    sizeGB = sqla.Column(sqla.Float, unique=False)

    def __init__(
        self,
        name,
        parent_path,
        is_file,
        is_dir,
    ):
        self.name = name

        self.parent_path = parent_path
        self.path = os.path.join(self.parent_path, self.name)
        self.is_file = is_file
        self.is_dir = is_dir

        self.size = os.path.getsize(self.path)
        self.sizeKB = self.size / 1024.0
        self.sizeMB = self.sizeKB / 1024.0
        self.sizeGB = self.sizeMB / 1024.0

    def __repr__(self):
        return "DirEntry(name={0}, parent_path={1}, is_file={2}, is_dir={3}".format(
            self.name, self.parent_path, self.is_file, self.is_dir
        )


# for i in session.query(DirEntry).all():
#     print i

class DirDb(object):
    def __init__(self):
        self._root_dir = ""
        self._engine = sqla.create_engine('sqlite:///:memory:', echo=False)

        Base.metadata.create_all(bind=self._engine)

        self._inspector = sqla.inspect(self._engine)
        self._session = None

    def session(self):
        return self._session

    def startSession(self):
        # create session
        Session = sessionmaker()
        Session.configure(bind=self._engine)
        self._session = Session()

    def setRootDir(self, root_dir):
        self._root_dir = root_dir

        if self._session is None:
            self.startSession()

        print "Clearing entries..."
        self._session.query(DirEntry).delete()

        print "Creating entries..."

        for root, subdirs, filenames in scandir.walk(self._root_dir):
            for subdir in subdirs:
                entry = DirEntry(
                    subdir,
                    parent_path=root,
                    is_file=False,
                    is_dir=True,
                )
                self._session.add(entry)

            for filename in filenames:
                entry = DirEntry(
                    filename,
                    parent_path=root,
                    is_file=True,
                    is_dir=False,
                )
                self._session.add(entry)

        print "Comitting..."

        self._session.commit()

    def getColumns(self, table_cls):
        return self._inspector.get_columns(table_cls.__tablename__)

    def getColumnNames(self, table_cls):
        return [i["name"] for i in self.getColumns(table_cls)]


class Signal(object):
    """Basic Qt-style Signal class
    """

    def __init__(self):
        self._methods = []

    def connect(self, method):
        self._methods.append(method)

    def emit(self):
        for method in self._methods:
            method()


class DbUserQuery(object):
    """Query class with user-friendly Db searching and filter functionality.
    Presents results to user per page.
    """

    def __init__(self, db, table_cls):
        self._db = db
        self._table_cls = table_cls

        self._order = sqla.asc
        self._order_column = self._table_cls.id

        self._filters = []
        self._searches = []
        self._data = []
        self._page = 0
        self._results_per_page = 20

        self._data_updated = Signal()

    def db(self):
        return self._db

    def table(self):
        return self._table_cls

    def data(self):
        return self._data

    def data_updated(self):
        return self._data_updated

    def add_filter(self, filter_cls):
        self._filters.append(filter_cls)
        filter_cls.data_updated().connect(self.update_data)
        self.update_data()

    def remove_filter(self, filter_cls):
        self._filters.remove(filter_cls)
        self.update_data()

    def filters(self):
        return self._filters

    def call_filters(self):
        if not len(self._filters):
            print "no filters"
            return [True]

        return [i.filter() for i in self._filters]

    def add_search(self, search_cls):
        self._searches.append(search_cls)
        search_cls.data_updated().connect(self.update_data)
        self.update_data()

    def remove_search(self, search_cls):
        self._searches.remove(search_cls)
        self.update_data()

    def searches(self):
        return self._searches

    def call_searches(self):
        if not len(self._searches):
            print "no searches"
            return [True]

        return self._searches[0].search()

        return [j for i in self._searches for j in i.search()]

    def resultsPerPage(self):
        return self._results_per_page

    def setResultsPerPage(self, results_per_page):
        if results_per_page > 0:
            self._results_per_page = results_per_page

        self.update_data()

    def setPage(self, page):
        if page >= self.pageCount():
            print "page is greater than page count"
            return

        self._page = page
        self.update_data()

    def resultCount(self):
        return self._db.session().query(self._table_cls).count()

    def pageCount(self):
        return math.ceil(
            float(self.resultCount()) / self._results_per_page
        )

    def firstPageResultIndex(self):
        return self._page * self._results_per_page

    def lastPageResultIndex(self):
        index = self.firstPageResultIndex() + self._results_per_page - 1

        if index < self.resultCount():
            return index
        else:
            return self.resultCount() - 1

    def setOrder(self, order):
        accepted_values = sqla.asc, sqla.desc

        if order not in accepted_values:
            raise TypeError("order must be one of: {}".format(accepted_values))

        self._order = order

        self.update_data()

    def order(self):
        return self._order

    def setAscendingOrder(self, value):
        if value:
            self.setOrder(sqla.asc)
        else:
            self.setOrder(sqla.desc)

    def setDecendingOrder(self, value):
        self.setAscendingOrder(not value)

    def setOrderColumn(self, column_index):
        column_name = self._db.getColumnNames(self._table_cls)[
            column_index]
        self._order_column = getattr(self._table_cls, column_name)
        self.update_data()

    def update_data(self):
        if not self._db.session():
            return

        print "updating query data"

        filters = self.call_filters()
        searches = self.call_searches()

#         search_terms = ["%.txt%", "%_1%", "%_2%"]
#         columns = [getattr(DirEntry, i) for i in ["name", "parent_path"]]
#
#         print columns

#         test_searches = [
#             sqla.or_(*[
#                 #                 DirEntry.name.like(i)
#                 column.like(i)
#                 for column in columns
#             ]) for i in search_terms
#         ]
#         print searches
#         print "test: ", searches == test_searches

#         searches = [True, True]

        self._data = self._db.session().query(
            self._table_cls
        ).filter(
            #             sqla.or_(*searches)
            *searches
        ).filter(
            *filters
        ).order_by(
            self._order(self._order_column)
        ).slice(
            self.firstPageResultIndex(),
            self.lastPageResultIndex() + 1
        ).all()

        self._data_updated.emit()


class DbFilter(object):
    def __init__(self, db, table_cls):
        self._db = db
        # TODO: check table is in db
        self._table_cls = table_cls

        self._column = None
        self._comparison = None
        self._method = None
        self._value = None

        self._data_updated = Signal()

    def _debug(self, msg):
        print msg

    def data_updated(self):
        return self._data_updated

    def available_columns(self):
        return self._db.getColumnNames(self._table_cls)

    def set_column(self, column_name):
        if column_name not in self.available_columns() + [None]:
            raise NameError(
                "Column name not found: {0}".format(column_name))

        self._column = column_name
        self._data_updated.emit()

    def set_comparison(self, comparison_name):
        if comparison_name not in SQL_COMPARISONS:
            if comparison_name in COMPARISON_METHODS:
                self._comparison = None
                self.set_method(comparison_name)
                return
            else:
                raise NameError(
                    "Comparison name not found: {0}".format(comparison_name))

        self._comparison = SQL_COMPARISONS[comparison_name]
        self._method = None
        self._data_updated.emit()

    def set_method(self, method_name):
        if method_name not in COMPARISON_METHODS:
            if method_name in SQL_COMPARISONS:
                self._method = None
                self.set_comparison(method_name)
                return
            else:
                raise NameError(
                    "Comparison name not found: {0}".format(method_name))

        self._method = COMPARISON_METHODS[method_name]
        self._comparison = None
        self._data_updated.emit()

    def set_value(self, value):
        # TODO value checks
        if value == "":
            value = None

        self._value = value
        self._data_updated.emit()

    def filter(self):
        """
        Equivalent to:

        DirEntry.is_file == True
        eg. query().filter(dir_db_filter.filter())

        if any value is None, return True to query all results
        ie. query().filter(True)

        """

        if any([
            self._column is None,
            self._value is None
        ]):
            self._debug("no column or value")
            return True

        column_object = getattr(self._table_cls, self._column)

        if self._comparison is not None:
            return getattr(column_object, self._comparison)(self._value)

        elif self._method is not None:
            return self._method(column_object, self._value)

        else:
            self._debug("no comparison or method")
            return True


class DbSearch(object):
    """Query for broad or general searches"""

    def __init__(self, db_user_query):
        self._db_user_query = db_user_query

        self._columns = []
        self.set_all_columns()

        self._search_terms = []
        self._filters = []
        self._data_updated = Signal()

    def _debug(self, msg):
        print msg

    def data_updated(self):
        return self._data_updated

    def db(self):
        return self._db_user_query.db()

    def table(self):
        return self._db_user_query.table()

    def set_all_columns(self):
        self._columns = self.db().getColumnNames(self.table())

    def set_columns(self, columns):
        if columns is None:
            self.set_all_columns()
        else:
            for column in columns:
                if column not in self.db().getColumnNames(self.table()):
                    raise NameError("Column not found: {0}".format(column))

            self._columns = list(columns)

#         self.update_filters()
        self._data_updated.emit()

    def search_terms(self):
        return self._search_terms

    def set_search_str(self, search_str):
        self._search_terms = [
            #             "%{0}%".format(
            #                 i.replace("*", "%")
            #             ) for i in search_str.split(" ")
            i.replace("*", "%") for i in search_str.split(" ")
        ]

#         self.update_filters()
        self._data_updated.emit()

    def clear_filters(self):
        for filter_cls in self._filters:
            self._db_user_query.remove_search(filter_cls)

        self._filters = []
        self._data_updated.emit()

    def search(self):
        """For each search term check if any column is similar"""
        if not len(self._columns) or not len(self._search_terms):
            return [True]

        print "column names: ", self._columns

        columns = [
            getattr(self.table(), column) for column in self._columns
        ]

        print "column objects: ", columns

        print self._search_terms

        return [
            sqla.or_(*[
                column.like(search_term) for column in columns
            ]) for search_term in self._search_terms
        ]

#     def update_filters(self):
#
#         self.clear_filters()
#
#         for column in self._columns:
#             for search_term in self._search_terms:
#                 filter_cls = DbFilter(self.db(), self.table())
#                 filter_cls.set_column(column)
#                 filter_cls.set_value(search_term)
#                 filter_cls.set_comparison("like")
#                 self._filters.append(filter_cls)
#                 self._db_user_query.add_search(filter_cls)

# QT classes ---


class DirEntryModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        """
        TODO: debugger class
        """
        super(DirEntryModel, self).__init__(parent)

        self._query_data = []

        self._dir_db = DirDb()
        self._query = DbUserQuery(self._dir_db, DirEntry)
        self._query.data_updated().connect(self.update_query_data)

        self._horizontal_headers = self._dir_db.getColumnNames(DirEntry)

    def db(self):
        return self._dir_db

    def query(self):
        return self._query

    def headerData(self, section, orientation, role):

        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section < len(self._horizontal_headers):
                    return self._horizontal_headers[section]
                else:
                    return "other"
            elif orientation == QtCore.Qt.Vertical:
                if section < len(self._query_data):
                    return self._query_data[section].id
                else:
                    return "#"

    def rowCount(self, *args, **kwargs):
        """ called by view to know how many rows to create
        """
        return len(self._query_data)

    def columnCount(self, *args, **kwargs):
        return len(self._horizontal_headers)

    def index(self, row, column, *args, **kwargs):
        """
            ** Overide Method **

            Create QModelIndex representing desired model item.

            The term "index" in this case is not used as the index of a list such as an integer
            "index" refers to a QModelIndex class instance, which contains a pointer to our data.
            The data in this case is a Node class instance.

            http://doc.qt.io/qt-5/qabstractitemmodel.html#createIndex

            I guess a QModelIndex is a more portable/abstract represenation of this model instance

            :TODO find out when this is called?
        """

        data = self._query_data[row]

        if not data:  # i mean why not?
            return QtCore.QModelIndex()  # return empty index

        # create new index with pointer to desired Node
        index = self.createIndex(row, column, data)
        return index

    def data(self, index, role):
        """
            called by view when populating item field

            http://doc.qt.io/qt-5/qt.html#ItemDataRole-enum

        """

        data = index.internalPointer()

        row = index.row()
        column = index.column()

        value = getattr(data, self._horizontal_headers[column])

        if role in [
            QtCore.Qt.DisplayRole,
            QtCore.Qt.ToolTipRole,
        ]:
            return value

    def setData(self, *args, **kwargs):
        """ called when user tries to edit an item
            must return true if successful and false if not
            if returned false, item stays as is!
        """
        return False

    def update_query_data(self):
        self.setQueryData(self.query().data())

    def setQueryData(self, query_data):

        # remove rows
        if self.rowCount() > 0:
            print "removing rows"
            self.beginRemoveRows(QtCore.QModelIndex(), 0, self.rowCount() - 1)
            self._query_data = []
            self.endRemoveRows()

        # send signal to views that were are about to modify the following ros
        # (parent, first row, last row)
        print "adding rows"
        print len(query_data)
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(query_data) - 1)
        self._query_data = query_data
        self.endInsertRows()

        # TODO check this:
#         self.dataChanged.emit(
#             self.index(0, 0),
#             self.index(self.rowCount() - 1, self.columnCount() - 1)
#         )

    def setRootDir(self, root_dir):
        self._dir_db.setRootDir(root_dir)
        self._query.setPage(0)

    def flags(self, *args, **kwargs):
        """ hard-coded item flags
            index is ignored
            this would probably be settable as normal if *args and **kwargs were passed into __init__
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


class DbTableView(QtGui.QTableView):
    def __init__(self, *args, **kwrags):
        super(DbTableView, self).__init__(*args, **kwrags)

        self._print_debug_messages = True

        self.horizontalHeader().sortIndicatorChanged.connect(self.sortColumn)
        self.horizontalHeader().sectionClicked.connect(self.columnClicked)
        self.horizontalHeader().setSortIndicator(0, QtCore.Qt.SortOrder.AscendingOrder)

    def _debug(self, msg):
        if self._print_debug_messages:
            print msg

    def columnClicked(self, column_logical_index):
        self._debug("column clicked")

        if not isinstance(self.model(), DirEntryModel):
            return

        self.model().query().setOrderColumn(column_logical_index)

    def sortColumn(self, column, order, *args, **kwargs):
        """
        params:
            column (int): column logicalIndex
            order (PySide.QtCore.Qt.SortOrder): order direction

        ie PySide.QtCore.Qt.SortOrder.AscendingOrder
        or PySide.QtCore.Qt.SortOrder.DescendingOrder

        """
        self._debug("column order changed: {}".format(order))

        if not isinstance(self.model(), DirEntryModel):
            return

        if order is QtCore.Qt.SortOrder.AscendingOrder:
            self.model().query().setAscendingOrder(True)
        else:
            self.model().query().setAscendingOrder(False)


class NumericComparisonWidget(QtGui.QWidget):
    def __init__(self):
        pass


class DbSearchWidget(QtGui.QWidget):
    def __init__(self, db_user_query, columns=None, parent=None):
        """
        Params:
            columns: (list) list of columns to query
        """
        super(DbSearchWidget, self).__init__(parent=parent)

        self._query = db_user_query
        self._search = DbSearch(db_user_query)
        self._search.set_columns(columns)

        self._create_widgets()
        self._connect_widgets()

    def search(self):
        return self._search

    def _create_widgets(self):
        self._lyt = QtGui.QHBoxLayout()
        self.setLayout(self._lyt)

        self._columns_menu = DbColumnMenu(
            self._query.db(),
            self._query.table()
        )
        self._columns_menu.triggered.connect(self.update_columns)

        self._columns_btn = QtGui.QPushButton("...")
        self._columns_btn.setMenu(self._columns_menu)
        self._value_edit = QtGui.QLineEdit()

        self._lyt.addWidget(self._columns_btn)
        self._lyt.addWidget(self._value_edit)

    def _connect_widgets(self):
        self._value_edit.textChanged.connect(
            self.update_value
        )

    def update_columns(self):
        columns = self._columns_menu.selected()
        self._search.set_columns(columns)

    def update_value(self):
        self._search.set_search_str(
            self._value_edit.text()
        )


class DirDbFilterWidget(QtGui.QWidget):
    def __init__(self, db, table_cls, parent=None):
        super(DirDbFilterWidget, self).__init__(parent=parent)

        self._filter = DbFilter(db, table_cls)

        self._create_widgets()
        self._connect_widgets()

    def filter(self):
        return self._filter

    def _create_widgets(self):
        self._lyt = QtGui.QHBoxLayout()
        self.setLayout(self._lyt)

        self._column_combo = QtGui.QComboBox()
        self._comparison_combo = QtGui.QComboBox()
        self._value_edit = QtGui.QLineEdit()

        self._populate_column_combo()
        self._populate_comarison_combo()

        self._lyt.addWidget(self._column_combo)
        self._lyt.addWidget(self._comparison_combo)
        self._lyt.addWidget(self._value_edit)

    def _populate_column_combo(self):
        # TODO make model for this
        self._column_combo.clear()
        self._column_combo.addItem("")
        self._column_combo.addItems(self._filter.available_columns())

    def _populate_comarison_combo(self):
        # TODO do we need a model for this?
        self._comparison_combo.clear()

        self._comparison_combo.addItems(
            SQL_COMPARISONS.keys() + COMPARISON_METHODS.keys()
        )

    def _connect_widgets(self):
        self._column_combo.currentIndexChanged.connect(
            self.update_column
        )

        self._comparison_combo.currentIndexChanged.connect(
            self.update_comparison
        )

        self._value_edit.textChanged.connect(
            self.update_value
        )

    def update_column(self):
        column = self._column_combo.currentText()
        if column == "":
            column = None

        self._filter.set_column(column)

    def update_comparison(self):
        self._filter.set_comparison(
            self._comparison_combo.currentText()
        )

    def update_value(self):
        self._filter.set_value(
            self._value_edit.text()
        )


class DbColumnMenu(QtGui.QMenu):
    """Menu with checkable columns"""

    def __init__(self, db, table_cls, name=None, parent=None):
        if name is None:
            name = "columns"

        super(DbColumnMenu, self).__init__(name, parent=parent)
        self._db = db
        self._table_cls = table_cls

        self.persist = False

        self.create_actions()

        self.triggered.connect(self.trigger)

    def trigger(self):
        if self.persist:
            self.popup(self.pos())

    def columns(self):
        return self._db.getColumnNames(self._table_cls)

    def selected(self):
        return [
            action.text() for action in self.actions() if action.isChecked()
        ]

    def create_actions(self):
        for column in self.columns():
            self.addAction(
                QtGui.QAction(column, self, checkable=True)
            )


class DirDbWidget(QtGui.QWidget):
    """
    Ideas:

    Queries list widget
    "add query" choose from a list eg ("MB >", "is dir", "is file", "KB <", "name contains", "path contains", "path token ==")
    internally each contains data type, and query method eg. (("MB >", float, dir_entry.mb_gt) or something?
    ("path_token ==", int, str, dir_entry.something)

    Save queries into preset list eg.("Flac files by Devin Townsend")

    """

    def __init__(self, parent=None):
        super(DirDbWidget, self).__init__(parent=parent)
        self.main_lyt = QtGui.QVBoxLayout()
        self.setLayout(self.main_lyt)

        # create database and model
        self.db_model = DirEntryModel()

        self.create_widgets()

        self.db_model.setRootDir(
            r"F:\dev\python\standalone_tools\sandbox\sqla\test_dir"
        )
#         self.db_model.setRootDir(
#             r"F:\Jobs"
#         )
#         self.db_model.setPage(1)
        self.connect_widgets()

    def test_filter_widgets(self):
        # TODO: is this convoluted?
        self._test_filter_widget = DirDbFilterWidget(
            self.db_model.db(), DirEntry
        )

        self.db_model.query().add_filter(
            self._test_filter_widget.filter()
        )

        self.main_lyt.addWidget(self._test_filter_widget)

        # second filter test
        self._test_filter_widget_2 = DirDbFilterWidget(
            self.db_model.db(), DirEntry
        )

        self.db_model.query().add_filter(
            self._test_filter_widget_2.filter()
        )

        self.main_lyt.addWidget(self._test_filter_widget_2)

        # search test
        self._test_search_widget_1 = DbSearchWidget(
            self.db_model.query(), columns=["name"]
        )

        self.db_model.query().add_search(
            self._test_search_widget_1.search()
        )

        self.main_lyt.addWidget(self._test_search_widget_1)

    def create_widgets(self):
        self.root_dir_label = QtGui.QLabel("Root")
        self.root_dir_edit = QtGui.QLineEdit(self)
        self.root_dir_browse = QtGui.QPushButton("Browse")
        self.root_dir_update = QtGui.QPushButton("Update")
        self.root_dir_lyt = QtGui.QHBoxLayout()

        self.root_dir_lyt.addWidget(self.root_dir_label)
        self.root_dir_lyt.addWidget(self.root_dir_edit)
        self.root_dir_lyt.addWidget(self.root_dir_browse)
        self.root_dir_lyt.addWidget(self.root_dir_update)
        self.main_lyt.addLayout(self.root_dir_lyt)

        self.results_label = QtGui.QLabel("Results per page")
        self.results_spin = QtGui.QSpinBox()
        self.results_spin.setValue(self.db_model.query().resultsPerPage())
        self.results_lyt = QtGui.QHBoxLayout()

        self.results_lyt.addWidget(self.results_label)
        self.results_lyt.addWidget(self.results_spin)

        self.main_lyt.addLayout(self.results_lyt)

        self.test_filter_widgets()

#         self.table_view = QtGui.QTableView()
        self.table_view = DbTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.setModel(self.db_model)
        self.main_lyt.addWidget(self.table_view)

        self.page_label = QtGui.QLabel("Page")
        self.page_spin = QtGui.QSpinBox()
        self.page_spin.setMinimum(0)
        self.page_spin.setMaximum(0)
        self.page_lyt = QtGui.QHBoxLayout()

        self.page_lyt.addWidget(self.page_label)
        self.page_lyt.addWidget(self.page_spin)

        self.main_lyt.addLayout(self.page_lyt)

    def connect_widgets(self):
        self.root_dir_browse.clicked.connect(self.browse_for_root_dir)
        self.root_dir_update.clicked.connect(self.update_root_dir)
        self.results_spin.valueChanged.connect(self.update_results_per_page)
        self.page_spin.valueChanged.connect(self.update_page_number)

        self.table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.table_view.customContextMenuRequested.connect(
            self.context_menu_handler)

    def context_menu_handler(self, position):
        sl_ids = self.table_view.selectedIndexes()
        for i in sl_ids:
            print i

        self.dir_context_menu(position)

    def dir_context_menu(self, position):
        menu = QtGui.QMenu(self)
        open_location_action = menu.addAction('Open location')

        action = menu.exec_(self.table_view.mapToGlobal(position))
        if action == open_location_action:
            self.open_location()

    def open_location(self):
        sl_ids = self.table_view.selectedIndexes()
        dir_entry = sl_ids[0].internalPointer()

        subprocess.Popen(r'explorer /select,"{0}"'.format(dir_entry.path))

    def browse_for_root_dir(self):
        root_dir = QtGui.QFileDialog.getExistingDirectory()
        self.root_dir_edit.setText(root_dir)
        self.update_root_dir()

    def update_root_dir(self):
        root_dir = self.root_dir_edit.text()

        if not os.path.exists(root_dir):
            print "ain't no path: ", root_dir
            return

        self.db_model.setRootDir(root_dir)

        self.update_page_spin()

    def update_page_spin(self):
        self.page_spin.setMaximum(self.db_model.query().pageCount() - 1)

    def update_page_number(self):
        page = self.page_spin.value()
        self.db_model.query().setPage(page)

    def update_results_per_page(self):
        results_per_page = self.results_spin.value()
        self.db_model.query().setResultsPerPage(results_per_page)
        self.update_page_spin()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    gui = DirDbWidget()
    gui.show()

#     query_data = session.query(DirEntry).slice(2, 5).all()
#
#     gui = QtGui.QTableView()
#     model = DirEntryModel()
#
#     gui.setModel(model)
#     gui.show()
#
#     model.setQueryData(query_data)

    sys.exit(app.exec_())
