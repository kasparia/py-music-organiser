import mutagen
from mutagen.id3 import ID3
from datetime import datetime
import shutil
import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton
from PyQt5.QtCore import Qt

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test-files/"

trackFileList = []
currentYearString = str(datetime.now().year)

def getCurrentMonthFolderName():
  plainMonth = datetime.now().month
  if plainMonth < 10:
    return "0" + str(plainMonth) + "-" + currentYearString[-2:]
  else:
    str(plainMonth) + "-" + currentYearString[-2:]


# Organises single track into follow folder structure: <year> / <month - last two digits of year> / <artist name> / <filename>
def organiseSingleTrack(trackRawFilePath):

  rawFileName = os.path.basename(trackRawFilePath)
  print("Running organiser for file: " + rawFileName)

  if ( os.path.exists(trackRawFilePath)):
    audiofile = ID3(trackRawFilePath)
      
    artistFolderName = audiofile["TPE1"].text[0]
    print("Artist name: " + artistFolderName)
    print(ROOT_DIR)

    if artistFolderName:

      if not (os.path.exists(ROOT_DIR + currentYearString)):
        print("Creating yearly folder...")
        os.mkdir( ROOT_DIR + currentYearString ) 

      # check if current month folder exists
      if not ( os.path.exists(ROOT_DIR + currentYearString + "/" + getCurrentMonthFolderName()) ):
        print("Creating monthly folder...")
        os.mkdir( ROOT_DIR + currentYearString + "/" + getCurrentMonthFolderName() )

      # check if current artist name folder exists
      if not ( os.path.exists(ROOT_DIR + currentYearString + "/" + getCurrentMonthFolderName() + "/" + artistFolderName)):
        print("Creating artist folder...")
        os.mkdir( ROOT_DIR + currentYearString + "/" + getCurrentMonthFolderName() + "/" + artistFolderName)

      # move file to correct location inside monthly and artist folders
      shutil.move(
        trackRawFilePath, 
        ROOT_DIR + currentYearString + "/" + getCurrentMonthFolderName() + "/" + artistFolderName + "/" + rawFileName
      )

      trackFileList.remove(trackRawFilePath)
      return True


class PyMusicOrganiser(QWidget):

    def __init__(self):
        super().__init__()
        self.resize(640, 480)
        self.setWindowTitle("Organiser")
        self.setAcceptDrops(True)

        mainLayout = QVBoxLayout()

        self.trackListWidget = QListWidget()
        mainLayout.addWidget(self.trackListWidget)

        self.organiseButton = QPushButton()
        self.organiseButton.setText("Organise tracks")
        self.organiseButton.clicked.connect(self.organiseTracksFromListing)
        mainLayout.addWidget(self.organiseButton)

        self.setLayout(mainLayout)

    def organiseTracksFromListing(self):
      # print("list size " + str(len(trackFileList)))
      for index, singleTrackFilePath in enumerate(trackFileList):
        print(singleTrackFilePath)
        if organiseSingleTrack(singleTrackFilePath):
          self.trackListWidget.takeItem(index)


    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        event.setDropAction(Qt.CopyAction)
        for index, singleFileUrl in enumerate(event.mimeData().urls()):   
          filePath = event.mimeData().urls()[index].toLocalFile()
          trackFileList.append(filePath) # add to system's file listing
          self.trackListWidget.insertItem(self.trackListWidget.count(), filePath) # add file to GUI listing

app = QApplication(sys.argv)
organiserWindow = PyMusicOrganiser()
organiserWindow.show()
sys.exit(app.exec_())