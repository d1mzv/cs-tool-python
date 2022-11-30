import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter import *
import json
import pandas as pd
from nade_loader_v2 import *
import sv_ttk
import webbrowser


class MultiColumnListbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""

    def __init__(self):
        self.tree = None
        self.df = read_data()
        self._setup_widgets()
        self._build_tree()

    def _setup_widgets(self):
        container = Frame(root)
        container.pack(fill='both', expand=True, side='bottom', padx=10)
        # create a treeview with dual scrollbars
        self.display_df = self.df.copy()
        del self.display_df['url']
        headers = self.display_df.columns.values.tolist()
        self.tree = ttk.Treeview(columns=headers, show="headings")
        self.tree.bind('<Control-c>', self.copy)
        self.tree.bind('<Double-Button>', self.open_url)
        vsb = ttk.Scrollbar(orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def _build_tree(self):
        headers = self.display_df.columns.values.tolist()
        for col in headers:
            self.tree.heading(col, text=col.title(),
                              command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                             width=tkFont.Font().measure(col.title()))
        nades_list = self.display_df.values.tolist()
        for item in nades_list:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(headers[ix], width=None) < col_w:
                    self.tree.column(
                        headers[ix], width=min(col_w, 200))

    def update(self, selected_maps, selected_playlists, selected_authors):
        self.df = read_data()
        data = self.df.to_dict('records')
        for item in self.tree.get_children():
            self.tree.delete(item)
        data_filtered = []
        data_filtered_full = []
        for i in range(len(data)):
            if (data[i]['map'] in selected_maps or selected_maps == [] or 'All' in selected_maps) and (bool(set(data[i]['playlists']) & set(selected_playlists)) or selected_playlists == [] or 'All' in selected_playlists) and (data[i]['created_by'] in selected_authors or selected_authors == [] or 'All' in selected_authors):
                # del data[i]['url']
                lst = list(data[i].values())
                self.tree.insert('', 'end', values=lst)
                data_filtered.append(data[i])
        with open('data_filtered.txt', 'w') as f:
            json.dump(data_filtered, f)

    def copy(self, event):
        sel = self.tree.selection()  # get selected items
        root.clipboard_clear()  # clear clipboard
        # # copy headers
        # headings = [self.tree.heading("#{}".format(i), "text")
        #             for i in range(len(self.tree.cget("columns")) + 1)]
        # root.clipboard_append("\t".join(headings) + "\n")
        for item in sel:
            # retrieve the values of the row
            values = [self.tree.item(item, 'text')]
            values.extend(self.tree.item(item, 'values'))
            # append the values separated by \t to the clipboard
            print(values[5])
            root.clipboard_append(values[5])
            return

    def open_url(self, event):
        sel = self.tree.selection()
        for item in sel:
            # retrieve the values of the row
            values = [self.tree.item(item, 'text')]
            values.extend(self.tree.item(item, 'values'))
            # append the values separated by \t to the clipboard
            map, name, coord = values[1], values[3], values[5]
            dfx = self.df.query(
                "map == @map and name == @name and coordinates == @coord")
            # print(map, name, coord)
            print(dfx.values[0][8])
            webbrowser.open(dfx.values[0][8])  # Go to example.com
            return
        # print('test')


def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    data = [(tree.set(child, col), child)
            for child in tree.get_children('')]
    # if the data to be sorted is numeric change to float
    #data =  change_numeric(data)
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col,
                                                     int(not descending)))


def apply_filters(evt):
    # get all selected indices
    selected_indices = listbox_maps.curselection()
    selected_maps = [listbox_maps.get(i) for i in selected_indices]
    selected_indices = listbox_playlists.curselection()
    selected_playlists = [listbox_playlists.get(i) for i in selected_indices]
    selected_indices = listbox_created_by.curselection()
    selected_authors = [listbox_created_by.get(i) for i in selected_indices]
    msg = f'Maps: {selected_maps}, Playlists: {selected_playlists}, Authors: {selected_authors}'
    # global listbox
    listbox_main.update(selected_maps, selected_playlists, selected_authors)
    print(msg)


def refresh_db():
    main()
    apply_filters(1)
    load()


def load_nades():
    load()


def read_data():
    f = open('data.txt')
    data = json.load(f)
    df = pd.DataFrame.from_dict(data)
    # del df['url']
    return df


def generate_filter(values):
    return tk.Listbox(
        top_frame_1, listvariable=tk.Variable(value=values), height=6, width=20, selectmode=tk.EXTENDED, exportselection=0,
    )


def format_filter(filter):
    filter.pack(side='left', expand=True)
    filter.bind('<<ListboxSelect>>', apply_filters)
    filter.select_set(0)  # This only sets focus on the first item.
    filter.event_generate("<<ListboxSelect>>")


def create_listbox(values):
    listbox = tk.Listbox(
        top_frame_1, listvariable=tk.Variable(value=values), height=6, width=20, selectmode=tk.EXTENDED, exportselection=0,
    )
    listbox.pack(side='left', expand=True)
    listbox.bind('<<ListboxSelect>>', apply_filters)
    listbox.select_set(0)  # This only sets focus on the first item.
    listbox.event_generate("<<ListboxSelect>>")
    return listbox


root = tk.Tk()
top_frame = Frame(root, padx=10, pady=10)
top_frame.pack(side='top', anchor=W)
top_frame_1 = Frame(top_frame)
top_frame_1.pack(side='left', anchor=W)
top_frame_2 = Frame(top_frame)
top_frame_2.pack(side='left', anchor=N, padx=(5, 2))
top_frame_3 = Frame(top_frame)
top_frame_3.pack(side='left', anchor=N, padx=2)
top_frame_4 = Frame(top_frame)
top_frame_4.pack(side='left', anchor=N, padx=2)
root.title("Nadebook")
sv_ttk.set_theme("dark")
root.config(menu="")
root.geometry("1200x800")

u_maps, u_playlists, u_created_by = generate_filters()

listbox_maps = create_listbox(u_maps)
listbox_playlists = create_listbox(u_playlists)
listbox_created_by = create_listbox(u_created_by)

ttk.Button(top_frame_2, text='Refresh DB',
           command=refresh_db).pack(fill="x", pady=(0, 2))

ttk.Button(top_frame_2, text='Load Nades',
           command=load_nades).pack(fill="x", pady=(0, 2))
# style='Accent.TButton'

listbox_main = MultiColumnListbox()

root.mainloop()
