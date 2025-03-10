"""QtWidgets that either induce or respond to user-initiated procedural resizing events.

** WIP **

migrate code from bpQtWidgets

refactor to be more generic using concept of "procedural size" instead of collapsing/expanding/adapting etc.


stuff to change/implement (mark each one as done as/when completed)


proceduralSizeSplitter

ABOUT_TO_PROCEDURALLY_RESIZE
PROCEDURALLY_RESIZED


_procedural_size = QtSize(self.size())


resizeEvent()
- update procedural size to new size


child_about_to_procedurally_resize():
cache current sizes


child_procedurally_resized():
update cached sizes with new child procedural size
set procedural size
if procedural size is greater than maximum size or less than minimum size then adjust accordingly
...(for example if parent widget is collapsed)
resize
emit (push up chain)
set sizes (after parents have resized)



proceduralSizeSplitterWidget

ABOUT_TO_PROCEDURALLY_RESIZE
PROCEDURALLY_RESIZED

_procedural_size = QtSize(self.size())

resizeEvent()
- update procedural size to new size

collapse()
self._expanded_size = self.size()
set fixed height of splitter to 0
emit()

expand()
if orientation is horizontal:
self._procedural_size.height = self._expanded_size.height()
emit()


splitter_about_to_procedurally_resize():
if collapsed...
do nothing?

otherwise...
emit about to procedurally resize


splitter_procedurally_resized():
if collapsed...
make sure splitter fixed size is still 0
return (don't emit)

otherwise...
set procedural size
resize
emit (push up chain)



TODO !!! RETIRE THIS MODULE !!!


"""

import sys

try:
    from Qt import QtCore
    from Qt import QtWidgets
    from Qt import QtGui
except ImportError:
    print "[ WARNING ] Cannot find Qt library, using PySide2 instead"
    from PySide2 import QtCore
    from PySide2 import QtWidgets
    from PySide2 import QtGui

# QtCore.SIGNAL doesn't seem to exist
# TODO investigate why
try:
    from PySide.QtCore import SIGNAL
except ImportError:
    from PySide2.QtCore import SIGNAL

from brenpy.qt.core import bpQtCore
from brenpy.qt.core import bpQtWidgets

QT_WIDGET_MAX_SIZE = (16777215, 16777215)
QT_WIDGET_MAX_WIDTH = QT_WIDGET_MAX_SIZE[0]
QT_WIDGET_MAX_HEIGHT = QT_WIDGET_MAX_SIZE[1]


