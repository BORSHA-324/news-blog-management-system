import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "usernews"
}

WINDOW_SIZE = "1200x700" 
BG_COLOR = "#f0f4f8"
FRAME_BG = "#ffffff"
BUTTON_COLOR = "#4a90e2"
BUTTON_HOVER = "#357abd"
HEADER_BG = "#2c3e50"
HEADER_FG = "#ffffff"
ACCENT_COLOR = "#3498db"



def get_conn():
    """Establishes and returns a database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        messagebox.showerror("DB Connection Error", str(e))
        return None

def ensure_tables_exist():
    """Creates the User and News tables with updated schema and foreign key."""
    conn = get_conn()
    if not conn:
        return
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS User (
        user_id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(100) UNIQUE NOT NULL, 
        email VARCHAR(100) UNIQUE NOT NULL,
        age INT,
        contact_number VARCHAR(20),
        u_occupation VARCHAR(100)
    ) ENGINE=InnoDB
    """)
   
    cur.execute("""
    CREATE TABLE IF NOT EXISTS News (
        news_id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        title VARCHAR(200),
        body TEXT,
        created_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_user_id_by_username(username):
    """Utility to look up user_id based on username."""
    conn = get_conn()
    if not conn: return None
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM User WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None


def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


ensure_tables_exist()

root = tk.Tk()
root.title("News Blog Management System")
root.geometry(WINDOW_SIZE)
root.configure(bg=BG_COLOR)


style = ttk.Style()
style.theme_use('clam')
style.configure('TFrame', background=BG_COLOR)
style.configure('TLabelframe', background=FRAME_BG, borderwidth=2, relief='solid')
style.configure('TLabelframe.Label', background=FRAME_BG, foreground=HEADER_BG, font=('Arial', 10, 'bold'))
style.configure('TLabel', background=FRAME_BG, foreground='#2c3e50', font=('Arial', 9))
style.configure('TButton', background=BUTTON_COLOR, foreground='white', font=('Arial', 9, 'bold'), borderwidth=1)
style.map('TButton', background=[('active', BUTTON_HOVER)])
style.configure('TEntry', fieldbackground='white', borderwidth=1)
style.configure('Treeview', background='white', foreground='#2c3e50', fieldbackground='white', font=('Arial', 9))
style.configure('Treeview.Heading', background=HEADER_BG, foreground=HEADER_FG, font=('Arial', 9, 'bold'))
style.map('Treeview.Heading', background=[('active', ACCENT_COLOR)])
style.configure('Danger.TButton', background='#e74c3c', foreground='white') # Define Danger style here


main_container = ttk.Frame(root)
main_container.pack(expand=1, fill="both", padx=6, pady=6)


front_page = ttk.Frame(main_container)
front_page.pack(expand=1, fill="both")

front_label = tk.Label(front_page, text="News Blog Management System", 
                       font=('Arial', 28, 'bold'), bg=BG_COLOR, fg=HEADER_BG)
front_label.pack(pady=80)

button_frame = tk.Frame(front_page, bg=BG_COLOR)
button_frame.pack(pady=20)

def show_users_tab():
    front_page.pack_forget()
    tab_users.pack(expand=1, fill="both")
    load_users()
    back_button_users.pack(side="bottom", pady=10)

def show_news_tab():
   
    front_page.pack_forget()
    tab_news.pack(expand=1, fill="both")
    load_news() 
    back_button_news.pack(side="bottom", pady=10)

def show_front_page():
    tab_users.pack_forget()
    tab_news.pack_forget()
    back_button_users.pack_forget()
    back_button_news.pack_forget()
    front_page.pack(expand=1, fill="both")

users_btn = tk.Button(button_frame, text="Manage Users", font=('Arial', 16, 'bold'),
                      bg=BUTTON_COLOR, fg='white', width=20, height=3,
                      relief='raised', borderwidth=3, cursor='hand2',
                      command=show_users_tab)
users_btn.grid(row=0, column=0, padx=20, pady=10)

news_btn = tk.Button(button_frame, text="Manage News", font=('Arial', 16, 'bold'),
                     bg='#27ae60', fg='white', width=20, height=3,
                     relief='raised', borderwidth=3, cursor='hand2',
                     command=show_news_tab)
news_btn.grid(row=0, column=1, padx=20, pady=10)

tab_users = ttk.Frame(main_container)
tab_news = ttk.Frame(main_container)

back_button_users = tk.Button(tab_users, text="← Back to Home", font=('Arial', 10, 'bold'),
                              bg='#e74c3c', fg='white', command=show_front_page,
                              relief='raised', borderwidth=2, cursor='hand2')

back_button_news = tk.Button(tab_news, text="← Back to Home", font=('Arial', 10, 'bold'),
                             bg='#e74c3c', fg='white', command=show_front_page,
                             relief='raised', borderwidth=2, cursor='hand2')




def search_data(search_term):
    """Unified search for Username, News Title, and News Content."""
    term = search_term.strip()
    load_users(term)
    load_news(term)


search_query_var = tk.StringVar()

 
frm_global_search = ttk.LabelFrame(tab_users, text="Search")
frm_global_search.pack(fill="x", padx=8, pady=6)
ttk.Label(frm_global_search, text="Search:").grid(row=0, column=0, padx=6, pady=6, sticky="w")
ttk.Entry(frm_global_search, textvariable=search_query_var, width=50).grid(row=0, column=1, padx=6)
ttk.Button(frm_global_search, text="Search", command=lambda: search_data(search_query_var.get())).grid(row=0, column=2, padx=8)
ttk.Button(frm_global_search, text="Clear Search", command=lambda: [search_query_var.set(""), load_users(), load_news()]).grid(row=0, column=3, padx=8)



frm_user_table = ttk.Frame(tab_users)
frm_user_table.pack(fill="both", expand=1, padx=8, pady=6)
user_cols = ("username", "email", "age", "contact_number")
user_table = ttk.Treeview(frm_user_table, columns=user_cols, show="headings", selectmode="browse")
for c in user_cols:
    user_table.heading(c, text=c.replace('_', ' ').title())
    user_table.column(c, width=200, anchor="w")
user_table.pack(side="left", fill="both", expand=1)

user_table.bind("<Double-1>", lambda e: open_user_management_modal())
scr_u = ttk.Scrollbar(frm_user_table, orient="vertical", command=user_table.yview)
user_table.configure(yscrollcommand=scr_u.set)
scr_u.pack(side="right", fill="y")

ttk.Button(tab_users, text="Add New User", command=lambda: open_user_management_modal(is_new=True)).pack(pady=10)



def load_users(search_term=None):
    """Loads all users, optionally filtered by search_term (username)."""
    for r in user_table.get_children():
        user_table.delete(r)
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    query = "SELECT user_id, username, email, age, contact_number FROM User"
    params = []
    if search_term:
        query += " WHERE username LIKE %s"
        params.append("%" + search_term + "%")
    
    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for r in rows:
        
        user_table.insert("", tk.END, values=r[1:], tags=(r[0],))

def load_news_for_user(user_id, treeview):
    """Load news for a specific user into a given Treeview widget (used by modal)."""
    for r in treeview.get_children():
        treeview.delete(r)
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    cur.execute("""
        SELECT N.news_id, N.title, N.body, N.created_at 
        FROM News N
        WHERE N.user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for r in rows:
        n_id, title, body, created_at = r
        fixed_body = " ".join(body.splitlines())
        # n_id (hidden) in tags[0]
        treeview.insert("", tk.END, values=(title, fixed_body, created_at), tags=(n_id,))

def load_news(search_term=None):
    """Loads all news posts, filtered by search_term (title/body/username)."""
    for r in news_table.get_children():
        news_table.delete(r)
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    
    query = """
        SELECT N.news_id, N.user_id, U.username, N.title, N.body, N.created_at 
        FROM News N
        LEFT JOIN User U ON N.user_id = U.user_id
    """
    params = []
    
    if search_term:
        query += " WHERE N.title LIKE %s OR N.body LIKE %s OR U.username LIKE %s"
        params.extend(["%" + search_term + "%"] * 3)
    
    # Order by creation date descending
    query += " ORDER BY N.created_at DESC"

    cur.execute(query, tuple(params))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for r in rows:
        n_id, u_id, u_name, title, body, created_at = r
        fixed_body = " ".join(body.splitlines())
      
        news_table.insert("", tk.END, values=(u_name, title, fixed_body, created_at), tags=(n_id, u_id))




def add_user_modal(modal, name_var, email_var, age_var, contact_var, occ_var):
    name = name_var.get().strip()
    email = email_var.get().strip()
    age_text = age_var.get().strip()
    occ = occ_var.get().strip()
    contact = contact_var.get().strip()
    
    if not name or not email:
        messagebox.showerror("Validation", "Name and Email are required.", parent=modal)
        return
    if not validate_email(email):
        messagebox.showerror("Validation", "Invalid email address.", parent=modal)
        return
    try:
        age_val = int(age_text) if age_text != "" else None
    except ValueError:
        messagebox.showerror("Validation", "Age must be an integer.", parent=modal)
        return
        
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO User (username, email, age, u_occupation, contact_number) VALUES (%s, %s, %s, %s, %s)",
                    (name, email, age_val, occ, contact))
        conn.commit()
        messagebox.showinfo("Success", "User added successfully.", parent=modal)
    except Error as e:
        messagebox.showerror("DB Error", f"Error adding user: {e}", parent=modal)
    finally:
        cur.close()
        conn.close()
        load_users()

