import sqlite3
from datetime import datetime

class Database:
  def __init__(self, db_name):
    self.conn = sqlite3.connect(db_name)
    self.create_tables()


  def create_tables(self):
    cursor = self.conn.cursor()
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
          user_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          phone TEXT NOT NULL,
          email TEXT NOT NULL,
          address TEXT NOT NULL,
          password TEXT NOT NULL,
          role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
        )
    ''')

    # Food items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_items (
          food_id INTEGER PRIMARY KEY AUTOINCREMENT,
          type TEXT NOT NULL CHECK(type IN ('veg', 'non-veg')),
          name TEXT NOT NULL UNIQUE,
          price REAL NOT NULL
        )
    ''')

   # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            date TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY(user) REFERENCES users(username)
        )
    ''') 

  # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_id INTEGER,
            food_id INTEGER,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            PRIMARY KEY(order_id, food_id),
            FOREIGN KEY(order_id) REFERENCES orders(order_id),
            FOREIGN KEY(food_id) REFERENCES food_items(food_id)
        )
    ''')
    self.conn.commit()


  def execute_query(self, query, params=(), fetch=False):
    try:
      cursor = self.conn.cursor()
      cursor.execute(query, params)
      if fetch:
        return cursor.fetchall()
      self.conn.commit()
      return True
    except sqlite3.Error as e:
      print(f"Database error: {e}")
      return False


class User:
  def __init__(self, email, role, db_object):
    self.email = email
    self.role = role
    self.db = db_object