class BpResizingSplitter(bpQtWidgets.BpSplitter):
    """QSplitter subclass that resizes if the user drags the splitter handle beyond maximum height.
    TODO horizontal orientation
    """

    RESIZE_ALL_MODE = 0
    RESIZE_INDEX_ABOVE_MODE = 1

    # signals
    ABOUT_TO_RESIZE = QtCore.Signal(QtWidgets.QWidget)
    RESIZED = QtCore.Signal(QtWidgets.QWidget)
    UPDATE_CACHE_REQUEST = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(BpResizingSplitter, self).__init__(*args, **kwargs)

        self.setChildrenCollapsible(False)

        self._mode = None
        self._method = None

        # self.set_mode(self.RESIZE_ALL_MODE)
        self.set_mode(self.RESIZE_INDEX_ABOVE_MODE)
        self.setOpaqueResize(False)

        self.splitterMoved.connect(self._splitter_moved)

        # position caches
        self._cached_cursor_pos = None
        self._cached_splitter_pos = None
        self._cached_sizes = []

        self._adapt_enabled = True
        self._size_hint = 0

        self._size_managed = False

        self._is_root = True

    def is_root(self):
        return self._is_root

    def set_is_root(self, value):
        self._is_root = value == True

    def size_managed(self):
        """Return if this widgets size managed by a parent adaptive widget.
        """
        return self._size_managed

    def set_size_managed(self, value):
        self._size_managed = value == True

    def setChildrenCollapsible(self, value):
        """TODO override other set collapsible methods
        """
        if value:
            raise bpQtCore.BpQtError("Resizing splitter cannot have collapsible children")

        return True

    def addWidget(self, widget):
        super(BpResizingSplitter, self).addWidget(widget)

        # connect child widget
        if isinstance(widget, (BpCollapsibleWidget, BpResizingSplitter)):
            widget.ABOUT_TO_RESIZE.connect(self._child_about_to_resize)
            widget.RESIZED.connect(self._child_resized)
            widget.UPDATE_CACHE_REQUEST.connect(self.update_cache_full_stack)
            widget.set_size_managed(True)
            widget.set_is_root(False)

        self.set_size_hint_to_current()

    def update_cache_full_stack(self):

        if self.is_root():
            # if this is top most adaptive widget,
            # then cache all children recursively
            self.update_cache(recursive=True)
        else:
            # if this is not the top most adaptive widget,
            # then push the signal up the chain until it gets to the top
            # to avoid multiple recursive caches
            self.UPDATE_CACHE_REQUEST.emit()

        return True

    def update_height_range(self, recursive=True):
        if not self.adapt_enabled():
            return

        if recursive:
            for widget in self.widgets():
                if isinstance(widget, (BpCollapsibleWidget, BpResizingSplitter)):
                    widget.update_height_range(recursive=True)

        self.setMinimumHeight(self.get_minimum_height())
        self.setMaximumHeight(self.get_maximum_height())

    def size_hint(self):
        return self._size_hint

    def sizeHint(self):
        """Override size hint with procedurally set size hint.
        """
        size_hint = super(BpResizingSplitter, self).sizeHint()

        if self.orientation() == QtCore.Qt.Vertical:
            size_hint.setHeight(self._size_hint)
        else:
            size_hint.setWidth(self._size_hint)

        return size_hint

    def set_size_hint_to_current(self, recursive=False):
        """Set size hint to current widget size.
        """

        if not self.adapt_enabled():
            return

        if self.orientation() == QtCore.Qt.Vertical:
            self._size_hint = self.height()
        else:
            self._size_hint = self.width()

        if recursive:
            for widget in self.widgets():
                if isinstance(widget, (BpCollapsibleWidget, BpResizingSplitter)):
                    widget.set_size_hint_to_current(recursive=True)

    def adapt_enabled(self):
        return self._adapt_enabled

    def set_adapt_enabled(self, value, recursive=False):
        self._adapt_enabled = value == True

        if recursive:
            for widget in self.widgets():
                if isinstance(widget, (BpResizingSplitter, BpCollapsibleWidget)):
                    widget.set_adapt_enabled(value, recursive=True)

        return True

    def resizeEvent(self, event):
        """Reimplemented from base class to update caches.
        Called after resize has already taken place.
        """
        super(BpResizingSplitter, self).resizeEvent(event)

        # compare size hints after resize
        # print "size hints", self.get_widget_size_hints()

        self._cached_cursor_pos = None
        self._cached_splitter_pos = None

        if not self.adapt_enabled():
            return

        # self.cache_sizes()
        # self.set_size_hint_to_current(recursive=True)

    def update_cache(self, recursive=False):
        if not self.adapt_enabled():
            return

        self._cached_sizes = list(self.sizes())

        if recursive:
            for widget in self.widgets():
                if isinstance(widget, BpCollapsibleWidget):
                    if not widget.collapsed():
                        widget.update_cache(recursive=True)

                elif isinstance(widget, BpResizingSplitter):
                    widget.update_cache(recursive=True)

    def apply_cached_sizes(self, recursive=False):

        if recursive:
            for widget in self.widgets():
                if isinstance(widget, (BpResizingSplitter)):
                    widget.apply_cached_sizes(recursive=True)

                elif isinstance(widget, (BpCollapsibleWidget)):
                    if not widget.collapsed():
                        widget.apply_cached_expanded_heights_and_sizes(recursive=True)

        # set sizes last in case apply child sizes had any affect on splitter sizes
        self.setSizes(self._cached_sizes)

    def createHandle(self):
        handle = bpQtWidgets.BpSplitterHandle(self.orientation(), self)
        handle.MOUSE_PRESSED.connect(self.splitter_handle_pressed)
        handle.MOUSE_RELEASED.connect(self.splitter_handle_released)
        return handle

    def mode(self):
        return self._mode

    def set_mode(self, mode):
        """
        TODO checks
        :param mode:
        :return:
        """

        if mode == self.RESIZE_ALL_MODE:
            self._method = self._resize_all

        elif mode == self.RESIZE_INDEX_ABOVE_MODE:
            self._method = self._resize_above_index

        else:
            raise bpQtCore.BpQtError(
                "Mode not recognised: {}".format(mode)
            )

        self._mode = mode

    def splitter_handle_pressed(self):
        """Stuff
        It possibly indicates user is about to move a splitter,
        in which case cache the current position ready for handling.

        """

        # self._cached_cursor_pos =  QtGui.QCursor.pos()
        self._cached_cursor_pos = self.mapFromGlobal(QtGui.QCursor.pos())
        self._cached_splitter_pos = None
        self.update_cache()

    def splitter_handle_released(self):
        """Stuff

        Potentially indicates user is done moving a splitter,
        in which case reset caches.

        """

        self._cached_cursor_pos = None
        self._cached_splitter_pos = None
        self.update_cache()

    def moveSplitter(self, pos, index):
        print "moving splitter"
        res = super(BpResizingSplitter, self).moveSplitter(pos, index)
        return res

    def _splitter_moved(self, pos, index):
        """Determine resize actions based on user mouse input.

        Current splitter position and current mouse position are
        compared against cached values to determine user intention.

        """
        # get mouse position
        # self._current_cursor_pos = QtGui.QCursor.pos()
        self._current_cursor_pos = self.mapFromGlobal(QtGui.QCursor.pos())

        # events should ensure caches are up to date,
        # but just in case ensure we have at least some values to compare
        if self._cached_cursor_pos is None:
            self._cached_cursor_pos = self._current_cursor_pos

        if self._cached_splitter_pos is None:
            self._cached_splitter_pos = pos

        if self._cached_sizes is None:
            self.update_cache()

        if self._current_cursor_pos.y() == self._cached_cursor_pos.y():
            # mouse either hasn't moved or only moved horizontally
            return

        # call method defined by self._mode
        self._method(pos, index)

        # if not self.adapt_enabled():
        #     self.cache_sizes()
        #     self.set_size_hint_to_current(recursive=True)
        # else:
        #     pass

        return True

    def _resize_all(self, pos, index):
        """Stuff.

        :param pos:
        :param index:
        :return:
        """

        # compare positions and perform appropriate resize actions
        if pos != self._cached_splitter_pos:
            # splitter moving normally
            self._cached_splitter_pos = pos
            self._cached_cursor_pos = self._current_cursor_pos
            return

        elif all([
            self._current_cursor_pos.y() > self._cached_cursor_pos.y(),
            self._current_cursor_pos.y() > pos + self.handleWidth()
        ]):
            # user dragged handle beyond maximum limit
            # resize widget and adapt size of child widget above handle
            # while keeping other child widgets the same size

            delta = self._current_cursor_pos.y() - self._cached_cursor_pos.y()

            # temp cache sizes
            sizes = self.sizes()

            self.ABOUT_TO_RESIZE.emit()

            # resize
            if not self.size_managed():
                self.resize(
                    self.width(),
                    self.height() + delta
                )

            self.RESIZED.emit()

            # update sizes
            sizes[index - 1] = sizes[index - 1] + delta
            self.setSizes(sizes)

            self._cached_cursor_pos = self._current_cursor_pos
            self._cached_splitter_pos = pos + delta

        elif all([
            self._current_cursor_pos.y() < self._cached_cursor_pos.y(),
            self._current_cursor_pos.y() < pos  # - self.handleWidth()
        ]):
            # user dragged handle beyond minimum limit
            # resize widget and allow all child widgets to resize evenly

            delta = self._current_cursor_pos.y() - self._cached_cursor_pos.y()

            # temp cache sizes
            # sizes = self.sizes()

            # resize
            # making sure we don't shrink below minimum height
            if self.height() + delta >= self.get_minimum_height_hint():
                self.ABOUT_TO_RESIZE.emit()

                if not self.size_managed():
                    self.resize(
                        self.width(),
                        self.height() + delta
                    )

                self.RESIZED.emit()

            # update sizes
            # sizes[index-1] = sizes[index-1] + delta
            # self.setSizes(sizes)

            self._cached_cursor_pos = self._current_cursor_pos
            self._cached_splitter_pos = pos + delta

        else:
            print "stuff?"
            self._cached_cursor_pos = self._current_cursor_pos
            self._cached_splitter_pos = pos

    def _resize_above_index(self, pos, index):
        """Stuff.

        :param pos:
        :param index:
        :return:
        """

        # get widget above index
        widget = self.widgets()[index - 1]

        # calculate delta
        delta = self._current_cursor_pos.y() - self._cached_cursor_pos.y()

        # retrieve sizes before splitter was moved
        sizes = list(self._cached_sizes)

        # calculate new heights
        new_widget_height = sizes[index - 1] + delta

        # check new height is within limits
        if new_widget_height <= widget.minimumSizeHint().height():
            # print "too smol"
            new_widget_height = widget.minimumSizeHint().height()

        elif new_widget_height >= widget.maximumHeight():
            # print "too big"
            new_widget_height = widget.maximumHeight()

        # check delta
        widget_delta = new_widget_height - sizes[index - 1]

        # resize
        if widget_delta != 0:
            self.ABOUT_TO_RESIZE.emit(self)

            new_size = self.height() + widget_delta

            if not self.size_managed():
                self.resize(self.width(), new_size)

            self._size_hint = new_size

            self.RESIZED.emit(self)

        # update sizes
        sizes[index - 1] = new_widget_height
        self.setSizes(sizes)

        # update caches
        self._cached_cursor_pos = self._current_cursor_pos
        self._cached_sizes = list(sizes)

        return True

    def _child_about_to_resize(self, child_widget):
        """Cache new sizes.
        """
        if not self.adapt_enabled():
            return

        self.update_cache()

    def _child_resized(self, child_widget):
        """Do nothing?
        """
        if not self.adapt_enabled():
            return

        return None


