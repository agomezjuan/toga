from gi.repository import Gtk

from .base import Widget


class Table(Widget):
    def create(self):
        self.store = Gtk.ListStore(*[str for h in self.interface.headings])

        # flat dict, maps Row to Gtk.TreeIter
        self.rows = {}

        # Create a table view, and put it in a scroll view.
        # The scroll view is the native, because it's the outer container.
        self.treeview = Gtk.TreeView(self.store)
        self.selection = self.treeview.get_selection()
        self.selection.set_mode(Gtk.SelectionMode.SINGLE)
        self.selection.connect("changed", self._on_select)

        for i, heading in enumerate(self.interface.headings):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(heading, renderer, text=i)
            self.treeview.append_column(column)

        self.native = Gtk.ScrolledWindow()
        self.native.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.native.add(self.treeview)
        self.native.set_min_content_width(200)
        self.native.set_min_content_height(200)
        self.native.interface = self.interface

    # Gtk.TreeIter cannot be compared with __eq__ !!!
    def compare_tree_iters(self, one, two):
        return self.store.get_path(one) == self.store.get_path(two)

    # find `tree_iter` in `self.rows`
    def get_row(self, tree_iter):
        if not isinstance(tree_iter, Gtk.TreeIter):
            raise TypeError("expected Gtk.TreeIter, got {}".format(type(tree_iter)))

        for row, it in self.rows.items():
            if self.compare_tree_iters(tree_iter, it):
                return row

    def _on_select(self, selection):
        if hasattr(self.interface, "_on_select") and self.interface.on_select:
            tree_model, tree_iter = selection.get_selected()
            row = self.get_row(tree_iter) if tree_iter else None
            self.interface.on_select(None, row=row)

    def row_data(self, row):
        return [
            str(getattr(row, attr))
            for attr in self.interface._accessors
        ]

    def change_source(self, source):
        """
        Synchronize self.data with self.interface.data
        """

        # Temporarily disconnecting the TreeStore improves performance for large
        # updates by deferring row rendering until the update is complete.
        self.treeview.set_model(None) # temporarily disconnect the view

        self.store.clear()
        for i, row in enumerate(self.interface.data):
            self.insert(i, row)

        self.treeview.set_model(self.store)

    def insert(self, index, item):
        self.rows[item] = self.store.insert(index, self.row_data(item))

    def change(self, item):
        self.store[self.rows[item]] = self.row_data(item)

    def remove(self, item):
        del self.store[self.rows[item]]
        del self.rows[item]

    def clear(self):
        self.store.clear()

    def set_on_select(self, handler):
        pass

    def scroll_to_row(self, row):
        raise NotImplementedError()
