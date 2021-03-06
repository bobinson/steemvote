from datetime import datetime
import time
import webbrowser

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class CommentsModel(QAbstractTableModel):
    URL = 0
    TIMESTAMP = 1
    REASON_TYPE = 2
    REASON_VALUE = 3
    TOTAL_FIELDS = 4
    def __init__(self, parent=None):
        super(CommentsModel, self).__init__(parent)
        self.comments = []

        self.headers = [
            {
                Qt.DisplayRole: 'URL',
                Qt.ToolTipRole: 'URL that the post can be found at',
            },
            {
                Qt.DisplayRole: 'Timestamp',
                Qt.ToolTipRole: 'When the post was created',
            },
            {
                Qt.DisplayRole: 'Reason',
                Qt.ToolTipRole: 'Why the post is being tracked',
            },
            {
                Qt.DisplayRole: 'User',
                Qt.ToolTipRole: 'Who caused the post to be tracked',
            },
        ]

    def set_comments(self, comments):
        """Set the comments for this model."""
        self.beginResetModel()
        self.comments = list(comments)
        self.endResetModel()

    def columnCount(self, parent=QModelIndex()):
        return self.TOTAL_FIELDS

    def rowCount(self, parent=QModelIndex()):
        return len(self.comments)

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if orientation != Qt.Horizontal: return None
        try:
            return self.headers[section][role]
        except (IndexError, KeyError):
            return None

    def data(self, index, role = Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self.comments):
            return None
        if role not in [Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole, Qt.UserRole]:
            return None

        tracked_comment = self.comments[index.row()]
        comment = tracked_comment.comment
        col = index.column()

        data = None
        if col == self.URL:
            data = comment.get_url()
            # UserRole is for the comment identifier.
            if role == Qt.UserRole:
                data = comment.identifier
        elif col == self.TIMESTAMP:
            data = comment.timestamp
            if role == Qt.DisplayRole:
                data = datetime.fromtimestamp(comment.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        elif col == self.REASON_TYPE:
            data = tracked_comment.reason_type
        elif col == self.REASON_VALUE:
            data = tracked_comment.reason_value

        return data


class CommentsWidget(QWidget):
    """Displays tracked comments."""
    def __init__(self, db, parent=None):
        super(CommentsWidget, self).__init__(parent)
        self.db = db
        self.model = CommentsModel()
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.model)

        self.view = QTableView()
        self.view.setModel(self.proxy_model)
        self.view.verticalHeader().setVisible(False)
        for header in [self.view.horizontalHeader(), self.view.verticalHeader()]:
            header.setHighlightSections(False)
        self.view.horizontalHeader().setResizeMode(self.model.URL, QHeaderView.Stretch)
        self.view.horizontalHeader().setResizeMode(self.model.TIMESTAMP, QHeaderView.ResizeToContents)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.view.setSortingEnabled(True)
        self.view.sortByColumn(self.model.TIMESTAMP, Qt.AscendingOrder)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.context_menu)

        # Layout.
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.view)
        self.setLayout(vbox)

    def update_comments(self):
        """Update tracked comments from the database."""
        self.model.set_comments(list(self.db.tracked_comments.values()))

    def context_menu(self, position):
        """Display the context menu."""
        if not self.view.selectedIndexes():
            return
        menu = QMenu()
        def open_in_browser(index):
            url = self.proxy_model.data(self.proxy_model.index(index.row(), self.model.URL))
            webbrowser.open(url)
        def open_user_page(index):
            user = self.proxy_model.data(self.proxy_model.index(index.row(), self.model.REASON_VALUE))
            url = 'https://steemit.com/@%s' % user
            webbrowser.open(url)
        def skip(index):
            identifier = self.proxy_model.data(self.proxy_model.index(index.row(), self.model.URL), role=Qt.UserRole)
            self.db.remove_tracked_comments([identifier])

        menu.addAction('Open post in browser', lambda: open_in_browser(self.view.currentIndex()))
        menu.addAction('Open user page in browser', lambda: open_user_page(self.view.currentIndex()))
        menu.addAction('Stop tracking', lambda: skip(self.view.currentIndex()))

        menu.exec_(self.view.viewport().mapToGlobal(position))