class BpAutoResizingSplitter(BpResizingSplitter):

    def __init__(self, *args, **kwargs):
        super(BpAutoResizingSplitter, self).__init__(*args, **kwargs)

    def _child_about_to_resize(self, child_widget):
        super(BpAutoResizingSplitter, self)._child_about_to_resize(child_widget)

        if not self.adapt_enabled():
            return

        if isinstance(child_widget, BpCollapsibleWidget):
            print "DEBUG CHILD ABOUT TO RESIZE: {}".format(child_widget.label())
        else:
            print "DEBUG CHILD ABOUT TO RESIZE: {}".format(child_widget)

        self.ABOUT_TO_RESIZE.emit(self)

    def _child_resized(self, child_widget):
        """Respond to child resizing, by getting new size hint and adjust our own size hint to match.
        Emits signal to prompt parent to do the same.
        """
        super(BpAutoResizingSplitter, self)._child_resized(child_widget)

        if not self.adapt_enabled():
            return

        new_sizes = list(self._cached_sizes)
        child_index = self.widgets().index(child_widget)

        if self.orientation() == QtCore.Qt.Vertical:
            new_sizes[child_index] = child_widget.sizeHint().height()
        else:
            new_sizes[child_index] = child_widget.sizeHint().width()

        new_size = sum(new_sizes) + self.total_handle_width()

        self.update_height_range(recursive=False)

        if self.orientation() == QtCore.Qt.Vertical:
            self.resize(self.width(), new_size)
        else:
            self.resize(new_size, self.height())

        self._size_hint = new_size

        self.RESIZED.emit(self)

        self.setSizes(new_sizes)

        if isinstance(child_widget, BpCollapsibleWidget):
            print "DEBUG CHILD RESIZED: {}".format(child_widget.label())
        else:
            print "DEBUG CHILD RESIZED: {}".format(child_widget)

        return True


