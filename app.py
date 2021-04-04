import collections

import gevent.monkey

gevent.monkey.patch_all()
import ast
import tkinter
from datetime import datetime
from tkinter import messagebox, ttk

from tinydb import TinyDB, Query


class Record(object):
    def __init__(self, name, department, klass, student_id):
        self.name = name
        self.department = department
        self.klass = klass
        self.student_id = student_id
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "name": self.name,
            "department": self.department,
            "klass": self.klass,
            "student_id": self.student_id,
            "created_at": self.created_at,
        }


class Spartan(object):
    db = TinyDB(
        "db.json",
        indent=4,
        separators=(",", ": "),
        ensure_ascii=False,
        encoding="utf-8",
    )

    def __init__(self):
        # 主窗口
        self.root = tkinter.Tk()
        self.root.title("This is Sparta!")
        self.tabControl = ttk.Notebook(self.root)

        self.inspect_data = ttk.Frame(self.tabControl)
        self.manage_data = ttk.Frame(self.tabControl)
        self.tabControl.add(self.inspect_data, text="实时数据")
        self.tabControl.add(self.manage_data, text="管理")

        # 全局监听键盘输入
        self.root.bind("<Key>", self.handle_listen_keyboard)

        # 回显列表
        self.display_info = tkinter.Listbox(self.inspect_data, width=200)

        # 初始数据
        self.init_data()

        self.del_btn = tkinter.Button(
            self.inspect_data, command=self.handle_del, text="删除"
        )

    def init_data(self):
        data = self.db.all()
        for record in data:
            self.display_info.insert(0, record)
        self.input_buffer = ""

    def layout(self):
        self.tabControl.pack()
        self.display_info.pack()
        self.del_btn.pack(fill=tkinter.BOTH, expand=True)

    def handle_listen_keyboard(self, event):
        """监听键盘输入, 以回车区分"""
        if event.keycode == 13 and self.input_buffer:  # 回车键且有输入的内容
            self.handle_input()
        else:
            self.input_buffer += event.char

    def handle_input(self):
        """
        处理输入事件
        预期数据格式：
        {
            "name": "斯巴达",
            "department": "霍格沃兹做饭学院",
            "klass": 1001,
            "student_id": "0001'
        }
        """
        # record = Record(**msg)
        record = Record(
            name=f"{self.input_buffer}",
            department="霍格沃兹做饭学院",
            klass=1001,
            student_id="0001",
        )
        self.insert(record.to_dict())

    def handle_del(self):
        """处理删除按钮点击事件"""
        cur_select = self.display_info.curselection()
        self.delete(cur_select if cur_select else 0)

    def confirm_input(self, record):
        messagebox.showinfo(title="确认", message=f"{self.input_buffer} 交表了")

    def insert(self, record):
        """验重、插入数据库、插入ListBox、清空输入缓存"""
        if self.is_duplicated(record):
            messagebox.showinfo(title="确认", message="已交表")
        else:
            self.db.insert(record)
            self.display_info.insert(0, record)
            self.confirm_input(record)

        self.input_buffer = ""

    def delete(self, idx):
        """删除数据库记录、删除ListBox记录"""
        record = ast.literal_eval(self.display_info.get(idx))
        self.db.remove(Query().name == record.get("name"))
        self.display_info.delete(idx)

    def is_duplicated(self, record):
        return self.db.contains(Query().name == record.get("name"))


def main():
    # 初始化对象
    FL = Spartan()
    # 进行布局
    FL.layout()
    # 主程序执行
    tkinter.mainloop()


if __name__ == "__main__":
    main()
