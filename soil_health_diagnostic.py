from gui import create_gui
from database import create_database

# Create the database table
create_database()

# Create the main window
window = create_gui()
window.mainloop()