def update_user_modal(modal, u_id, name_var, email_var, age_var, contact_var, occ_var):
    name = name_var.get().strip()
    email = email_var.get().strip()
    age_text = age_var.get().strip()
    occ = occ_var.get().strip()
    contact = contact_var.get().strip()
    
    if not name or not email:
        messagebox.showerror("Validation", "Name and Email are required.", parent=modal)
        return
    if not validate_email(email):
        messagebox.showerror("Validation", "Invalid email address.", parent=modal)
        return
    try:
        age_val = int(age_text) if age_text != "" else None
    except ValueError:
        messagebox.showerror("Validation", "Age must be an integer.", parent=modal)
        return

    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("UPDATE User SET username=%s, email=%s, age=%s, u_occupation=%s, contact_number=%s WHERE user_id=%s",
                    (name, email, age_val, occ, contact, u_id))
        conn.commit()
        messagebox.showinfo("Success", "User updated successfully.", parent=modal)
    except Error as e:
        messagebox.showerror("DB Error", f"Error updating user: {e}", parent=modal)
    finally:
        cur.close()
        conn.close()
        load_users()

def delete_user_modal(u_id):
    if not messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this user and ALL their news posts?"):
        return
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM User WHERE user_id=%s", (u_id,))
        conn.commit()
        messagebox.showinfo("Success", "User and associated news deleted.")
    except Error as e:
        messagebox.showerror("DB Error", f"Error deleting user: {e}")
    finally:
        cur.close()
        conn.close()
        load_users()
        load_news()

