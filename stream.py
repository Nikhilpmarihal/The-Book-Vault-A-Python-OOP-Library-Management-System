# app.py
import streamlit as st
from main import Library

# ---------- Config ----------
st.set_page_config(page_title="Library Management", layout="wide")
st.title("📚 Library Management (Streamlit)")

# Initialize Library
lib = Library()

# ---------- Helpers ----------
def reload_data():
    # Force reload from disk in case of external changes (optional, but good for consistency)
    # Since Library loads on init, we might want a reload method if we expect concurrent edits.
    # For now, we rely on the shared static data in Library class.
    # But since Streamlit reruns the script, 'lib' is re-instantiated. 
    # Library class loads data at class level, but we should ensure it refreshes if needed.
    # Actually, Library.data is a class attribute, so it persists across instantiations in the same process 
    # if the module isn't reloaded. However, Streamlit execution model might reload modules.
    # To be safe, let's just use lib.data directly.
    pass

# ---------- Sidebar ----------
menu = st.sidebar.selectbox("Choose action", [
    "Dashboard",
    "Add Book",
    "List Books",
    "Add Member",
    "List Members",
    "Borrow Book",
    "Return Book",
])

# ---------- Dashboard ----------
if menu == "Dashboard":
    st.subheader("Library overview")
    books = Library.data["books"]
    members = Library.data["members"]
    
    total_books = sum(b.get("total_copies", 0) for b in books)
    available_books = sum(b.get("available_copies", 0) for b in books)
    total_members = len(members)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total book copies", total_books)
    col2.metric("Available copies", available_books)
    col3.metric("Total members", total_members)

    st.markdown("### Recent Books")
    recent = sorted(books, key=lambda x: x.get("added_on",""), reverse=True)[:10]
    if recent:
        st.table([{
            "id": b["id"],
            "title": b["title"],
            "author": b["author"],
            "available/total": f"{b.get('available_copies',0)}/{b.get('total_copies',0)}",
            "added_on": b.get("added_on","")
        } for b in recent])
    else:
        st.write("No books yet.")

# ---------- Add Book ----------
elif menu == "Add Book":
    st.subheader("Add a new book")
    with st.form("add_book"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        copies = st.number_input("Number of copies", min_value=1, step=1, value=1)
        submitted = st.form_submit_button("Add book")
        
        if submitted:
            if title and author:
                success = lib.add_book(title, author, int(copies))
                if success:
                    st.success(f"Book added: {title}")
                else:
                    st.error("Failed to add book.")
            else:
                st.error("Please fill in all fields.")

# ---------- List Books ----------
elif menu == "List Books":
    st.subheader("All books")
    books = Library.data["books"]
    if not books:
        st.info("No books available.")
    else:
        st.dataframe(books, use_container_width=True)

# ---------- Add Member ----------
elif menu == "Add Member":
    st.subheader("Add a new member")
    with st.form("add_member"):
        name = st.text_input("Member name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Add member")
        
        if submitted:
            if name and email:
                success = lib.add_member(name, email)
                if success:
                    st.success(f"Member added: {name}")
                else:
                    st.error("Failed to add member.")
            else:
                st.error("Please fill in all fields.")

# ---------- List Members ----------
elif menu == "List Members":
    st.subheader("All members")
    members = Library.data["members"]
    if not members:
        st.info("No members yet.")
    else:
        st.dataframe(members, use_container_width=True)

# ---------- Borrow Book ----------
elif menu == "Borrow Book":
    st.subheader("Borrow a book")
    if not Library.data["members"]:
        st.warning("Add members first.")
    elif not Library.data["books"]:
        st.warning("Add books first.")
    else:
        member_option = st.selectbox("Select member", [f"{m['id']} — {m['name']}" for m in Library.data["members"]])
        
        available_books = [b for b in Library.data["books"] if b.get("available_copies", 0) > 0]
        if not available_books:
            st.info("No available copies to borrow.")
        else:
            book_option = st.selectbox("Select book", [f"{b['id']} — {b['title']} ({b.get('available_copies',0)} avail)" for b in available_books])
            
            if st.button("Borrow"):
                mid = member_option.split(" — ")[0]
                bid = book_option.split(" — ")[0]
                
                if lib.borrow(mid, bid):
                    st.success("Book borrowed successfully!")
                    st.rerun()
                else:
                    st.error("Failed to borrow book (maybe limit reached or invalid ID).")

# ---------- Return Book ----------
elif menu == "Return Book":
    st.subheader("Return a borrowed book")
    if not Library.data["members"]:
        st.info("No members")
    else:
        member_option = st.selectbox("Select member", [""] + [f"{m['id']} — {m['name']}" for m in Library.data["members"]])
        
        if member_option:
            mid = member_option.split(" — ")[0]
            member = next((m for m in Library.data["members"] if m["id"] == mid), None)
            
            if member and member.get("borrowed"):
                borrowed = member["borrowed"]
                choice = st.selectbox("Select borrowed book to return", [f"{b['title']} ({b['book_id']})" for b in borrowed])
                
                if st.button("Return"):
                    bid = choice.split(" (")[1].replace(")", "")
                    if lib.return_book(mid, bid):
                        st.success("Book returned successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to return book.")
            else:
                st.info("This member has no borrowed books.")

