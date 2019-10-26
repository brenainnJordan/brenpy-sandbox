'''
Created on Nov 26, 2017

@author: User
'''

import sys
import json

# ordered dict is to maintain hierarchy order
# deque and deepcopy are used for undo que
from collections import OrderedDict, deque
from copy import deepcopy

from PySide import QtGui
from PySide.QtCore import Qt

#deque([tuple(i.astype(int))], maxlen=self.trail_len)

# Node/Root hierarchy functions ---

def get_children_names_recursive_dict(parent, hierarchy_dict):
    '''
    Recursively loop through children and store node names into dict
    '''
    
    for child in parent.children:
        child_dict = hierarchy_dict[child.name] = {}
        get_children_names_recursive_dict(child, child_dict)


def get_children_names(parent, recursive=True, flatten=False):
    '''
    Get names of all children
    :recursive True: return all children names as dict
    :flatten True: as above but as flat list
    :recursive False: return top level children as list
    '''
    
    if recursive and flatten:
        node_list = []
        get_children_recursive_list(parent, node_list)
        node_name_list = [i.name for i in node_list]
        return node_name_list
    
    elif recursive:
        #hierarchy_dict = {}
        hierarchy_dict = OrderedDict()
        get_children_names_recursive_dict(parent, hierarchy_dict)
        return hierarchy_dict
    
    else:
        child_list = [child.name for child in parent.children]
        return child_list


def get_children_recursive_list(parent, node_list):
    '''
    Recursively loop through children and store node instances into list
    '''
    
    for child in parent.children:
        node_list.append(child)
        get_children_recursive_list(child, node_list)


def get_children(parent, recursive=False):
    '''
    Return flat list of node instances
    '''
    
    if recursive:
        node_list = []
        get_children_recursive_list(parent, node_list)
        return node_list
    else:
        return parent.children


# Multiple Node functions ---

def get_common_node_parent(nodes, inclusive=True):
        '''
        Walk up hierarchy until we find a parent shared by all nodes
        '''
        if len(nodes) == 1:
            return nodes[0].parent
        
        prnts = [node.get_parents() for node in nodes]
        
        if inclusive:
            prnts = [[a]+b for a, b in zip(nodes, prnts)]
        
        common_prnts = list(set(prnts[0]).intersection(*prnts))
        common_prnts = sort_nodes_by_hierarchy(common_prnts)
        common_prnts.reverse()
        
        return common_prnts[0]


def sort_nodes_by_hierarchy(nodes):
    '''
    sort list of nodes by highest first
    siblings in no particular order
    '''
    # get root
    for node in nodes:
        if isinstance(node, Root):
            root = node
            break
        elif isinstance(node, Node):
            root = node.get_root()
            break
    
    # get nodes
    node_order = [root]+get_children(root, recursive=True)
    ordered_nodes = [i for i in node_order if i in nodes]
    return ordered_nodes


# Node/Root Classes ---