class BpCollapsibleWidget(
    # QtWidgets.QWidget
    QtWidgets.QFrame
):
    """

    *** WIP ***

    """

    # signals
    ABOUT_TO_RESIZE = QtCore.Signal(QtWidgets.QWidget)
    RESIZED = QtCore.Signal(QtWidgets.QWidget)
    UPDATE_CACHE_REQUEST = QtCore.Signal()

    def __init__(self, label="", parent=None, orientation=QtCore.Qt.Vertical):
        """
        TODO orientation
        """
        super(BpCollapsibleWidget, self).__init__(
            # orientation=QtCore.Qt.Vertical,
            parent=parent
        )

        self.setFrameStyle(self.Panel | self.Plain)

        self._orientation = orientation

        self._collapsed_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_ToolBarHorizontalExtensionButton
        )

        self._expanded_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_ToolBarVerticalExtensionButton
        )

        self._size_hint = 0
        self._expanded = True
        self._adapt_enabled = True
        self._size_managed = False

        self._cached_expanded_height = 0
        self._cached_expanded_minimum_height = 0
        self._cached_expanded_maximum_height = 0

        self._splitter_cached_expanded_minimum_height = 0
        self._splitter_cached_expanded_maximum_height = 0

        self.create_widgets()
        self.set_label(label)
        self.create_layout()
        self.connect_widgets()

        self._is_root = True

    def is_root(self):
        return self._is_root

    def set_is_root(self, value):
        self._is_root = value == True

    def update_cache_full_stack(self):

        if self.is_root():
            # if this is top most adaptive widget,
            # then cache all children recursively
            self.update_cache(recursive=True)
        else:
            # if this is not the top most adaptive widget,
            # then push the signal up the chain until it gets to the top
            # to avoid multiple recursive caches
            self.UPDATE_CACHE_REQUEST.emit()

        return True

    def size_managed(self):
        """Return if this widgets size managed by a parent adaptive widget.
        """
        return self._size_managed

    def set_size_managed(self, value):
        self._size_managed = value == True

    def orientation(self):
        return self._orientation

    def create_widgets(self):

        self._expand_btn = QtWidgets.QPushButton()
        self._expand_btn.setIcon(self._expanded_icon)
        self._expand_btn.setStyleSheet("Text-align:left")

        self._expand_btn.setFixedHeight(25)

        # self._splitter = BpSplitter()
        # self._splitter = BpResizingSplitter()
        self._splitter = BpAutoResizingSplitter()
        self._splitter.setOrientation(QtCore.Qt.Vertical)
        # self._splitter.setChildrenCollapsible(False)

        # set splitter resize to opaque to reduce heavy refreshes
        # self._splitter.setOpaqueResize(False)

        # turn off updating on resize
        # to avoid updating after collapsing
        # self._splitter.set_adapt_enabled(False)

    def connect_widgets(self):
        self._expand_btn.clicked.connect(self.toggle_collapse)

        # TODO use new methods
        self._splitter.ABOUT_TO_RESIZE.connect(self._splitter_about_to_resize)
        self._splitter.RESIZED.connect(self._splitter_resized)

    def label(self):
        return self._expand_btn.text()

    def set_label(self, label):
        self._expand_btn.setText(label)

    def create_layout(self):
        self._main_lyt = QtWidgets.QVBoxLayout()
        self.setLayout(self._main_lyt)

        self._main_lyt.addWidget(self._expand_btn)

        self._child_margin_lyt = QtWidgets.QVBoxLayout()
        self._child_margin_lyt.addWidget(self._splitter)

        self._main_lyt.addLayout(self._child_margin_lyt)

        # set margins and spacing
        self._main_lyt.setContentsMargins(0, 0, 0, 0)
        self._main_lyt.setSpacing(0)

        self._child_margin_lyt.setContentsMargins(5, 2, 2, 2)
        self._child_margin_lyt.setSpacing(0)

    def add_widget(self, widget):

        # if isinstance(widget, BpCollapsibleWidget):
        #
        #     widget.ABOUT_TO_RESIZE.connect(self._child_about_to_resize)
        #     widget.RESIZED.connect(self._child_resized)

        self._splitter.addWidget(widget)

        self.update_height_range()

        # print "DEBUG"
        # print "widget min height: ", widget.minimumHeight(), widget.minimumSizeHint().height()
        # print "splitter min height", self._splitter.minimumHeight(), self._splitter.minimumSizeHint().height()
        # print "self min height", self.minimumHeight(), self.minimumSizeHint().height()
        # print "lyt min height", self._main_lyt.minimumSize().height()
        # print "chd lyt min height", self._child_margin_lyt.minimumSize().height()

        return True

    def widgets(self):
        """Return splitter child widgets
        """
        return self._splitter.widgets()

    def set_size_hint_to_current(self, recursive=False):
        """Set size hint to current widget size.
        """

        if not self.adapt_enabled():
            return

        if self._orientation == QtCore.Qt.Vertical:
            self._size_hint = self.height()
        else:
            self._size_hint = self.width()

        if recursive:
            self._splitter.set_size_hint_to_current(recursive=True)

    def sizeHint(self):
        """Override size hint with procedurally set size hint.
        """
        size_hint = super(BpCollapsibleWidget, self).sizeHint()

        if self._orientation == QtCore.Qt.Vertical:
            size_hint.setHeight(self._size_hint)
        else:
            size_hint.setWidth(self._size_hint)

        return size_hint

    def total_margins(self):
        return sum([
            self._main_lyt.contentsMargins().top(),
            self._main_lyt.contentsMargins().bottom(),
        ])

    def get_collapsed_height(self):
        return self._expand_btn.height() + self.total_margins()

    def get_minimum_height(self):
        # print "splitter min height", self._splitter.get_minimum_height()

        if not self.expanded():
            return self.get_collapsed_height()

        max_height = sum([
            self._main_lyt.contentsMargins().top(),
            self._expand_btn.height(),
            self._main_lyt.spacing(),
            self._child_margin_lyt.contentsMargins().top(),
            # it's neccesary to use the height hint, instead of minimum height
            # because minimum height can often return 0,
            # which causes issues for our main layout which seems
            # to adapt and shrink the button layout below it's minimum height
            # TODO there's probably a better way to do this, but for now it seems to work
            self._splitter.get_minimum_height_hint(),
            #
            self._child_margin_lyt.contentsMargins().bottom(),
            self._main_lyt.contentsMargins().bottom(),
        ])

        if max_height < QT_WIDGET_MAX_HEIGHT:
            return max_height
        else:
            return QT_WIDGET_MAX_HEIGHT

    # def minimumHeight(self):
    # ** note: overriding this method seems to have no effect **
    #     print "min height", self.get_minimum_height()
    #     return self.get_minimum_height()

    def minimumSizeHint(self):
        """Override minimum size hint.

        This is a dependency of the above solution, we need to generate our own size hint
        to produce a minimum size that avoids widgets overlapping when the user
        shrinks down a splitter region to the point where the main layout shrinks the button.

        """
        minimum_size_hint = QtCore.QSize(
            super(BpCollapsibleWidget, self).minimumSizeHint().width(),
            self.get_minimum_height()
        )

        return minimum_size_hint

    def get_maximum_height(self):

        if not self.expanded():
            return self.get_collapsed_height()

        max_height = sum([
            self._main_lyt.contentsMargins().top(),
            self._expand_btn.height(),
            self._main_lyt.spacing(),
            self._child_margin_lyt.contentsMargins().top(),
            self._splitter.get_maximum_height(),
            self._child_margin_lyt.contentsMargins().bottom(),
            self._main_lyt.contentsMargins().bottom(),
        ])

        if max_height < QT_WIDGET_MAX_HEIGHT:
            return max_height
        else:
            return QT_WIDGET_MAX_HEIGHT

    def update_height_range(self, recursive=False):

        self._splitter.update_height_range(recursive=recursive)
        self.setMinimumHeight(self.get_minimum_height())
        self.setMaximumHeight(self.get_maximum_height())

    # def update_height(self, recursive=True):
    #     if not self.adapt_enabled():
    #         return
    #
    #     if recursive:
    #         for widget in self.widgets():
    #             if isinstance(widget, BpCollapsibleWidget):
    #                 widget.update_height(recursive=True)
    #
    #         self.update_height_range()
    #
    #         self.resize(
    #             self.width(),
    #             self.desired_height()
    #         )
    #
    #         # print "Height updated: {} {}".format(self.label(), self)
    #
    #     return True

    def update_cache(self, recursive=False):

        self._cached_expanded_height = self.height()
        self._cached_expanded_minimum_height = self.minimumHeight()
        self._cached_expanded_maximum_height = self.maximumHeight()

        self._splitter.update_cache(recursive=recursive)
        self._splitter_cached_expanded_minimum_height = self._splitter.minimumHeight()
        self._splitter_cached_expanded_maximum_height = self._splitter.maximumHeight()

        # if recursive:
        #     for widget in self.widgets():
        #         if isinstance(widget, BpCollapsibleWidget):
        #             if not widget.collapsed():
        #                 widget.update_cache(recursive=True)
        #
        #         elif isinstance(widget, BpResizingSplitter) and not self.collapsed():
        #             widget.update_cache(recursive=True)

    def apply_cached_expanded_heights_and_sizes(self, recursive=False):

        self.setMinimumHeight(self._cached_expanded_minimum_height)
        self.setMaximumHeight(self._cached_expanded_maximum_height)
        self._splitter.setMinimumHeight(self._splitter_cached_expanded_minimum_height)
        self._splitter.setMaximumHeight(self._splitter_cached_expanded_maximum_height)

        self._splitter.apply_cached_sizes(recursive=recursive)

        if not self.size_managed() or True:
            self.resize(
                self.width(),
                self._cached_expanded_height
            )

        self._size_hint = self._cached_expanded_height

        return True

    def collapse(self, recursive=False):

        if self.collapsed():
            return True

        # disable updating on resize while collapsed
        self.set_adapt_enabled(False, recursive=False)
        self._splitter.set_adapt_enabled(False, recursive=True)

        # inform parent widgets that we're about to resize
        self.ABOUT_TO_RESIZE.emit(self)

        # cache current height
        # self.update_cache(recursive=True)
        self.update_cache_full_stack()

        # first collapse children
        if recursive:
            for widget in self.widgets():
                if isinstance(widget, BpCollapsibleWidget):
                    widget.collapse(recursive=True)

        # hide splitter by setting height to 0
        self._splitter.setFixedHeight(0)

        # update button icon
        self._expand_btn.setIcon(self._collapsed_icon)

        # determine new size and store
        self._size_hint = self.get_collapsed_height()

        # mark as collapsed before inducing resizeEvents
        self._expanded = False

        # if this widget size isn't controlled by a parent widget
        # then go ahead and resize
        # (if widget size is controlled then this will be ignored?)
        # TODO find out
        self.setFixedHeight(
            self.get_collapsed_height()
        )

        self.RESIZED.emit(self)

        print "Collapsed: {} {}".format(self.label(), self)

    def collapsed(self):
        return not self._expanded

    def expand(self, recursive=False):

        if self._expanded:
            return True

        self.ABOUT_TO_RESIZE.emit(self)


        # if self._cached_expanded_height is not None:
        #     new_size = self._cached_expanded_height
        # else:
        #     new_size = self.sizeHint().height()

        self._expanded = True
        self._expand_btn.setIcon(self._expanded_icon)

        # restore height range
        # self.update_height_range()


        # expand children now there is room to
        if recursive:
            for widget in self.widgets():
                if isinstance(widget, BpCollapsibleWidget):
                    widget.expand(recursive=True)

        # then resize
        # self.resize(
        #     self.width(),
        #     new_size
        # )
        self.apply_cached_expanded_heights_and_sizes(recursive=True)

        # self.apply_cached_sizes(recursive=True)
        #
        self.RESIZED.emit(self)

        # re-enable updating on resize
        self.set_adapt_enabled(True)
        self._splitter.set_adapt_enabled(True, recursive=True)

        # print "DEBUG"
        # print "height", self.height(), self._size_hint
        # # print "widget min height: ", widget.minimumHeight(), widget.minimumSizeHint().height()
        # print "splitter min height", self._splitter.minimumHeight(), self._splitter.minimumSizeHint().height()
        # print "self min height", self.minimumHeight(), self.minimumSizeHint().height()
        # print "self max height", self.maximumHeight()
        # print "lyt min height", self._main_lyt.minimumSize().height()
        # print "chd lyt min height", self._child_margin_lyt.minimumSize().height()

    def expanded(self):
        return self._expanded

    def toggle_collapse(self):
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def adapt_enabled(self):
        return self._adapt_enabled

    def set_adapt_enabled(self, value, recursive=False):
        self._adapt_enabled = value == True

        print "DEBUG ADAPT ENABLED: {} ({})".format(self._adapt_enabled, self.label())

        if recursive:
            for widget in self.widgets():
                if isinstance(widget, (BpResizingSplitter, BpCollapsibleWidget)):
                    widget.set_adapt_enabled(value, recursive=True)

        return True

    def resizeEvent(self, *args, **kwargs):
        """
        Called either when user resizes this or a parent widget,
        or when a child widget has procedurally resized.
        """
        super(BpCollapsibleWidget, self).resizeEvent(*args, **kwargs)

        if not self.adapt_enabled():
            return

        # self.set_size_hint_to_current(recursive=True)
        # # self._splitter.cache_sizes()
        # # self._cached_height = self.height()
        print "RESIZED ({})".format(self.label())

    def _splitter_about_to_resize(self):
        if not self.adapt_enabled():
            return
        print "DEBUG SPLITTER ABOUT TO RESIZE ({})".format(self.label())
        self.ABOUT_TO_RESIZE.emit(self)

    def _splitter_resized(self):

        if not self.adapt_enabled():
            return

        print "DEBUG SPLITTER RESIZED ({})".format(self.label())

        # update min/max heights
        self.update_height_range()

        # calculate new height
        if self.orientation() == QtCore.Qt.Vertical:
            new_size = sum([
                self._main_lyt.contentsMargins().top(),
                self._expand_btn.height(),
                self._main_lyt.spacing(),
                self._child_margin_lyt.contentsMargins().top(),
                self._splitter.sizeHint().height(),
                self._child_margin_lyt.contentsMargins().bottom(),
                self._main_lyt.contentsMargins().bottom(),
            ])
        else:
            # TODO
            new_size = 0


        # resize self
        # (potentially overridden by parent widget)
        # if we are part of another adapting widget, then
        # the size hint will communicate our new desired size
        self.resize(
            self.width(),
            new_size
        )

        self._size_hint = new_size

        # emit signal to update parent widgets
        # (this assumes the ABOUT_TO_RESIZE signal has already been emitted)
        self.RESIZED.emit(self)

        # send data back down the chain to make sure everything is up to date
        # self.set_size_hint_to_current(recursive=True)

        return True


