from .base_form import Form
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene , QGraphicsTextItem
from PyQt6.QtGui import QPen, QBrush, QFont, QTextOption, QTextCursor, QPageSize, QPainter

# Import the Windows printer API
from PyQt6.QtPrintSupport import QPrinterInfo, QPrinter, QPrinterInfo
from PyQt6.QtCore import Qt, QSizeF, QRectF
# Import QSizeF for defining the physical label dimensions

import json
from pathlib import Path

class MainScreenForm(Form):

    def __init__(self,base_form):
        super().__init__(base_form)
        # set form title
        self.setWindowTitle("KAM-V1.0")
        self.set_icons()

        self.scene = QGraphicsScene()

        self.view = QGraphicsView(self.scene, self.ui.workspace)
        self.view.setGeometry(self.ui.workspace.rect())
        self.view.setStyleSheet("background: #dddddd; border: none;")

        self.label_width_mm = 40
        self.label_height_mm = 20

        # Set the allowed font-size range from 20 to 100
        self.ui.font_size.setMinimum(20)
        self.ui.font_size.setMaximum(100)

        self.create_label()
        # Load the printers installed in Windows into the printers combo box
        self.load_printers()

        # Connect the font-size slider so the current line changes size
        self.ui.font_size.valueChanged.connect(self.change_font_size)

        # Check the 5-line limit whenever the user changes the text
        self.text_item.document().contentsChanged.connect(self.check_text_limit)

        # Connect the Bold button
        self.ui.bold_btn.clicked.connect(self.toggle_bold)

        # Connect the Italic button
        self.ui.italic_btn.clicked.connect(self.toggle_italic)

        # Store the current vertical text alignment
        self.vertical_alignment = "center"

 

        

        # Connect the alignment buttons
        self.ui.top_btn.clicked.connect(self.align_text_top)
        self.ui.bottom_btn.clicked.connect(self.align_text_bottom)
        self.ui.x_center_btn.clicked.connect(self.align_text_vertical_center)
        self.ui.left_btn.clicked.connect(self.align_text_left)
        self.ui.right_btn.clicked.connect(self.align_text_right)
        self.ui.center_btn.clicked.connect(self.align_text_center)
        self.ui.rtl_ltr_btn.clicked.connect(self.toggle_text_direction)
        # Connect the Print button
        self.ui.print_btn.clicked.connect(self.print_label)

        

  

    def set_icons(self):
        """ Set icons for buttons in the form."""

        self.set_icon("logo_btn", "logo.png")
        self.set_icon("italic_btn", "italic.svg")
        self.set_icon("bold_btn", "bold.svg")
        self.set_icon("right_btn", "align-right.svg")
        self.set_icon("left_btn", "align-left.svg")
        self.set_icon("center_btn", "center.svg")
        self.set_icon("top_btn", "top.svg")
        self.set_icon("bottom_btn", "bottom.svg")
        self.set_icon("x_center_btn", "x_center.svg")
        self.set_icon("rtl_ltr_btn", "text-direction.svg")
        self.set_icon("print_btn", "print.svg")
        self.set_icon("cancel_btn", "cancel.svg")

    def create_label(self):
        workspace_width = self.ui.workspace.width()
        workspace_height = self.ui.workspace.height()

        margin = 20

        available_width = workspace_width - margin * 2
        available_height = workspace_height - margin * 2

        scale_x = available_width / self.label_width_mm
        scale_y = available_height / self.label_height_mm

        scale = min(scale_x, scale_y)

        width = self.label_width_mm * scale
        height = self.label_height_mm * scale

        x = (workspace_width - width) / 2
        y = (workspace_height - height) / 2
        # Store the label position and size so other functions can use them later
        self.label_x = x
        self.label_y = y
        self.label_width = width
        self.label_height = height

        self.scene.clear()
        self.scene.setSceneRect(0, 0, workspace_width, workspace_height)

        pen = QPen(Qt.PenStyle.NoPen)
        pen.setWidth(1)

        brush = QBrush(Qt.GlobalColor.white)

        self.scene.addRect(
            x,
            y,
            width,
            height,
            pen,
            brush
        )

        self.text_item = QGraphicsTextItem("أكتب هنا")
        self.text_item.setTextWidth(width)
        # Allow the user to type and edit text directly inside the label
        self.text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)

        option = self.text_item.document().defaultTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_item.document().setDefaultTextOption(option)

        self.text_item.setFont(
            QFont("Arial", 15)
        )

        self.scene.addItem(self.text_item)


        text_height = self.text_item.boundingRect().height()

        text_y = y + (height - text_height) / 2

        self.text_item.setPos(x, text_y)

    # Change the current text line's font size from the font-size slider
    def change_font_size(self, value):
        if not hasattr(self, "text_item"):
            return

        cursor = self.text_item.textCursor()

        # Select the current line
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)

        # Apply the slider value as the font size
        text_format = cursor.charFormat()
        text_format.setFontPointSize(value)

        cursor.mergeCharFormat(text_format)

        self.text_item.setTextCursor(cursor)

        self.update_text_position()

    # Reposition the text according to the current vertical alignment
    def update_text_position(self):
        text_height = self.text_item.boundingRect().height()

        if self.vertical_alignment == "top":
            text_y = self.label_y

        elif self.vertical_alignment == "bottom":
            text_y = self.label_y + self.label_height - text_height

        else:
            text_y = self.label_y + (self.label_height - text_height) / 2

        self.text_item.setPos(self.label_x, text_y)


  
    # Check the text height and keep the text inside the label
    def check_text_limit(self):
        text_height = self.text_item.boundingRect().height()

        if text_height > self.label_height:
            cursor = self.text_item.textCursor()

            if cursor.hasSelection():
                cursor.removeSelectedText()
            else:
                cursor.deletePreviousChar()

            self.text_item.setTextCursor(cursor)

        # Reposition the text according to the current vertical alignment
        self.update_text_position()

    # Position the text at the top of the label
    def align_text_top(self):
        self.vertical_alignment = "top"
        self.update_text_position()

    # Position the text at the bottom of the label
    def align_text_bottom(self):
        self.vertical_alignment = "bottom"
        self.update_text_position()

    # Position the text at the vertical center of the label
    def align_text_vertical_center(self):
        self.vertical_alignment = "center"
        self.update_text_position()

    # Align all text lines to the left
    def align_text_left(self):
        option = self.text_item.document().defaultTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.text_item.document().setDefaultTextOption(option)

    # Align all text lines to the right
    def align_text_right(self):
        option = self.text_item.document().defaultTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.text_item.document().setDefaultTextOption(option)

    # Align all text lines to the horizontal center
    def align_text_center(self):
        option = self.text_item.document().defaultTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_item.document().setDefaultTextOption(option)

    # Toggle the text direction between RTL and LTR
    def toggle_text_direction(self):
        option = self.text_item.document().defaultTextOption()

        if option.textDirection() == Qt.LayoutDirection.RightToLeft:
            option.setTextDirection(Qt.LayoutDirection.LeftToRight)
        else:
            option.setTextDirection(Qt.LayoutDirection.RightToLeft)

        self.text_item.document().setDefaultTextOption(option)

    # Load all available Windows printers into the printers combo box
    def load_printers(self):
        self.ui.printers.clear()

        printers = QPrinterInfo.availablePrinters()

        for printer in printers:
            self.ui.printers.addItem(printer.printerName())

    # Print the current virtual label using the selected size and printer
    def print_label(self):
        settings_path = Path(__file__).resolve().parent.parent / "settings.json"
        print(settings_path)

        # Read the selected label size from settings.json
        with open(settings_path, "r", encoding="utf-8") as file:
            settings = json.load(file)

        selected_size = settings["selected_size"]
        size_data = settings["sizes"][selected_size]

        width_mm = size_data["width_mm"]
        height_mm = size_data["height_mm"]

        # Get the printer selected in the combo box
        printer_name = self.ui.printers.currentText()

        if not printer_name:
            return

        # Create the printer and select the Windows printer
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPrinterName(printer_name)

        # Use the exact label dimensions as the physical paper size
        page_size = QPageSize(
        QSizeF(width_mm, height_mm),
        QPageSize.Unit.Millimeter
        )



        printer.setPageSize(page_size)
        printer.setFullPage(True)

        # Draw the same label area that is shown in the virtual editor
        painter = QPainter(printer)

        target_rect = QRectF(
            printer.pageLayout().paintRectPixels(
                printer.resolution()
            )
        )

        source_rect = self.scene.sceneRect()

        self.scene.render(
            painter,
            target_rect,
            source_rect
        )

        painter.end()


    # Toggle bold formatting for the current text line
    def toggle_bold(self):
        cursor = self.text_item.textCursor()

        # Select the current line
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)

        # Check whether the current line is already bold
        current_format = cursor.charFormat()
        is_bold = current_format.fontWeight() == QFont.Weight.Bold

        # Apply the opposite bold state
        text_format = cursor.charFormat()

        if is_bold:
            text_format.setFontWeight(QFont.Weight.Normal)
        else:
            text_format.setFontWeight(QFont.Weight.Bold)

        cursor.mergeCharFormat(text_format)

        self.text_item.setTextCursor(cursor)

    # Toggle italic formatting for the current text line
    def toggle_italic(self):
        cursor = self.text_item.textCursor()

        # Select the current line
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)

        # Check whether the current line is already italic
        current_format = cursor.charFormat()
        is_italic = current_format.fontItalic()

        # Apply the opposite italic state
        text_format = cursor.charFormat()
        text_format.setFontItalic(not is_italic)

        cursor.mergeCharFormat(text_format)

        self.text_item.setTextCursor(cursor)





        