def open_user_management_modal(is_new=False):
    """Opens the Toplevel window for user management (CRUD & News by User)."""
    
    selected_item = user_table.selection()
    
    
    if not is_new and not selected_item:
        messagebox.showerror("Selection Error", "Please double-click a user or use the 'Add New User' button.")
        return
    
    
    if is_new:
        u_id = None
        initial_data = ("New User", "", "", "", "")
    else:
        item = user_table.item(selected_item[0])
        u_id = item["tags"][0]
        initial_data = item["values"]
        
    modal = tk.Toplevel(root)
    modal.title(f"Manage User: {initial_data[0]}")
   
    modal.geometry("750x600") 
    modal.resizable(False, False)
    modal.transient(root) 

    
    m_name_var = tk.StringVar(value=initial_data[0] if not is_new else "")
    m_email_var = tk.StringVar(value=initial_data[1] if not is_new else "")
    m_age_var = tk.StringVar(value=str(initial_data[2]) if initial_data[2] else "")
    m_contact_var = tk.StringVar(value=initial_data[3] if not is_new else "")
    
 
    m_occ_var = tk.StringVar()
    if not is_new:
        conn = get_conn()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT u_occupation FROM User WHERE user_id = %s", (u_id,))
            full_data = cur.fetchone()
            m_occ_var.set(full_data[0] if full_data and full_data[0] else "")
            cur.close()
            conn.close()

    
    frm_container = ttk.Frame(modal)
    frm_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    modal.grid_rowconfigure(0, weight=1)
    modal.grid_columnconfigure(0, weight=1)
    
   
    frm_user_details = ttk.LabelFrame(frm_container, text="User Information (Update/Create)")
    frm_user_details.grid(row=0, column=0, sticky="ew", pady=5)
    
    
    frm_user_details.grid_columnconfigure(1, weight=1)

    labels = ["Username", "Email", "Age", "Contact Number", "Occupation"]
    vars_list = [m_name_var, m_email_var, m_age_var, m_contact_var, m_occ_var]
    
    for i, (label, var) in enumerate(zip(labels, vars_list)):
        ttk.Label(frm_user_details, text=label).grid(row=i, column=0, padx=6, pady=4, sticky="w")
        state = 'readonly' if not is_new and label == "Username" else 'normal'
        ttk.Entry(frm_user_details, textvariable=var, width=40, state=state).grid(row=i, column=1, padx=6, pady=4, sticky="ew")

    
    btn_frame_modal = ttk.Frame(frm_user_details)
    btn_frame_modal.grid(row=len(labels), column=0, columnspan=2, pady=10)
    
    if is_new:
        ttk.Button(btn_frame_modal, text="Create User", command=lambda: [add_user_modal(modal, m_name_var, m_email_var, m_age_var, m_contact_var, m_occ_var), modal.destroy()]).pack(side=tk.LEFT, padx=6)
    else:
        ttk.Button(btn_frame_modal, text="Update User", command=lambda: [update_user_modal(modal, u_id, m_name_var, m_email_var, m_age_var, m_contact_var, m_occ_var), modal.destroy()]).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame_modal, text="Delete User", style='Danger.TButton', command=lambda: [delete_user_modal(u_id), modal.destroy()]).pack(side=tk.LEFT, padx=6)

    
    if not is_new:
        frm_user_news = ttk.LabelFrame(frm_container, text=f"News Posts by {initial_data[0]}")
        frm_user_news.grid(row=1, column=0, sticky="nsew", pady=5)
        
      
        frm_container.grid_rowconfigure(1, weight=1)
        frm_container.grid_columnconfigure(0, weight=1)

       
        news_cols_modal = ("title", "body", "created_at")
        user_news_table = ttk.Treeview(frm_user_news, columns=news_cols_modal, show="headings", selectmode="browse")
        
        for c in news_cols_modal:
            user_news_table.heading(c, text=c.replace('_', ' ').title())
            if c == "body":
                 user_news_table.column(c, width=300) 
            else:
                 user_news_table.column(c, width=120, anchor="w")

        
        scr_u_news = ttk.Scrollbar(frm_user_news, orient="vertical", command=user_news_table.yview)
        user_news_table.configure(yscrollcommand=scr_u_news.set)

       
        user_news_table.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        scr_u_news.grid(row=0, column=1, sticky="ns", pady=5)
        
        frm_user_news.grid_rowconfigure(0, weight=1)
        frm_user_news.grid_columnconfigure(0, weight=1)
        
        load_news_for_user(u_id, user_news_table)
        
       
        btn_news_modal = ttk.Frame(frm_container)
        btn_news_modal.grid(row=2, column=0, sticky="ew", pady=5)
        
        
        btn_sub_frame = ttk.Frame(btn_news_modal)
        btn_sub_frame.pack(expand=True) 
        
        
        ttk.Button(btn_sub_frame, text="Add News", 
                   command=lambda: open_news_form_modal(user_news_table, u_id, initial_data[0])).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(btn_sub_frame, text="Edit Selected News", 
                   command=lambda: open_news_form_modal(user_news_table, u_id, initial_data[0], is_edit=True)).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(btn_sub_frame, text="Delete Selected News", 
                   command=lambda: delete_news_modal(user_news_table, u_id)).grid(row=0, column=2, padx=5, pady=5) 
        
      
        modal.update_idletasks() 
        modal.update()

    modal.grab_set() 
    modal.wait_window()