class Test0(object):
    def __init__(self):
        self._widget_1 = BpCollapsibleWidget(label="test1")

        self._edit_1 = QtWidgets.QTextEdit()
        self._edit_1.setText("blah")
        self._widget_1.add_widget(self._edit_1)

        self._widget_1.show()

class Test1(object):
    def __init__(self):
        self._splitter_1 = BpAutoResizingSplitter()
        self._splitter_1.setOrientation(QtCore.Qt.Vertical)

        self._widget_1 = BpCollapsibleWidget(label="test1")
        self._widget_2 = BpCollapsibleWidget(label="test2")
        self._widget_3 = BpCollapsibleWidget(label="test3")

        self._edit_1 = QtWidgets.QTextEdit()
        self._edit_1.setText("blah")
        self._widget_1.add_widget(self._edit_1)

        self._edit_2 = QtWidgets.QTextEdit()
        self._edit_2.setText("blah")
        self._widget_2.add_widget(self._edit_2)

        self._edit_3 = QtWidgets.QTextEdit()
        self._edit_3.setText("blah")
        self._widget_3.add_widget(self._edit_3)

        self._splitter_1.addWidget(self._widget_1)
        self._splitter_1.addWidget(self._widget_2)
        self._splitter_1.addWidget(self._widget_3)

        self._splitter_1.show()

