import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from CTkMessagebox import CTkMessagebox

from CTkScrollableDropdown import CTkScrollableDropdown
from collections import defaultdict
import sys
import os
from customtkinter import TOP, NE, NW


def callback(sv, combobox):
    if sv.get().isnumeric():
        max_val = int(sv.get())
        combobox.configure(values=[str(i) for i in range(max_val+1)])
    else:
        combobox.configure(values=[])


def add(task_name="", mult="1"):
    frame = ctk.CTkFrame(container)
    frame.pack(pady=3, fill="both", expand=True)
    points = ctk.CTkComboBox(frame, values=["1", "2", "3"], width=70)
    points.set(mult)

    #sv = ctk.StringVar()
    #sv.trace("w", lambda name, index, mode, sv=sv: callback(sv, points))

    task = ctk.CTkEntry(frame, placeholder_text="task", width=50)
    task.insert(0, task_name)
    task.pack(side="left", padx=5)

    # max_points = ctk.CTkEntry(frame, textvariable=sv, width=30)
    max_points = ctk.CTkEntry(frame, width=30)
    # max_points.insert(0, max_point_value)
    max_points.pack(side="left", padx=5)

    points.pack(side="left", padx=5)

    star = ctk.CTkCheckBox(frame, text="⭐", width=50)
    star.pack(side="left", padx=5)

    comment_frame = ctk.CTkFrame(frame)
    comment_frame.pack(pady=3, fill="both", expand=True)

    sub_frame = ctk.CTkFrame(comment_frame)
    sub_frame.pack(pady=3, fill="both", expand=True)

    comment = ctk.CTkEntry(sub_frame, width=400, placeholder_text="comment")
    comment.pack(side="left", padx=5, fill="both", expand=True)

    add_btn = ctk.CTkButton(sub_frame, text="+", command= lambda: sub_add(comment_frame), width=30)
    add_btn.pack(side="left", padx=5)

    drop = CTkScrollableDropdown(comment, values=[], command=lambda e: fill_text(e, comment), autocomplete=True)
    box_to_dropdown[comment] = drop


def sub_add(comment_container):
    sub_frame = ctk.CTkFrame(comment_container)
    sub_frame.pack(pady=3, fill="both", expand=True)
    comment = ctk.CTkEntry(sub_frame, width=400, placeholder_text="comment")
    comment.pack(side="left", padx=5, fill="both", expand=True)

    index = len(comment_container.winfo_children()) - 1
    add_btn = ctk.CTkButton(sub_frame, text="-", command=lambda: sub_remove(comment_container, index), width=30)
    add_btn.pack(side="left", padx=5)


def sub_remove(comment_container, index):
    print(index)
    comment_container.winfo_children()[index].destroy()


def fill_text(text, text_field):
    text_field.delete(0, 'end')
    text_field.insert(0, text)


def remove():
    if container.winfo_children():
        container.winfo_children()[-1].destroy()


def reset():
    name.delete(0, 'end')
    for child in container.winfo_children():
        for comment in child.winfo_children()[4].winfo_children()[1:]:
            comment.destroy()
        points = child.winfo_children()[2]
        points.delete(0, 'end')
        comment = child.winfo_children()[4].winfo_children()[0].winfo_children()[0]
        comment.delete(0, 'end')


def set_max():
    for child in container.winfo_children():
        points = child.winfo_children()[2]
        points.delete(0, 'end')
        points.insert(0, "1")
        star = child.winfo_children()[3]
        star.select()