def open_news_form_modal(user_news_table, u_id, username, is_edit=False):
    """Opens a sub-modal for adding/editing news within the User Management Modal."""
    
    news_modal = tk.Toplevel(user_news_table)
    news_modal.title("Edit News" if is_edit else "Add New News")
    news_modal.geometry("600x400")
    news_modal.transient(root)
    news_modal.grab_set()
    
    news_m_title_var = tk.StringVar()
    news_m_body_text = tk.Text(news_modal, height=10, wrap="word")
    
    n_id = None
    
    if is_edit:
        sel = user_news_table.selection()
        if not sel:
            messagebox.showerror("Selection Error", "Select a news post to edit.", parent=news_modal)
            news_modal.destroy()
            return
        item = user_news_table.item(sel[0])
        n_id = item["tags"][0]
        
       
        conn = get_conn()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT title, body FROM News WHERE news_id = %s", (n_id,))
            data = cur.fetchone()
            cur.close()
            conn.close()
            if data:
                news_m_title_var.set(data[0])
                news_m_body_text.insert("1.0", data[1])
    
    ttk.Label(news_modal, text=f"User: {username}").pack(padx=10, pady=5, anchor="w")
    ttk.Label(news_modal, text="Title").pack(padx=10, pady=2, anchor="w")
    ttk.Entry(news_modal, textvariable=news_m_title_var, width=50).pack(padx=10, pady=2, fill="x")
    ttk.Label(news_modal, text="Body").pack(padx=10, pady=2, anchor="w")
    news_m_body_text.pack(padx=10, pady=5, fill="both", expand=1)
    
    if is_edit:
        ttk.Button(news_modal, text="Save Changes", command=lambda: [update_news_modal(news_modal, user_news_table, n_id, u_id, news_m_title_var, news_m_body_text), news_modal.destroy()]).pack(pady=10)
    else:
        ttk.Button(news_modal, text="Add Post", command=lambda: [add_news_modal(news_modal, user_news_table, u_id, news_m_title_var, news_m_body_text), news_modal.destroy()]).pack(pady=10)