class Test2(object):
    def __init__(self):
        self._widget_1 = BpCollapsibleWidget(label="test1")
        self._widget_2 = BpCollapsibleWidget(label="test2")
        self._widget_3 = BpCollapsibleWidget(label="test3")

        self._edit_1 = QtWidgets.QTextEdit()
        self._edit_1.setText("blah")
        self._widget_1.add_widget(self._edit_1)

        self._edit_2 = QtWidgets.QTextEdit()
        self._edit_2.setText("blah")
        self._widget_3.add_widget(self._edit_2)

        self._widget_2.add_widget(self._widget_1)
        self._widget_2.add_widget(self._widget_3)

        self._widget_2.show()


class Test3(object):
    def __init__(self):
        self._widget_1 = BpCollapsibleWidget(label="test1")
        self._widget_2 = BpCollapsibleWidget(label="test2")
        self._widget_3 = BpCollapsibleWidget(label="test3")
        self._widget_4 = BpCollapsibleWidget(label="test4")
        self._widget_5 = BpCollapsibleWidget(label="test5")

        self._edit_1 = QtWidgets.QTextEdit()
        self._edit_1.setText("blah")
        self._widget_1.add_widget(self._edit_1)

        self._edit_2 = QtWidgets.QTextEdit()
        self._edit_2.setText("blah")
        self._widget_3.add_widget(self._edit_2)

        self._edit_3 = QtWidgets.QTextEdit()
        self._edit_3.setText("blah")
        self._widget_5.add_widget(self._edit_3)

        self._edit_4 = QtWidgets.QTextEdit()
        self._edit_4.setText("blah")
        self._widget_1.add_widget(self._edit_4)

        self._widget_2.add_widget(self._widget_1)
        self._widget_2.add_widget(self._widget_3)

        self._widget_4.add_widget(self._widget_2)
        self._widget_4.add_widget(self._widget_5)

        self._edit_5 = QtWidgets.QTextEdit()
        self._edit_5.setText("blah")
        self._widget_2.add_widget(self._edit_5)

        self._widget_4.show()

        # TODO collapsing procedurally seems to cause some issues, figure out why
        # self._widget_4.collapse(recursive=False)
        # self._widget_3.collapse(recursive=False)



