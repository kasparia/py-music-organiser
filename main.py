from datetime import datetime
import shutil
import sys
import os
import mutagen
from mutagen.id3 import ID3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test-files/"

trackFileList = []
CURRENT_YEAR_STRING = str(datetime.now().year)

def get_current_month_folder_name():
    """
        Stylize month got as an integer to string in format: "05-23". Used for folder naming.
    """
    plain_month = datetime.now().month
    if plain_month < 10:
        return "0" + str(plain_month) + "-" + CURRENT_YEAR_STRING[-2:]

    return str(plain_month) + "-" + CURRENT_YEAR_STRING[-2:]


def organise_single_track(track_raw_file_path):
    """
        Organises single track into follow folder structure: 
        <year> / <month - last two digits of year> / <artist name> / <filename>
    """

    raw_file_name = os.path.basename(track_raw_file_path)
    print("Running organiser for file: " + raw_file_name)

    try:
        audiofile = ID3(track_raw_file_path)
    except mutagen.id3.ID3NoHeaderError:
        return False # If no ID3 tag is found, return as error file for list styling

    if ( os.path.exists(track_raw_file_path) and audiofile):
        artist_folder_name = audiofile["TPE1"].text[0]
        print("Artist name: " + artist_folder_name)

        if artist_folder_name:

            if not os.path.exists(ROOT_DIR + CURRENT_YEAR_STRING) :
                print("Creating yearly folder...")
                os.mkdir( ROOT_DIR + CURRENT_YEAR_STRING )

            # check if current month folder exists
            if not os.path.exists(ROOT_DIR + CURRENT_YEAR_STRING + "/" + get_current_month_folder_name()) :
                print("Creating monthly folder...")
                os.mkdir( ROOT_DIR + CURRENT_YEAR_STRING + "/" + get_current_month_folder_name() )

            # check if current artist name folder exists
            if not os.path.exists(ROOT_DIR + CURRENT_YEAR_STRING + "/" + get_current_month_folder_name() + "/" + artist_folder_name) :
                print("Creating artist folder...")
                os.mkdir( ROOT_DIR + CURRENT_YEAR_STRING + "/" + get_current_month_folder_name() + "/" + artist_folder_name)

            # move file to correct location inside monthly and artist folders
            shutil.move(
                track_raw_file_path,
                ROOT_DIR + CURRENT_YEAR_STRING + "/" + get_current_month_folder_name() + "/" + artist_folder_name + "/" + raw_file_name
            )

            trackFileList.remove(track_raw_file_path)
            return True
    return False

class PyMusicOrganiser(QWidget):
    """
        Main class for music organiser
    """

    def __init__(self):
        super().__init__()
        self.resize(640, 480)
        self.setWindowTitle("Organiser")
        self.setAcceptDrops(True)

        main_gui_layout = QVBoxLayout()

        self.track_list_widget = QListWidget()
        main_gui_layout.addWidget(self.track_list_widget)

        self.organise_button = QPushButton()
        self.organise_button.setText("Organise tracks")
        self.organise_button.clicked.connect(self.organise_tracks_from_listing)
        main_gui_layout.addWidget(self.organise_button)

        self.setLayout(main_gui_layout)

    def organise_tracks_from_listing(self):
        for index, single_track_file_path in enumerate(trackFileList):
            print(single_track_file_path)
            if organise_single_track(single_track_file_path):
                self.track_list_widget.takeItem(index)
            else:
                items = self.track_list_widget.findItems(single_track_file_path, Qt.MatchExactly)
                if len(items) > 0:
                    for single_error_item in items:
                        single_error_item.setBackground(QColor("#ff2e2e"))

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
        for index, single_file_url in enumerate(event.mimeData().urls()):   
            file_path = event.mimeData().urls()[index].toLocalFile()
            trackFileList.append(file_path) # add to system's file listing
            self.track_list_widget.insertItem(self.track_list_widget.count(), file_path) # add file to GUI listing

app = QApplication(sys.argv)
organiserWindow = PyMusicOrganiser()
organiserWindow.show()
sys.exit(app.exec_())
