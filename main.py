from datetime import datetime
import shutil
import sys
import os
import mutagen
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QListWidgetItem, QLabel, QHBoxLayout, QLineEdit
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test-files/"

trackFileList = []
CURRENT_YEAR_STRING = str(datetime.now().year)

SETTINGS_GUI_WIDTH = 800
SETTINGS_GUI_HEIGHT = 600

def get_current_month_folder_name():
    """
        Stylize month got as an integer to string in format: "05-23". Used for folder naming.
    """
    plain_month = datetime.now().month
    if plain_month < 10:
        return "0" + str(plain_month) + "-" + CURRENT_YEAR_STRING[-2:]

    return str(plain_month) + "-" + CURRENT_YEAR_STRING[-2:]

def get_track_info(track_raw_file_path):
    """
        Get track ID3 info
        EasyID3 tags = dict_keys(['album', 'bpm', 'compilation', 'composer', 'copyright', 'encodedby', 'lyricist', 'length', 'media', 'mood', 'grouping', 'title', 'version',
        'artist', 'albumartist','conductor', 'arranger', 'discnumber', 'organization', 'tracknumber', 'author', 'albumartistsort', 'albumsort', 'composersort', 'artistsort',
        'titlesort', 'isrc', 'discsubtitle', 'language', 'genre', 'date', 'originaldate', 'performer:*', 'musicbrainz_trackid', 'website', 'replaygain_*_gain', 'replaygain_*_peak',
        'musicbrainz_artistid', 'musicbrainz_albumid', 'musicbrainz_albumartistid', 'musicbrainz_trmid', 'musicip_puid', 'musicip_fingerprint', 'musicbrainz_albumstatus',
        'musicbrainz_albumtype', 'releasecountry', 'musicbrainz_discid', 'asin', 'performer', 'barcode', 'catalognumber', 'musicbrainz_releasetrackid',
        'musicbrainz_releasegroupid', 'musicbrainz_workid', 'acoustid_fingerprint', 'acoustid_id'])
    """

    track_id3_info = {
        "artist": "",
        "albumartist": "",
        "album": "",
        "title": "",
        "length": ""
    }

    try:
        audio_id3_info = EasyID3(track_raw_file_path)
        #print(EasyID3.valid_keys.keys())
    except mutagen.id3.ID3NoHeaderError:
        return track_id3_info # If no ID3 tag is found, return as error file for list styling

    if os.path.exists(track_raw_file_path):
        if audio_id3_info:
            if not audio_id3_info["artist"] == "":
                track_id3_info["artist"] = audio_id3_info["artist"][0]

            if not audio_id3_info["albumartist"] == "":
                track_id3_info["albumartist"] = audio_id3_info["albumartist"][0]

            if not audio_id3_info["album"] == "":
                track_id3_info["album"] = audio_id3_info["album"][0]

            if not audio_id3_info["title"] == "":
                track_id3_info["title"] = audio_id3_info["title"][0]

            #if not audio_id3_info["length"] == "":
                #track_id3_info["length"] = audio_id3_info["length"]


    return track_id3_info

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




class TrackEditor(QWidget):
    """
        Editor for single track's ID3 ifnormation
    """

    def __init__(self):
        super().__init__()
        self.resize(480, 320)
        self.setWindowTitle("Editor")

        editor_window_layout = QVBoxLayout()

        self.track_file_path_label = QLabel("")
        editor_window_layout.addWidget(self.track_file_path_label)

        self.track_artist_field_label = QLabel("Artist")
        self.track_artist_field = QLineEdit()
        editor_window_layout.addWidget(self.track_artist_field_label)
        editor_window_layout.addWidget(self.track_artist_field)

        self.track_title_field_label = QLabel("title")
        self.track_title_field = QLineEdit()
        editor_window_layout.addWidget(self.track_title_field_label)
        editor_window_layout.addWidget(self.track_title_field)

        self.track_album_field_label = QLabel("Album")
        self.track_album_field = QLineEdit()
        editor_window_layout.addWidget(self.track_album_field_label)
        editor_window_layout.addWidget(self.track_album_field)

        editor_save_and_close_button = QPushButton("Save and close")
        editor_window_layout.addWidget(editor_save_and_close_button)

        self.setLayout(editor_window_layout)

    def populate_fields(self, track_file_path):
        """
            Populate editor fields with found ID3 info
        """

        track_info = get_track_info( track_file_path )
        self.track_file_path_label.setText( track_file_path )
        self.track_artist_field.setText( track_info["artist"] )
        self.track_title_field.setText( track_info["title"] )
        self.track_title_field.setText( track_info["album"] )




class PyMusicOrganiser(QWidget):
    """
        Main class for music organiser
    """

    def __init__(self):
        super().__init__()
        self.resize(SETTINGS_GUI_WIDTH, SETTINGS_GUI_HEIGHT)
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

    def show_track_id3_editor(self, track_file_path):
        self.track_editor = TrackEditor()
        self.track_editor.populate_fields(track_file_path)
        self.track_editor.show()
        print(track_file_path)


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

            item = QListWidgetItem()
            item_widget = QWidget()
            line_text = QLabel(file_path)
            line_push_button = QPushButton("Edit")
            #item.setObjectName(file_path)
            line_push_button.clicked.connect(lambda: self.show_track_id3_editor(file_path) )
            item_layout = QHBoxLayout()
            item_layout.addWidget(line_text)
            item_layout.addWidget(line_push_button)
            item_widget.setLayout(item_layout)
            item.setSizeHint(item_widget.sizeHint())
            #self.ListWidget.addItem(item)

            #self.track_list_widget.insertItem(self.track_list_widget.count(), file_path) # add file to GUI listing
            self.track_list_widget.addItem(item) # add file to GUI listing
            self.track_list_widget.setItemWidget(item, item_widget)

            #self.track_list_widget.insertItem(self.track_list_widget.count(), file_path) # add file to GUI listing



app = QApplication(sys.argv)
organiserWindow = PyMusicOrganiser()
organiserWindow.show()
sys.exit(app.exec_())