class ResizingSplitterTest(object):
    def __init__(self):
        self._widget_1 = BpResizingSplitter()

        self._widget_1.setOrientation(QtCore.Qt.Vertical)
        self._widget_1.setChildrenCollapsible(False)
        self._widget_1.setHandleWidth(50)

        self._edit_1 = QtWidgets.QTextEdit("stuff\nthings")
        self._edit_2 = QtWidgets.QTextEdit("stuff\nmore things")
        self._edit_3 = QtWidgets.QTextEdit("stuff\nthings3")

        self._btn_1 = QtWidgets.QPushButton("btn 1")
        self._btn_1.setFixedHeight(50)
        self._btn_2 = QtWidgets.QPushButton("btn 2")
        self._btn_2.setFixedHeight(50)
        self._btn_3 = QtWidgets.QPushButton("btn 3")
        self._btn_3.setFixedHeight(50)
        self._btn_4 = QtWidgets.QPushButton("btn 4")
        self._btn_4.setFixedHeight(50)

        self._widget_1.addWidget(self._edit_1)
        self._widget_1.addWidget(self._btn_1)
        self._widget_1.addWidget(self._edit_2)
        self._widget_1.addWidget(self._btn_2)
        self._widget_1.addWidget(self._edit_3)
        self._widget_1.addWidget(self._btn_3)
        self._widget_1.addWidget(self._btn_4)

        self._widget_1.show()

        # print pos, self._widget_1.sizes(), cursor_local_pos, self._widget_1.handleWidth()