class Admin(User):
  def __init__(self, email, db_object):
     super().__init__(email, 'admin', db_object)

  def manage_user(self):
    while True:
      print("\n----------------------- User Management ----------------------")
      print("1. Add User\n2. View User\n3. Update User\n4. Delete User\n5. Back")
      choice = input("Enter choice: ")

      if choice == '1':
        print("\n----------------------- Add New User -----------------------")
        name = input("Enter name: ").strip()
        phone = input("Enter phone no.: ").strip()
        email = input("Enter email: ").strip()

        # Check if username exists
        existing = self.db.execute_query(
          "SELECT email FROM users WHERE email = ?",
          (email,),
          fetch=True
        )
        if existing:
          print("Username already exists!")
          return False
        
        address = input("Enter address: ").strip()
        password = input("Enter password: ").strip()
        
        role = input("Enter role (admin/user): ").strip().lower()
        if role not in ['admin', 'user']:
            print("Invalid role!")
            return False
            
        self.db.execute_query(
            "INSERT INTO users (name, phone, email, address, password, role) VALUES (?, ?, ?, ?, ?, ?)",
            (name, phone, email, address, password, role)
        )
        print("User added!" if self.db.conn.total_changes else "Failed to add user")
      
      elif choice == '2':
        self.view_user()

      elif choice == '3':
        user_id = self._get_valid_user_id()
        if user_id is None: continue

        new_name = input("Enter new name(Keep to blank): ").strip()
        new_phone = input("Enter new phone no.(Keep to blank): ").strip()
        new_email = input("Enter new email(Keep to blank): ").strip()

        # Check if username exists
        existing = self.db.execute_query(
          "SELECT email FROM users WHERE email = ?",
          (new_email,),
          fetch=True
        )
        if existing:
          print("Username already exists!")
          return False
        
        new_address = input("Enter new address(Keep to blank): ").strip()
        
        updates = []
        params = []

        if new_name:
          updates.append("name = ?")
          params.append(new_name)
        if new_phone:
          updates.append("phone = ?")
          params.append(new_phone)
        if new_email:
          updates.append("email = ?")
          params.append(new_email)
        if new_address:
          updates.append("address = ?")
          params.append(new_address)

        if updates:
          params.append(user_id)
          query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
          self.db.execute_query(query, params)
          print("User updated!" if self.db.conn.total_changes else "No changes made")

      elif choice == '4':
        user_id = self._get_valid_user_id()
        if user_id is None: continue

        confirm = input("Are your sure want to delete?(y/n):")
        if confirm == "y":
          self.db.execute_query(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
          )
          print("User deleted!" if self.db.conn.total_changes else "User not found")

      elif choice == '5':
        break
      else:
        print("Wrong choice...!")

  def manage_food_items(self):
    while True:
      print("\n------------------------ Food Management -----------------------")
      print("1. Add Food Item\n2. View Menu\n3. Update Item\n4. Delete Item\n5. Back")
      choice = input("Enter choice: ")
      
      if choice == '1':
        type = input("Enter Food type (veg/non-veg): ").strip().lower()
        if type not in ['veg', 'non-veg']:
          print("Invalid type!")
          return False
        name = input("Enter food name: ").strip()
        price = self._get_valid_price()
        if price is None: continue
        
        self.db.execute_query(
          "INSERT INTO food_items (type, name, price) VALUES (?, ?, ?)",
          (type, name, price)
        )
        print("Food item added!" if self.db.conn.total_changes else "Failed to add item")
          
      elif choice == '2':
        self.view_menu()
          
      elif choice == '3':
          food_id = self._get_valid_id()
          if food_id is None: continue

          new_type = input("Enter new Food type (veg/non-veg)(blank to keep): ").strip().lower()
          new_name = input("Enter new name (blank to keep): ").strip()
          new_price = self._get_valid_price(allow_blank=True)
          
          updates = []
          params = []

          if new_type:
            updates.append("type = ?")
            params.append(new_type)
          if new_name:
            updates.append("name = ?")
            params.append(new_name)
          if new_price is not None:
            updates.append("price = ?")
            params.append(new_price)
          
          if updates:
            params.append(food_id)
            query = f"UPDATE food_items SET {', '.join(updates)} WHERE food_id = ?"
            self.db.execute_query(query, params)
            print("Item updated!" if self.db.conn.total_changes else "No changes made")
              
      elif choice == '4':
        food_id = self._get_valid_id()
        if food_id is None: continue
        
        confirm = input("Are your sure want to delete?(y/n):")
        if confirm == "y":
          self.db.execute_query(
            "DELETE FROM food_items WHERE food_id = ?",
            (food_id,)
          )
          print("Item deleted!" if self.db.conn.total_changes else "Item not found")
            
      elif choice == '5':
        break
      else:
        print("Wrong choice...!")

  def _get_valid_price(self, allow_blank=False):
    while True:
      try:
        value = input("Enter price: ").strip()
        if allow_blank and not value:
          return None
        return float(value)
      except ValueError:
        print("Invalid price! Please enter a valid number.")

  def _get_valid_id(self):
    while True:
      try:
        return int(input("Enter food ID:"))
      except ValueError:
        print("Invalid ID! Please enter a number.")

  def _get_valid_user_id(self):
    while True:
      try:
        return int(input("Enter user ID:"))
      except ValueError:
        print("Invalid ID! Please enter a number.")

  def view_menu(self):
    menu = self.db.execute_query(
      "SELECT food_id, type, name, price FROM food_items",
      fetch=True
    )
    print("\n----------------------- Veg Food Items ------------------------")
    max_length = 0
    for item in menu:
        if max_length <= len(item[2]):
          max_length = len(item[2])
    max_length += 30
    for item in menu:
      if item[1] == 'veg':
        length = len(item[2])
        joint_space = max_length - length
        space = ''
        for i in range(0, joint_space):
          space += ' '
        print(f"{item[0]}     {item[2]+space}  Rs {item[3]:.2f}")
      
    print("\n---------------------- Non-veg Food Items ---------------------")
    for item in menu:
        if item[1] == 'non-veg':
          length = len(item[2])
          joint_space = max_length - length
          space = ''
          for i in range(0, joint_space):
            space += ' '
          print(f"{item[0]}     {item[2]+space}  Rs {item[3]:.2f}")

  def view_user(self):
    users = self.db.execute_query(
      "SELECT user_id, name, phone, email, address, role FROM users",
      fetch=True
    )
    print("\n------------------------- User List ---------------------------")
    name_len = 0
    phn_len = 0
    email_len = 0
    address_len = 0
    for user in users:
      if name_len <= len(user[1]):
        name_len = len(user[1])
      if phn_len <= len(user[2]):
        phn_len = len(user[2])
      if email_len <= len(user[3]):
        email_len = len(user[3])
      if address_len <= len(user[4]):
        address_len = len(user[4])
    name_len += 4
    phn_len += 4
    email_len += 4
    address_len += 4

    for user in users:
      name_length = len(user[1])
      phn_length = len(user[2])
      email_length = len(user[3])
      add_length = len(user[4])
      name_space = ''
      phn_space = ''
      email_space = ''
      add_space = ''
      name_join = name_len - name_length
      phn_join = phn_len - phn_length
      email_join = email_len - email_length
      add_join = address_len - add_length
      for i in range(0, name_join):
        name_space += ' '
      for i in range(0, phn_join):
        phn_space += ' '
      for i in range(0, email_join):
        email_space += ' '
      for i in range(0, add_join):
        add_space += ' '
      print(f"{user[0]}    {user[1]+name_space}  {user[2]+phn_space}  {user[3]+email_space}  {user[4]+add_space}  {user[5]}")
    

