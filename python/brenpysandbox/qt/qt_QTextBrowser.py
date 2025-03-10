import subprocess
import sys

from brenpy.qt.core.bpQtImportUtils import QtWidgets
from brenpy.qt.core.bpQtImportUtils import SIGNAL

# legacy code support

if SIGNAL is None:
    raise ImportError("Failed to import SIGNAL")

PYCHARM_BIN_DIR = r"C:\Program Files\JetBrains\PyCharm Community Edition 2019.2.3\bin"


class SandboxBrowser(QtWidgets.QTextBrowser):
    def __init__(self, *args, **kwargs):
        super(SandboxBrowser, self).__init__(*args, **kwargs)

        # self.test_1()
        # self.test_2()
        self.test_3()

    def test_1(self):

        self.setAcceptRichText(True)
        self.setOpenExternalLinks(True)

        for i in [
            'Plain Text',
            '<b>Bold</b>',
            '<i>Italic</i>',
            '<p style="color: red">Red</p>',
            '<p style="font-size: 20px">20px</p>',
            '<a href="https://www.google.com">Google</a>',
            'H<sup>2</sup>0',
            '2<sub>4</sub>',
        ]:
            self.append(i)

    def test_2(self):
        self.setAcceptRichText(True)
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)
        self.setSearchPaths(":")
        self.anchorClicked.connect(self._anchor_clicked)

        for i in [
            'Plain Text',
            'stuff :linkofsomeking things',
            'Plain Text',
            '<a href="https://www.google.com">Google</a>',
            '<a href="poop">poop</a>',
        ]:
            self.append(i)

    def _anchor_clicked(self, url):
        print url.toString()

    def test_3(self):
        self.setAcceptRichText(True)
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)
        self.setAutoFormatting(False)

        self.anchorClicked.connect(self._code_anchor_linked)

        for i in [
            'Plain Text',
            'Plain Text',
            r'<a href="D:\Repos\brenfbxpy\python\brenfbx\items\bfSceneItems.py,252">File "D:\Repos\brenfbxpy\python\brenfbx\items\bfSceneItems.py", line 252, in __init__</a>',
            '<a href="poop" style="color: none; text-decoration: none;" ><strong>poop</strong></a>',
        ]:
            # self.setTextColor()
            self.append(i)

    def _code_anchor_linked(self, url):
        path, line = url.toString().split(",")
        print path
        print line
        self.load_in_pycharm(path, int(line))

    def load_in_pycharm(self, file_path, line=0):
        cmd = r"{pycharm_bin_dir}\pycharm64.exe --line {line} {file_path}".format(
            pycharm_bin_dir=PYCHARM_BIN_DIR,
            line=line,
            file_path=file_path
        )

        subprocess.Popen(cmd)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    test = SandboxBrowser()
    test.show()

    sys.exit(app.exec_())
