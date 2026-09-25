from PyQt6.QtWidgets import QApplication

from uis.main_screen import Ui_Form as MainScreenUi
from ui_logic.main_screen_form import MainScreenForm
import sys
def main():
    app = QApplication(sys.argv)
    form = MainScreenForm(MainScreenUi)
    form.exec()
    
    # sys.exit(app.exec())

if __name__ == "__main__": 
    main()