class Waiter(User):
  def __init__(self, email, db_object):
    super().__init__(email, 'user', db_object)

  def place_order(self):
    menu = self.db.execute_query(
      "SELECT food_id, type, name, price FROM food_items",
      fetch=True
    )
    if not menu:
      print("No items in menu!")
      return

    print("\n----------------------- Veg Food Items ------------------------")
    max_length = 0
    for item in menu:
      if max_length <= len(item[2]):
        max_length = len(item[2])
    max_length += 30
    for item in menu:
      if item[1] == 'veg':
        length = len(item[2])
        joint_space = max_length - length
        space = ''
        for i in range(0, joint_space):
          space += ' '
        print(f"{item[0]}     {item[2]+space}  Rs {item[3]:.2f}")
      
    print("\n---------------------- Non-veg Food Items ---------------------")
    for item in menu:
      if item[1] == 'non-veg':
        length = len(item[2])
        joint_space = max_length - length
        space = ''
        for i in range(0, joint_space):
          space += ' '
        print(f"{item[0]}     {item[2]+space}  Rs {item[3]:.2f}")
            
    order_items = []
    while True:
      try:
        food_id = int(input("\nEnter food ID (to finish order enter 0): "))
        if food_id == 0:
          break
              
        item = next((x for x in menu if x[0] == food_id), None)
        if not item:
          print("Invalid ID!")
          continue
            
        qty = int(input("Enter quantity: "))
        if qty < 1:
          print("Quantity must be at least 1!")
          continue
            
        order_items.append({
          'food_id': food_id,
          'name': item[2],
          'price': item[3],
          'quantity': qty
        })
      except ValueError:
        print("Invalid input!")
          
    if not order_items:
      print("No items selected!")
      return
            
    total = sum(item['price'] * item['quantity'] for item in order_items)
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    # Start transaction
    self.db.conn.execute("BEGIN TRANSACTION")
    try:
      # Insert order
      self.db.execute_query(
        "INSERT INTO orders (user, date, total) VALUES (?, ?, ?)",
        (self.email, order_date, total)
      )
      order_id = self.db.conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            
      # Insert order items
      for item in order_items:
        self.db.execute_query(
          "INSERT INTO order_items VALUES (?, ?, ?, ?)",
          (order_id, item['food_id'], item['quantity'], item['price'])
        )
            
      self.db.conn.commit()
      print("\n--------------------------- Bill ------------------------------")
      max_name_len = 0
      max_price_len = 0
      max_q_len = 0
      for item in order_items:
        if max_name_len <= len(item['name']):
          max_name_len = len(item['name'])
        if max_price_len <= len(str(item['price'])):
          max_price_len = len(str(item['price']))
        if max_q_len <= len(str(item['quantity'])):
          max_q_len = len(str(item['quantity']))
      max_name_len += 8
      max_price_len += 2
      max_q_len += 8
      for item in order_items:
        name_len = len(item['name'])
        price_len = len(str(item['price']))
        q_len = len(str(item['quantity']))
        name_space = ''
        price_space = ''
        q_space = ''
        name_join = max_name_len - name_len
        price_join = max_price_len - price_len
        q_join = max_q_len - q_len
        for i in range(0, name_join):
          name_space += ' '
        for i in range(0, price_join):
          price_space += ' '
        for i in range(0, q_join):
          q_space += ' '
        print(f"{item['name']+name_space} Rs {str(item['price'])+price_space}*  {str(item['quantity'])+q_space}Rs {item['price']* item['quantity']:.2f}")
      print(f"\nTotal: Rs {total:.2f}")
            
    except sqlite3.Error:
      self.db.conn.rollback()
      print("Failed to place order!")

