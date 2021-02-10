# kivymd
from kivy.config import Config
Config.set('graphics', 'width','300')
Config.set('graphics', 'height','500')

from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.bottomsheet import MDListBottomSheet

from models import db, sql

KV = """
MDScreen:

    MDToolbar:
        id:button
        left_action_items: [["menu", lambda x: app.show_list_bottom_sheet()]]
        title: 'Номера'
        pos_hint: {'top': 1}
        height:'40dp'
        MDFloatingActionButtonSpeedDial:
            id:flat
            rotation_root_button: False
            root_button_anim: True
            callback:app.button_press
            data: app.data

"""
KV2 = """

BoxLayout:
    orientation: "vertical"
    spacing: "12dp"
    size_hint_y: None
    height: "120dp"

    MDTextField:
        hint_text: "номер авто"

"""


class Example(MDApp):

    dialog = None
    dialogPlus = None
    dialogPlusNone = None
    dialogAbout = None


    data = {
        "minus": "",
        "plus": "",
    }
    all_numbers = list()
    select_numbers = list()

    layout = AnchorLayout()

    def show_list_bottom_sheet(self):
        bottom_sheet_menu = MDListBottomSheet()
        bottom_sheet_menu.add_item("О приложении", callback = self.about)
        bottom_sheet_menu.add_item("Номер версии 0.8 ", callback = self.about)
        bottom_sheet_menu.open()

    def about(self,obj):
        self.dialogAbout = MDDialog(
            text = """Программа - База данных. \n\nПрограмма написанная на языке Python с использованием фреймворка KivyMd.

                    \n\nПо всем вопросам обращаться: \ntamirlanshereuzhev@gmail.com
                    """,
            buttons = [MDFlatButton(text = 'OK', on_press = self.about_dialog_close)] )
        self.dialogAbout.open()



    def on_start(self):

        self.sql_select()
        self.layout.add_widget(self.Table())
        self.layout.add_widget(Builder.load_string(KV))

    def on_check_press(self, instance_table, current_row):
        if self.select_numbers.count(current_row[0]) <1:
            for i in current_row:
                self.select_numbers.append(i)
        else:
            self.select_numbers.remove(current_row[0])


    def button_press(self, callback):

        if callback.icon == 'minus':
            if len(self.select_numbers) > 0:
                for i in self.select_numbers:
                    sql.execute(f"DELETE FROM numbers WHERE number = '{i}'")

                db.commit()
                self.sql_select()
                self.select_numbers.clear()
                self.layout.clear_widgets()
                self.layout.add_widget(self.Table())
                self.layout.add_widget(Builder.load_string(KV))

            else:
                self.dialog = MDDialog(
                    text = 'Выберите записи для удаления',
                    buttons = [MDFlatButton(text = 'OK', on_press = self.close_dialog1)] )
                self.dialog.open()


        elif callback.icon == 'plus':
            self.dialogPlus = MDDialog(
                title = "Добавление номера",
                type="custom",
                content_cls = Builder.load_string(KV2),
                buttons=[
                    MDFlatButton(
                        text="Отмена", text_color=self.theme_cls.primary_color, on_press = self.close_dialog2,
                    ),
                    MDFlatButton(
                        text="OK", text_color=self.theme_cls.primary_color, on_press = self.add_dialog,
                    ),
                ],
            )
            self.dialogPlus.open()


    def close_dialog1(self,obj):
        self.dialog.dismiss()
        self.dialog = None

    def close_dialog2(self,obj):
        self.dialogPlus.dismiss()
        self.dialogPlus = None

    def close_dialogNone(self,obj):
        self.dialogPlusNone.dismiss()
        self.dialogPlusNone = None

    def about_dialog_close(self,obj):
        self.dialogAbout.dismiss()
        self.dialogAbout = None

    def add_dialog(self,obj):
        for obj in self.dialogPlus.content_cls.children:
            if isinstance(obj, MDTextField):
                if obj.text!='':
                    k = next((z for z in sql.execute(f"SELECT number FROM numbers WHERE number = '{obj.text}'")),None)
                    if k is None:
                        sql.execute(f"INSERT INTO numbers VALUES ('{obj.text}')")
                        db.commit()
                        self.sql_select()
                        self.layout.clear_widgets()
                        self.layout.add_widget(self.Table())
                        self.layout.add_widget(Builder.load_string(KV))

                        self.dialogPlus.dismiss()
                        self.dialogPlus = None
                    else:
                        self.dialogPlusNone = MDDialog(
                            title = "Добавление номера",
                            text = 'Номер уже существует!',
                            buttons=[
                                MDFlatButton(
                                    text="OK", text_color=self.theme_cls.primary_color, on_press = self.close_dialogNone,
                                ),
                            ],
                        )
                        self.dialogPlusNone.open()

                else:
                    return


    def btpress(self, instance_button):
        self.dialog.close()

    def sql_select(self):
        self.all_numbers.clear()
        numbers = sql.execute("SELECT number FROM numbers")
        for i in numbers:
            self.all_numbers.append(i)

    def Table(self):
        count = next((k for k in (sql.execute("SELECT COUNT(number) FROM numbers"))))[0]
        if count <= 0: count = 1

        self.data_tables = MDDataTable(
            size_hint=(0.8, 0.8),
            check=True,
            column_data=[
                ("Numbers", dp(100)),
            ],
            row_data= self.all_numbers,
            rows_num = count,
            elevation=2,
        )
        self.data_tables.bind(on_check_press=self.on_check_press)
        return self.data_tables


    def build(self):
        return self.layout

if __name__ == '__main__':
    Example().run()
