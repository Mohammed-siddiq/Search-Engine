import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QLabel, QTextBrowser
from PyQt5.QtCore import pyqtSlot

from Ranker.MyRanker import get_search_result

'''
A simple UI displays user a query input and the results of the query search engine
'''

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'UIC search Engine'
        self.left = 10
        self.top = 10
        self.width = 1200
        self.height = 700
        self.initUI()
        self.results_page = 10

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(430, 20)
        self.textbox.resize(420, 30)
        self.textbox.setToolTip("Enter Your Query here")

        # Create a button in the window
        self.button = QPushButton('Search UIC', self)
        self.button.move(580, 55)

        # connect TextView to function on_click
        self.button.clicked.connect(self.on_click)
        self.result_view = QTextBrowser(self)
        # self.result_view.setReadOnly(True)
        self.result_view.move(250, 140)
        self.result_view.resize(800, 500)
        self.result_view.hide()
        self.next10 = QPushButton('Search More results....', self)
        self.next10.move(250, 110)
        self.next10.resize(250, 30)
        self.next10.setStyleSheet('color: blue')
        self.next10.clicked.connect(self.on_click_label)
        # self.next10.linkActivated(self.on_click_label)
        self.next10.hide()
        # self.next10.clicked.connect(self.on_click_label)
        self.setStyleSheet(
            "background-image: url(banner.jpg); background-attachment: stretch")
        self.showFullScreen()

    @pyqtSlot()
    def on_click(self):
        self.results_page = 10
        query = self.textbox.text()
        search_result = get_search_result(query, 500)
        display_html = ''
        self.url_list = []
        for url, score in search_result:

            display_html += self.add_href(url, score)
            self.url_list.append(self.add_href(url, score))

        urls = ''.join(self.url_list[:self.results_page])
        self.result_view.setText(urls)
        self.result_view.setOpenExternalLinks(True)
        # self.result_view.show()
        self.next10.setText('Show more Results....')
        self.next10.show()

        self.setStyleSheet("")

        self.result_view.show()

        # self.result_view.textCursor().insertHtml(display_html)
        # self.result_view.append(display_html)

    def add_href(self, url, score):
        # return '<a href="' + url + '">' + url + '</a>' + '<pre> Score : ' + str(score) + '</pre><br>'
        return '<a href="' + url + '">' + url + '</a><br><br>'

    @pyqtSlot()
    def on_click_label(self):
        self.results_page = self.results_page + 10
        self.result_view.setText(''.join(self.url_list[:self.results_page]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