def add_news_modal(modal, treeview, u_id, title_var, body_text):
    """Adds news from the sub-modal and REFRESHES DISPLAY (Modal and Main)."""
    title = title_var.get().strip()
    body = body_text.get("1.0", "end").rstrip("\n")
    if not title or not body:
        messagebox.showerror("Validation", "Title and body are required.", parent=modal)
        return
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO News (user_id, title, body, created_at) VALUES (%s, %s, %s, %s)",
                (u_id, title, body, now))
    conn.commit()
    cur.close()
    conn.close()
    load_news_for_user(u_id, treeview) 
    load_news()                        

def update_news_modal(modal, treeview, n_id, u_id, title_var, body_text):
    """Updates news from the sub-modal and REFRESHES DISPLAY (Modal and Main)."""
    title = title_var.get().strip()
    body = body_text.get("1.0", "end").rstrip("\n")
    if not title or not body:
        messagebox.showerror("Validation", "Title and body are required.", parent=modal)
        return
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    cur.execute("UPDATE News SET title=%s, body=%s WHERE news_id=%s",
                (title, body, n_id))
    conn.commit()
    cur.close()
    conn.close()
    load_news_for_user(u_id, treeview) 
    load_news()                        

def delete_news_modal(treeview, u_id):
    """Deletes news from the modal's news list and REFRESHES DISPLAY (Modal and Main)."""
    sel = treeview.selection()
    if not sel:
        messagebox.showerror("Select", "Select news to delete.")
        return
    item = treeview.item(sel[0])
    n_id = item["tags"][0]
            
    if not messagebox.askyesno("Confirm", "Delete selected news?"):
        return
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    cur.execute("DELETE FROM News WHERE news_id=%s", (n_id,))
    conn.commit()
    cur.close()
    conn.close()
    
    load_news_for_user(u_id, treeview)
    load_news()



news_username_var = tk.StringVar()
news_title_var = tk.StringVar()
news_body_text = tk.Text(tab_news, height=12, wrap="word", bg='white', fg='#2c3e50', 
                         font=('Arial', 9), borderwidth=2, relief='solid')

frm_news_form = ttk.LabelFrame(tab_news, text="News Form")
frm_news_form.pack(fill="x", padx=8, pady=6)
ttk.Label(frm_news_form, text="Username").grid(row=0, column=0, padx=6, pady=4, sticky="w") 
ttk.Label(frm_news_form, text="Title").grid(row=0, column=2, padx=6, pady=4, sticky="w")
ttk.Entry(frm_news_form, textvariable=news_username_var, width=16).grid(row=0, column=1, padx=6)

ttk.Entry(frm_news_form, textvariable=news_title_var, width=70).grid(row=0, column=3, padx=6) 

news_body_label = tk.Label(tab_news, text="News Body", bg=FRAME_BG, fg='#2c3e50', font=('Arial', 9))
news_body_label.pack(anchor="w", padx=12)
news_body_text.pack(fill="x", padx=12, pady=6)


btn_frame_n = ttk.Frame(frm_news_form)
btn_frame_n.grid(row=1, column=0, columnspan=4, pady=8)
ttk.Button(btn_frame_n, text="Add News", command=lambda: add_news()).grid(row=0, column=0, padx=6)
ttk.Button(btn_frame_n, text="Update", command=lambda: update_news()).grid(row=0, column=1, padx=6)
ttk.Button(btn_frame_n, text="Delete", command=lambda: delete_news()).grid(row=0, column=2, padx=6)
ttk.Button(btn_frame_n, text="Show All News", command=lambda: [load_news(), clear_news_form()]).grid(row=0, column=3, padx=6)