def generate():
    try:
        with open(f"{save_path}/{name.get()}.txt", "w") as f:
            total_points = 0
            acquired_points = 0
            acquired_stars = 0
            for child in container.winfo_children():
                task = child.winfo_children()[1].get()
                points = child.winfo_children()[2].get()
                point_mult = float(child.winfo_children()[0].get())

                total_points += point_mult

                acquired_points += int(points) * point_mult
                star = "*" if child.winfo_children()[3].get() else ""
                acquired_stars += int(points) * point_mult if star == "*" else 0

                comments = child.winfo_children()[4]
                weighting = f"({point_mult}x Gewichtung)" if point_mult > 1 else ""
                f.write(f"{task}) {points}{star}/1 {weighting}\n")
                for comment_frame in comments.winfo_children():
                    comment_entry = comment_frame.winfo_children()[0]
                    comment = comment_entry.get()
                    if comment != "":
                        f.write(f"- {comment}\n")
                    # save suggestion
                    # if comment:
                    #     comment_entry = child.winfo_children()[3]
                    #     suggestion_map[comment_entry].add(comment)
                    #     if suggestion_on:
                    #         box_to_dropdown[comment_entry].configure(values=suggestion_map[comment_entry])
#
                    # if comment != "":
                    #     f.write(f"{task}) {curr_points}/{max_points}: {comment}\n")
                    # else:
                    #     f.write(f"{task}) {curr_points}/{max_points}\n")
            f.write(f"Total: {int(acquired_points)}/{total_points}\n")
            f.write(f"Total *: {int(acquired_stars)}*/{total_points}*")
    except Exception as e:
        print("generation failed")
        print(e)
        CTkMessagebox(message="Something went wrong please try again.", title="Error", icon="cancel")


def save_task():
    f = filedialog.asksaveasfile(mode='w', defaultextension=".bus")
    if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    for child in container.winfo_children():
        task = child.winfo_children()[1].get()
        point_mult = int(child.winfo_children()[0].get())
        f.write(f"{task}|{point_mult}\n")
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
            task, point_mult = line.split("|")
            add(task, point_mult)


# def switch_event():
#     suggestion_on = comment_prompt_toggle.get()
#     for box, drop in box_to_dropdown.items():
#         drop.configure(values=suggestion_map[box] if suggestion_on else [])


def set_save_path():
    global save_path
    directory = filedialog.askdirectory()
    save_path = directory
    print(directory)


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

    save_path = "."

    app = ctk.CTk()
    app.geometry("800x600")

    point_map = {}
    name = ctk.CTkEntry(app, placeholder_text="File Name")
    name.pack(pady=10)

    # Reset Button
    image = ctk.CTkImage(light_image=Image.open(resource_path("Assets/reset.png")), dark_image=Image.open(resource_path("Assets/reset.png")), size=(15, 15))
    reset_button = ctk.CTkButton(app, image=image, text="", width=20, height=30, command=reset)
    reset_button.pack(side = TOP, anchor = NW, pady=5, padx=5)# .place(x=0, y=0)

    # Path Button
    save_path_button = ctk.CTkButton(app, text="set path", command=set_save_path, width=100)
    save_path_button.pack(side = TOP, anchor = NE, pady=5, padx=5)#.place(x=400, y=0)

    # Max PointsButton
    max_points_button = ctk.CTkButton(app, text="MAX", width=20, command=set_max)
    max_points_button.pack(side = TOP, anchor = NW, pady=5, padx=5)#.place(x=0, y=35)

    # Suggestions Toggle
    # suggestion_on = True
    # comment_prompt_toggle = ctk.CTkSwitch(app, text="Use comment suggestion", command=switch_event)
    # comment_prompt_toggle.select()
    # comment_prompt_toggle.pack(side = TOP, anchor = NW, pady=5, padx=5)# .place(x=0, y=70)

    # Add Button
    add_button = ctk.CTkButton(app, text="Add", command=add)
    add_button.pack(pady=5)
    remove_button = ctk.CTkButton(app, text="Remove Last", command=remove)
    remove_button.pack(pady=5)

    # Container
    container = ctk.CTkScrollableFrame(app, width=500)
    container.pack(fill="both", expand=True)

    # Generate Button
    generate = ctk.CTkButton(app, text="Generate", command=generate)
    generate.pack(pady=5)

    # Save/Load Buttons
    setting_frame = ctk.CTkFrame(app)
    setting_frame.pack(pady=5)
    save = ctk.CTkButton(setting_frame, text="save", command=save_task)
    save.pack(side="left", padx=2)
    load = ctk.CTkButton(setting_frame, text="load", command=load_task)
    load.pack(side="left", padx=2)

    app.mainloop()