class Root(object):
    '''
    Top level hierarchy node to store Node children
    '''
    
    def __init__(self):
        self.children = []
    
    def __str__(self):
        '''
        Return human readable hierarchy
        '''
        
        str_data = json.dumps(
            self.get_children_names(recursive=True, flatten=False),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
        
        return str_data
    
    def get_children_names(self, recursive=True, flatten=False):
        return get_children_names(self, recursive=recursive, flatten=flatten)


class Node(object):
    '''
    Hierachy node to store name and arbitrary contents
    '''
    
    def __init__(self, parent, name, contents=None):
        self.children = []
        
        self._name = None
        res = self.set_name(name)
        if not res:
            return None
        
        self.contents = contents
        
        self._parent = None
        self.parent = parent
    
    def set_parent(self, parent):
        # type check
        if not isinstance(parent, (Node, Root)):
            return False
        
        # child check
        if parent in get_children(self, recursive=True):
            print "cannot parent to one of it's own children"
            return False
        
        # unparent from current parent
        if isinstance(self._parent, (Node, Root)):
            self._parent.children.remove(self)
        
        # parent
        self._parent = parent
        parent.children.append(self)
        return True

    
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        self.set_parent(parent)
    
    def set_name(self, name):
        if not isinstance(name, (str, unicode)):
            print 'name is not of valid type: ', type(name)
            return False
        self._name = name
        return True
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self.set_name(name)
    
    def get_root(self):
        node = self
        while True:
            if isinstance(node, Root):
                return node
            node = node.parent
    
    def get_parents(self):
        '''
        Walk up hierarchy until we find Root instance
        '''
        
        prnts = [self.parent]
        
        while isinstance(prnts[-1], Node):
            prnt = prnts[-1].parent
            prnts.append(prnt)
        
        return prnts



# Qt Gui ---

class GUI(QtGui.QWidget):
    '''
    Simple GUI to represent and edit hierarchy
    '''
    
    def __init__(self, max_undo=10):
        super(GUI, self).__init__()
        
        # get hierarchy
        self.hierarchy = self.test()
        self.max_undo = max_undo
        
        # init undo que
        self.hierachy_undo_que = deque([self.hierarchy], maxlen=self.max_undo)
        
        # create layout
        self.lyt = QtGui.QHBoxLayout()
        self.setLayout(self.lyt)
        
        # create and configure tree view
        self.tree = QtGui.QTreeView()
        self.tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu_handler)
        
        # create model and populate tree
        self.model = QtGui.QStandardItemModel()
        self.tree.setModel(self.model)
        
        self.populate_tree()
        self.model.setHorizontalHeaderLabels(['Hierarchy'])
        
        # add tree to widget
        self.lyt.addWidget(self.tree)
        
        # btns
        btn_lyt = QtGui.QVBoxLayout()
        self.lyt.addLayout(btn_lyt)
        
        # debug button
        debug_btn = QtGui.QPushButton('debug')
        debug_btn.clicked.connect(self.print_hierarchy)
        btn_lyt.addWidget(debug_btn)
        
        test_btn = QtGui.QPushButton('test')
        test_btn.clicked.connect(self.print_test)
        btn_lyt.addWidget(test_btn)
        
        undo_btn = QtGui.QPushButton('undo')
        undo_btn.clicked.connect(self.undo_hierarchy_operation)
        btn_lyt.addWidget(undo_btn)
    
    def update_hierachy_undo_que(self):
        current_state = deepcopy(self.hierarchy)
        self.hierachy_undo_que.append(current_state)
    
    def undo_hierarchy_operation(self):
        if len(self.hierachy_undo_que) == 1:
            print "no more undo's left"
            return
        
        # return and remove element from right side of deque
        self.hierarchy = self.hierachy_undo_que.pop()
        self.populate_tree()
    
    def print_hierarchy(self):
        print str(self.root_node)
        print get_children_names(self.root_node, recursive=True, flatten=True)
    
    def print_test(self):
        nodes = self.get_selected_nodes()
        items = self.get_selected_node_items()
        if not len(nodes):
            return
        
        common_prnt = get_common_node_parent(nodes)
        common_prnt_item = common_prnt.qt_item    
        
        if isinstance(common_prnt, Root):
            print 'root'
        else:
            print common_prnt.name
        print common_prnt_item
        print common_prnt_item.text()
    
    def get_selected_node_items(self):
        '''
        Get selected items which contain a Node instance and return items
        '''
        sl_ids = self.tree.selectedIndexes()
        selected_items = [self.model.itemFromIndex(i) for i in sl_ids]
        selected_node_items = [i for i in selected_items if isinstance(i.node, Node)]
        return selected_node_items
            
    def get_selected_nodes(self):
        '''
        Get selected items which contain a Node instance and return nodes.
        No Root instances are returned.
        '''
        selected_node_items = self.get_selected_node_items()
        selected_nodes = [i.node for i in selected_node_items]
        return selected_nodes
    
    def context_menu_handler(self, position):
        '''
        Get information about what items are selected.
        Then show the appropriate context menu.
        '''
        ids = self.tree.selectedIndexes()
        node_items = self.get_selected_node_items()
        
        if len(ids) == 2 and len(node_items) == 1:
            self.single_node_and_root_context_menu(position, node_items[0])
        elif len(ids) > len(node_items):
            self.multi_node_and_root_context_menu(position, node_items)
        elif len(node_items) == 1:
            self.single_node_context_menu(position, node_items[0])
        elif len(node_items) > 1:
            self.multi_node_context_menu(position, node_items)
        else:
            self.root_context_menu(position)

    def single_node_and_root_context_menu(self, position, item):
        '''
        Context menu for when root and one node is selected
        '''
        menu = QtGui.QMenu(self)
        prnt_action = menu.addAction('Parent to Root')
        
        action = menu.exec_(self.mapToGlobal(position))
        if action == prnt_action:
            self.parent_item_and_node(item, self.root_item)
    
    def multi_node_and_root_context_menu(self, position, node_items):
        '''
        Context menu for when root and multiple nodes are selected
        '''
        menu = QtGui.QMenu(self)
        
        parent_action = menu.addAction('Parent to Root')
        parent_hierarchy_action = menu.addAction('Parent to Root (keep hierarchy)')
        
        action = menu.exec_(self.mapToGlobal(position))
        
        if action == parent_action:
            for item in node_items:
                self.parent_item_and_node(item, self.root_item)
        elif action == parent_hierarchy_action:
            #common_prnt_item = get_common_item_parent(node_items)
            common_prnt_node = get_common_node_parent([i.node for i in node_items], inclusive=True)
            common_prnt_item = common_prnt_node.qt_item
            self.parent_item_and_node(common_prnt_item, self.root_item)
            
    
    def single_node_context_menu(self, position, item):
        '''
        Context menu for when one node is selected and root is not selected. 
        '''
        menu = QtGui.QMenu(self)
        
        new_child_action = menu.addAction('New child')
        new_sibling_action = menu.addAction('New sibling')
        new_parent_action = menu.addAction('New parent')
        del_node_action = menu.addAction('Delete')
        rename_action = menu.addAction('Rename')
        
        action = menu.exec_(self.mapToGlobal(position))
        
        if action == new_child_action:
            self.new_child_node(item)
        elif action == new_sibling_action:
            self.new_sibling_node(item)
        elif action == new_parent_action:
            self.new_parent_node([item])
        elif action == del_node_action:
            self.delete_item_and_node(item)
        elif action == rename_action:
            self.rename_item_and_node(item)
    
    
    def multi_node_context_menu(self, position, node_items):
        '''
        Context menu for when multiply nodes are selected and root is not selected.
        '''
        
        menu = QtGui.QMenu(self)
        #new_node_action = menu.addAction('New node')
        del_nodes_action = menu.addAction('Delete')
        parent_action = menu.addAction('Parent to node')
        parent_hierarchy_action = menu.addAction('Parent to node (keep hierarchy)')
        
        action = menu.exec_(self.mapToGlobal(position))
        
        if action == del_nodes_action:
            for selected_item in node_items:
                self.delete_item_and_node(selected_item)
        
        elif action == parent_action:
            parent_item = node_items[-1]
            for item in node_items[:-1]:
                self.parent_item_and_node(item, parent_item)
        
        elif action == parent_hierarchy_action:
            parent_item = node_items[-1]
            common_prnt_node = get_common_node_parent([i.node for i in node_items[:-1]], inclusive=True)
            #common_prnt_item = get_common_item_parent(node_items)
            print [i.node.name for i in node_items]
            if isinstance(common_prnt_node, Root):
                print 'Cannot parent Root'
                return
            
            common_prnt_item = common_prnt_node.qt_item
            self.parent_item_and_node(common_prnt_item, parent_item)
    
    
    def root_context_menu(self, position):
        menu = QtGui.QMenu(self)
        new_node_action = menu.addAction('New node')
        root_action = menu.addAction('Root stuff')
        
        action = menu.exec_(self.mapToGlobal(position))
        if action == new_node_action:
            self.new_node(self.root_item)
    
    
    def new_node_item(self, name, parent_item):
        parent_node = parent_item.node
        node = Node(parent_node, name)
        item = QtGui.QStandardItem(name)
        item.setEditable(False)
        item.node = node
        node.qt_item = item
        parent_item.appendRow(item)
        return item
    
    
    def new_child_node(self, parent_item):
        name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter new child node name:')
        if not ok:
            return
        
        self.update_hierachy_undo_que()
        self.new_node_item(name, parent_item)
    
    
    def new_sibling_node(self, item):
        name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter new sibling node name:')
        if not ok:
            return
        
        self.update_hierachy_undo_que()
        parent_item = item.parent()
        self.new_node_item(name, parent_item)
    
    
    def new_parent_node(self, items):
        name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter new parent node name:')
        if not ok:
            return
        
        self.update_hierachy_undo_que()
        
        nodes = [i.node for i in items]
        common_parent_node = get_common_node_parent(nodes, inclusive=False)
        common_parent_item = common_parent_node.qt_item
        
        parent_item = self.new_node_item(name, common_parent_item)
        
        for item in items:
            self.parent_item_and_node(item, parent_item)
    
    def delete_item_and_node(self, item):
        node = item.node
        node.parent.children.remove(node)
        item_parent = item.parent()
        item_parent.removeRow(item.index().row())
        
    def rename_item_and_node(self, item):
        self.update_hierachy_undo_que()
        
        name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 'Enter new name:')
        if not ok:
            return
        
        node = item.node
        res = node.set_name(name)
        if not res:
            return
        
        item.setText(name)
    
    def parent_item_and_node(self, item, new_parent_item):
        self.update_hierachy_undo_que()
        
        # reparent node
        item_node = item.node
        new_parent_node = new_parent_item.node
        res = item_node.set_parent(new_parent_node)
        
        if res is False:
            return

        # remove row without deleting it
        item_parent = item.parent()
        item_parent.takeRow(item.index().row())
        
        # append to new parent
        new_parent_item.appendRow(item)
    
    
    def _populate_tree_recursive(self, node, item_parent):
        for child_node in node.children:
            name = child_node.name
            child_item = QtGui.QStandardItem(str(name))
            child_item.setEditable(False)
            child_item.node = child_node
            child_node.qt_item = child_item
            item_parent.appendRow(child_item)
            self._populate_tree_recursive(child_node, child_item)
    
    
    def populate_tree(self):
        self.model.clear()
        self.root_node = self.hierarchy
        self.root_item = QtGui.QStandardItem('root')
        self.root_item.setEditable(False)
        self.root_item.node = self.root_node
        self.root_node.qt_item = self.root_item
        self.model.appendRow(self.root_item)
        self._populate_tree_recursive(self.root_node, self.root_item)
        self.tree.expandAll()
        
    
    def test(self):
        root = Root()
        
        for i in range(6):
            child = Node(root, str(i))
            
            for j in range(3):
                sub_child = Node(child, '{}_{}'.format(i, j))
        
        return root


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec_())
    