class AuthManager:
  def __init__(self, db_object):
    self.db = db_object

  def signup(self):

    print("\n--------------------------- Signup ---------------------------")
    name = input("Enter name: ").strip()
    phone = input("Enter phone no.: ").strip()
    email = input("Enter email: ").strip()

    # Check if username exists
    existing = self.db.execute_query(
      "SELECT email FROM users WHERE email = ?",
      (email,),
      fetch=True
    )
    if existing:
      print("Username already exists!")
      return False
    
    address = input("Enter address: ").strip()
    password = input("Enter password: ").strip()
    
    role = input("Enter role (admin/user): ").strip().lower()
    if role not in ['admin', 'user']:
        print("Invalid role!")
        return False
        
    success = self.db.execute_query(
        "INSERT INTO users (name, phone, email, address, password, role) VALUES (?, ?, ?, ?, ?, ?)",
        (name, phone, email, address, password, role)
    )
    if success:
        print("Signup successful!")
        return True
    print("Signup failed!")
    return False

  def login(self):
    print("\n---------------------------- Login ---------------------------")
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    
    user = self.db.execute_query(
      "SELECT email, role FROM users WHERE email = ? AND password = ?",
      (email, password),
      fetch=True
    )
    if user:
      return user[0]  # Returns (email, role)
    print("Invalid credentials!")
    return None


def main():
  db = Database("PythonRestaurant.db")
  auth = AuthManager(db)

  while True:
    print("\n--------------- Welcome to Python Restaurant ----------------")
    print("1. Signup\n2. Login\n3. Exit")
    choice = input("Enter choice: ").strip()
    
    if choice == '1':
        auth.signup()
    elif choice == '2':
        user = auth.login()
        if user:
          email, role = user
          if role == 'admin':
            admin = Admin(email, db)
            while True:
              print("\n------------------------- Admin Panel -----------------------")
              print("1. Manage Food Items\n2. Manage Users\n3. Generate Report\n4. Logout")
              admin_choice = input("Enter choice: ")
              if admin_choice == '1':
                admin.manage_food_items()
              elif admin_choice == '2':
                admin.manage_user()
              elif admin_choice == '3':
                generate_monthly_report(db)
                pass
              elif admin_choice == '4':
                break
              else:
                print("Wrong choice...!")
          else:
            user = Waiter(email, db)
            admin = Admin(email, db)
            while True:
              print("\n------------------------ Waiter Panel ------------------------")
              print("1. View Menu\n2. Place Order\n3. Logout")
              user_choice = input("Enter choice: ")
              if user_choice == '1':
                admin.view_menu()
              elif user_choice == '2':
                user.place_order()
              elif user_choice == '3':
                break
              else:
                print("Wrong choice...!")
    elif choice == '3':
      print("Exiting...")
      break
    else:
      print("Wrong choice...!")

def generate_monthly_report(db):
  month = input("Enter month (MM): ").strip()
  year = input("Enter year (YYYY): ").strip()
  
  # Get total income
  total_income = db.execute_query(
    '''SELECT SUM(total) FROM orders 
    WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?''',
    (month.zfill(2), year),
    fetch=True
  )[0][0] or 0.0
  
  # Get popular items
  popular_items = db.execute_query(
      '''SELECT f.name, SUM(oi.quantity), SUM(oi.quantity * oi.price)
      FROM order_items oi
      JOIN orders o ON oi.order_id = o.order_id
      JOIN food_items f ON oi.food_id = f.food_id
      WHERE strftime('%m', o.date) = ? AND strftime('%Y', o.date) = ?
      GROUP BY f.food_id
      ORDER BY SUM(oi.quantity) DESC''',
      (month.zfill(2), year),
      fetch=True
  )
  
  print(f"\n--------------- Monthly Report ({month}/{year}) --------------------")
  print(f"Total Income: Rs {total_income:.2f}")
  print("\nTop Selling Items")
  for item in popular_items:
    print(f"- {item[0]}: {item[1]} units sold (Rs {item[2]:.2f} revenue)")

if __name__ == "__main__":
  main()