class ScrollAreaTest(object):
    def __init__(self):

        self._widget_1 = BpResizingSplitter()

        self._widget_1.setOrientation(QtCore.Qt.Vertical)
        self._widget_1.setChildrenCollapsible(False)
        self._widget_1.setHandleWidth(50)

        self._edit_1 = QtWidgets.QTextEdit("stuff\nthings")
        self._edit_2 = QtWidgets.QTextEdit("stuff\nmore things")
        self._edit_3 = QtWidgets.QTextEdit("stuff\nthings3")

        self._btn_1 = QtWidgets.QPushButton("btn 1")
        self._btn_1.setFixedHeight(50)
        self._btn_2 = QtWidgets.QPushButton("btn 2")
        self._btn_2.setFixedHeight(50)
        self._btn_3 = QtWidgets.QPushButton("btn 3")
        self._btn_3.setFixedHeight(50)
        self._btn_4 = QtWidgets.QPushButton("btn 4")
        self._btn_4.setFixedHeight(50)

        self._widget_1.addWidget(self._edit_1)
        self._widget_1.addWidget(self._btn_1)
        self._widget_1.addWidget(self._edit_2)
        self._widget_1.addWidget(self._btn_2)
        self._widget_1.addWidget(self._edit_3)
        self._widget_1.addWidget(self._btn_3)
        self._widget_1.addWidget(self._btn_4)

        self._scroll_area = bpQtWidgets.BpScrollArea()
        self._scroll_area.setWidget(self._widget_1)
        # self._scroll_area.setWidgetResizable(True)
        self._scroll_area.set_widget_width_resizable(True)
        # self._scroll_area.set_widget_height_resizable(True)

        self._scroll_area.show()


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    if True:
        test = ResizingSplitterTest()
        # test = Test2()
        # test = ScrollAreaTest()
        # test.show()

    sys.exit(app.exec_())
