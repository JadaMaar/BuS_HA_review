import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from CTkMessagebox import CTkMessagebox
from CTkScrollableDropdown import CTkScrollableDropdown
from collections import defaultdict
import sys
import os


def callback(sv, combobox):
    if sv.get().isnumeric():
        max_val = int(sv.get())
        combobox.configure(values=[str(i) for i in range(max_val+1)])
    else:
        combobox.configure(values=[])


def add(task_name="", max_point_value=""):
    frame = ctk.CTkFrame(container)
    frame.pack(pady=3)
    points = ctk.CTkComboBox(frame, values=[], width=70)
    points.set("")

    sv = ctk.StringVar()
    sv.trace("w", lambda name, index, mode, sv=sv: callback(sv, points))

    task = ctk.CTkEntry(frame, placeholder_text="task", width=50)
    task.insert(0, task_name)
    task.pack(side="left", padx=5)

    max_points = ctk.CTkEntry(frame, textvariable=sv, width=30)
    max_points.insert(0, max_point_value)
    max_points.pack(side="left", padx=5)

    points.pack(side="left", padx=5)

    comment = ctk.CTkEntry(frame, width=400, placeholder_text="comment")
    comment.pack(side="left", padx=5)

    drop = CTkScrollableDropdown(comment, values=[], command=lambda e: fill_text(e, comment), autocomplete=True)
    box_to_dropdown[comment] = drop


def fill_text(text, text_field):
    text_field.delete(0, 'end')
    text_field.insert(0, text)


def remove():
    if container.winfo_children():
        container.winfo_children()[-1].destroy()


def reset():
    name.delete(0, 'end')
    for child in container.winfo_children():
        curr_points = child.winfo_children()[0]
        curr_points.set('')
        comment = child.winfo_children()[3]
        comment.delete(0, 'end')


def set_max():
    for child in container.winfo_children():
        max_points = child.winfo_children()[2].get()
        curr_points = child.winfo_children()[0]
        curr_points.set(max_points)


def generate():
    try:
        with open(f"{name.get()}.txt", "w") as f:
            total_points = 0
            acquired_points = 0
            for child in container.winfo_children():
                task = child.winfo_children()[1].get()
                max_points = child.winfo_children()[2].get()
                total_points += int(max_points)
                curr_points = child.winfo_children()[0].get()
                acquired_points += float(curr_points)
                comment = child.winfo_children()[3].get()

                # save suggestion
                if comment:
                    comment_entry = child.winfo_children()[3]
                    suggestion_map[comment_entry].add(comment)
                    if suggestion_on:
                        box_to_dropdown[comment_entry].configure(values=suggestion_map[comment_entry])

                if comment != "":
                    f.write(f"{task}) {curr_points}/{max_points}: {comment}\n")
                else:
                    f.write(f"{task}) {curr_points}/{max_points}\n")
            f.write(f"Total: {acquired_points}/{total_points}")
    except:
        print("generation failed")
        CTkMessagebox(message="Something went wrong please try again.", title="Error", icon="cancel")


def save_task():
    f = filedialog.asksaveasfile(mode='w', defaultextension=".bus")
    if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    for child in container.winfo_children():
        task = child.winfo_children()[1].get()
        max_points = child.winfo_children()[2].get()
        f.write(f"{task}|{max_points}\n")
    f.close()


def load_task():
    file_path = filedialog.askopenfilename()
    if file_path == "":
        return
    if not file_path.endswith(".bus"):
        CTkMessagebox(message="Selected file had the wrong datatype. It must be a .bus file.", title="Error", icon="cancel")
        return
    # remove all prior existing tasks and load one from file
    while container.winfo_children():
        remove()
    with open(file_path, "r") as f:
        file = f.readlines()
        for line in file:
            line = line.strip("\n")
            task, max_point = line.split("|")
            add(task, max_point)


def switch_event():
    suggestion_on = comment_prompt_toggle.get()
    for box, drop in box_to_dropdown.items():
        drop.configure(values=suggestion_map[box] if suggestion_on else [])


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # remembers previously used comments for each task
    # used comments will be added everytime the "Generate" button is clicked
    suggestion_map = defaultdict(set)
    box_to_dropdown = dict()

    app = ctk.CTk()

    point_map = {}
    name = ctk.CTkEntry(app, placeholder_text="File Name")
    name.pack()

    image = ctk.CTkImage(light_image=Image.open(resource_path("Assets/reset.png")), dark_image=Image.open(resource_path("Assets/reset.png")), size=(15, 15))
    reset_button = ctk.CTkButton(app, image=image, text="", width=20, height=30, command=reset)
    reset_button.place(x=0, y=0)

    max_points_button = ctk.CTkButton(app, text="MAX", width=20, command=set_max)
    max_points_button.place(x=0, y=35)

    suggestion_on = True
    comment_prompt_toggle = ctk.CTkSwitch(app, text="Use comment suggestion", command=switch_event)
    comment_prompt_toggle.select()
    comment_prompt_toggle.place(x=0, y=70)

    add_button = ctk.CTkButton(app, text="Add", command=add)
    add_button.pack(pady=5)
    remove_button = ctk.CTkButton(app, text="Remove Last", command=remove)
    remove_button.pack(pady=5)

    container = ctk.CTkScrollableFrame(app, width=500)
    container.pack()

    generate = ctk.CTkButton(app, text="Generate", command=generate)
    generate.pack(pady=5)

    setting_frame = ctk.CTkFrame(app)
    setting_frame.pack(pady=5)
    save = ctk.CTkButton(setting_frame, text="save", command=save_task)
    save.pack(side="left", padx=2)
    load = ctk.CTkButton(setting_frame, text="load", command=load_task)
    load.pack(side="left", padx=2)

    app.mainloop()
