#import libraries
from PySide6 import QtWidgets, QtGui
from maya import cmds
from core.actions import validate_scene, alembic_export

class ExportAlembicUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Alembic Tool")
        self.resize(400, 300)

        self.build_ui()


    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.object_list = QtWidgets.QListWidget()
        layout.addWidget(self.object_list)

        self.refresh_button = QtWidgets.QPushButton("Refresh Selection")
        layout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self.refresh_selection)

        self.validate_button = QtWidgets.QPushButton("Validate")
        layout.addWidget(self.validate_button)
        self.validate_button.clicked.connect(self.validate_selection)

        self.export_button = QtWidgets.QPushButton("Export Alembic")
        layout.addWidget(self.export_button)
        self.export_button.clicked.connect(self.export_alembic)

    
    def refresh_selection(self):
        self.object_list.clear()
        selection = cmds.ls(selection=True)
        self.object_list.addItems(selection)

    
    def validate_selection(self):
        #recup all name in the list
        objects = [
            self.object_list.item(i).text().split(" ")[0]
            for i in range(self.object_list.count())
        ]

        if not objects:
            print("No object to validate")
            return
        
        report = validate_scene(objects)

        for obj, checks in report.items():
            if all(checks.values()):
                label = f"{obj} validate"
                color = QtGui.QColor("green")
            else:
                failed = [name for name, ok in checks.items() if not ok]
                label = f"{obj} failed checks: {', '.join(failed)}"
                color = QtGui.QColor("orange")
        
            item = QtWidgets.QListWidgetItem(label)
            item.setForeground(color)
            self.object_list.addItem(item)
        

    def export_alembic(self):
        #recup all name in the list
        objects = [
            self.object_list.item(i).text().split(" ")[0]
            for i in range(self.object_list.count())
        ]

        destination_path = QtWidgets.QFileDialog.getExistingDirectory(caption="Select Folder")

        alembic_export(objects, destination_path)


def show_ui():
    global window
    try:
        window.close()
        window.deleteLater()
    except:
        pass
    window = ExportAlembicUI()
    window.show()

show_ui()