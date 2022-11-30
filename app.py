import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter import *
from nade_loader_v2 import *
import pandas as pd


class MultiColumnListbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""

    def __init__(self):
        self.tree = None
        self._setup_widgets()
        self._build_tree()

    def _setup_widgets(self):
        s = """\click on header to sort by that column
to change width of column drag boundary
        """
        msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
                        padding=(10, 2, 10, 6), text=s)
        msg.pack(fill='x')
        container = ttk.Frame()
        container.pack(fill='both', expand=True)
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=car_header, show="headings")
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
        for col in car_header:
            self.tree.heading(col, text=col.title(),
                              command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                             width=tkFont.Font().measure(col.title()))

        for item in car_list:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(car_header[ix], width=None) < col_w:
                    self.tree.column(car_header[ix], width=col_w)


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

# the test data ...


# create the root window
root = tk.Tk()
root.title('Nadebook')

top_frame = Frame(root, width=800, height=200)
top_frame.grid(row=0, column=0, padx=10, pady=5, sticky='w')

bottom_frame = Frame(root, width=800, height=200)
bottom_frame.grid(row=1, column=0, padx=10, pady=5)

# create a list box
u_maps, u_playlists, u_created_by = generate_filters()

var_maps = tk.Variable(value=u_maps)
listbox_maps = tk.Listbox(
    top_frame,
    listvariable=var_maps,
    height=6,
    selectmode=tk.EXTENDED,
    exportselection=0,
)
listbox_maps.grid(row=1, column=0)

var_playlists = tk.Variable(value=u_playlists)
listbox_playlists = tk.Listbox(
    top_frame,
    listvariable=var_playlists,
    height=6,
    selectmode=tk.EXTENDED,
    exportselection=0
)
listbox_playlists.grid(row=1, column=1)

var_created_by = tk.Variable(value=u_created_by)
listbox_created_by = tk.Listbox(
    top_frame,
    listvariable=var_created_by,
    height=6,
    selectmode=tk.EXTENDED,
    exportselection=0
)
listbox_created_by.grid(row=1, column=2)


def items_selected():
    # get all selected indices
    selected_indices = listbox_maps.curselection()
    # get selected items
    selected_maps = ",".join([listbox_maps.get(i) for i in selected_indices])
    msg = f'You selected: {selected_maps}'
    print(msg)


Button(top_frame, text='Apply', command=items_selected).grid(row=2, column=1)

# root = Tk()

f = open('data.txt')
data = json.load(f)
df = pd.DataFrame.from_dict(data)


car_header = df.columns.values
car_list = df.values.tolist()

listbox = MultiColumnListbox()
root.mainloop()