# News Table (List all news posts)
frm_news_table = ttk.Frame(tab_news)
frm_news_table.pack(fill="both", expand=1, padx=8, pady=6)
news_cols = ("username", "title", "body", "created_at")
news_table = ttk.Treeview(frm_news_table, columns=news_cols, show="headings", selectmode="browse")
for c in news_cols:
    news_table.heading(c, text=c.replace('_', ' ').title())
    if c == "body":
        news_table.column(c, width=400)
    else:
        news_table.column(c, width=150, anchor="w")

news_table.pack(side="left", fill="both", expand=1)
news_table.bind("<<TreeviewSelect>>", lambda e: on_news_select())
scr_n = ttk.Scrollbar(frm_news_table, orient="vertical", command=news_table.yview)
news_table.configure(yscrollcommand=scr_n.set)
scr_n.pack(side="right", fill="y")

def clear_news_form():
    news_username_var.set("")
    news_title_var.set("")
    news_body_text.delete("1.0", "end")

def add_news():
    """Handles adding news from the main News tab using username lookup."""
    username = news_username_var.get().strip()
    title = news_title_var.get().strip()
    body = news_body_text.get("1.0", "end").rstrip("\n")
    
    if not username or not title or not body:
        messagebox.showerror("Validation", "Please enter username, title, and body.")
        return
        
    u_id = get_user_id_by_username(username)
    if u_id is None:
        messagebox.showerror("Validation", f"User '{username}' does not exist.")
        return
        
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cur.execute("INSERT INTO News (user_id, title, body, created_at) VALUES (%s, %s, %s, %s)",
                    (u_id, title, body, now))
        conn.commit()
    except Error as e:
        messagebox.showerror("DB Error", f"Error adding news: {e}")
    finally:
        cur.close()
        conn.close()
    
   
    load_news() 
    clear_news_form()

def on_news_select():
    """Populates the News Form when an item is selected in the main news table."""
    sel = news_table.selection()
    if not sel: return
    item = news_table.item(sel[0])
    values = item["values"]
    u_name, title, body_preview, created_at = values
    
    if not item["tags"]: return 

    n_id = item["tags"][0]
    
    news_username_var.set(u_name)
    news_title_var.set(title)
    
   
    conn = get_conn()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT body FROM News WHERE news_id = %s", (n_id,))
        full_body = cur.fetchone()
        cur.close()
        conn.close()
        
        news_body_text.delete("1.0", "end")
        if full_body:
            news_body_text.insert("1.0", full_body[0])

def update_news():
    """Handles updating news from the main News tab."""
    sel = news_table.selection()
    if not sel:
        messagebox.showerror("Select", "Select news to update.")
        return
    item = news_table.item(sel[0])
    
   
    if not item["tags"]: return 
    n_id = item["tags"][0]
    
    username = news_username_var.get().strip()
    title_val = news_title_var.get().strip()
    body_val = news_body_text.get("1.0", "end").rstrip("\n")

    if not username or not title_val or not body_val:
         messagebox.showerror("Validation", "All fields are required.")
         return
    
    u_id = get_user_id_by_username(username)
    if u_id is None:
        messagebox.showerror("Validation", f"User '{username}' does not exist.")
        return
        
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("UPDATE News SET user_id=%s, title=%s, body=%s WHERE news_id=%s",
                    (u_id, title_val, body_val, n_id))
        conn.commit()
    except Error as e:
        messagebox.showerror("DB Error", f"Error updating news: {e}")
    finally:
        cur.close()
        conn.close()
    
    load_news()
    clear_news_form()

def delete_news():
    """Handles deleting news from the main News tab."""
    sel = news_table.selection()
    if not sel:
        messagebox.showerror("Select", "Select news to delete.")
        return
    item = news_table.item(sel[0])
    
   
    if not item["tags"]: return 
    n_id = item["tags"][0]
    
    if not messagebox.askyesno("Confirm", "Delete selected news?"):
        return
    conn = get_conn()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM News WHERE news_id=%s", (n_id,))
        conn.commit()
    except Error as e:
        messagebox.showerror("DB Error", f"Error deleting news: {e}")
    finally:
        cur.close()
        conn.close()
    
    
    load_news()
    clear_news_form()


load_users()
load_news()

root.mainloop()