import tkinter as tk
from tkinter import ttk

import sqlite3

class Product:
    
    db_name= 'database.db'
    
    def __init__(self,window) -> None:
        self.__window=window
        self.__window.title("Sistema de Gestion de Inventarios")
        
        # Creating container
        frame= tk.LabelFrame(self.__window, text="Agregar Producto al Inventario:")
        frame.grid(row=0, column=0, columnspan=3, pady=20)
        
        # Creating name input
        tk.Label(frame, text="Nombre del producto:").grid(row=1,column=0)
        self.__name= tk.Entry(frame)
        self.__name.focus()                        # Focus in name input
        self.__name.grid(row=1,column=1)
        
        #Creating price input
        tk.Label(frame, text="Precio por unidad:").grid(row=2,column=0)
        self.__price= tk.Entry(frame)
        self.__price.grid(row=2,column=1)
        
        #Creating stock input
        tk.Label(frame,text="Stock").grid(row=3,column=0)
        self.__stock= tk.Entry(frame)
        self.__stock.grid(row=3,column=1)
        
        #Button add product
        tk.Button(frame,text="Guardar Producto", command=self.add_product).grid(row=4, columnspan=2,sticky= tk.W + tk.E )
        
        #Output Messages
        self.__message=tk.Label(text='', fg='red')
        self.__message.grid(row=3,column=0,columnspan=2, sticky= tk.W + tk.E)
        

        #Table
        self.__tree=ttk.Treeview(height=10, column=("#1", "#2"))
        self.__tree.grid(row=5,column=0, columnspan=2)
        self.__tree.heading('#0',text="Nombre", anchor= tk.CENTER)
        self.__tree.heading('#1',text="Precio por unidad", anchor= tk.CENTER)
        self.__tree.heading('#2', text="Stock", anchor= tk.CENTER)
        
        #buttons EDIT/DELETE
        ttk.Button(text='ELIMINAR', command=self.delete_product).grid(row=6,column=0,sticky=tk.W+tk.E)
        ttk.Button(text='EDITAR', command=self.edit_product).grid(row=6,column=1,sticky=tk.W+tk.E)
        
        #filling the row
        self.get_products()
        
        #inventory value
        
        tk.Label(text='Valor total del inventario').grid(row=7,column=0)
        
        self.total_cost=tk.Label(textvariable=tk.StringVar(value=self.inventory_value()))
        self.total_cost.grid(row=7,column=1)
        
        
    
    def run_query(self,query,parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor= conn.cursor()
            result=cursor.execute(query,parameters)
            conn.commit()
        return result
    
    def get_products(self):
        #cleaning table
        record= self.__tree.get_children()
        for element in record:
            self.__tree.delete(element)
        
        #quering data
        query= 'SELECT * FROM product ORDER BY name DESC'
        db_rows=self.run_query(query)            
        #filling data
        for row in db_rows:
            self.__tree.insert('', text= row[1], values= (row[2],row[3]), index=0)
     
    # if both imputs aren't empty, return true. REGISTRATION FUNCTIONS.
    def validate_empty_inputs(self):
        return len(self.__name.get())!=0 and len(self.__price.get()) !=0 and len(self.__stock.get())!=0   # use ".get()" to get the input value
    
    def validate_price_stock(self,price,stock):
        return not float(price)<=0 and not int(stock)<=0
    
    def validate_product(self):
        query= 'SELECT * FROM product ORDER BY name DESC'
        db_rows=self.run_query(query)
        condition=True                    
        for row in db_rows:
            if self.__name.get() == row[1]:
                condition=False
                break          
        return condition
    
    def add_product(self):
        if self.validate_empty_inputs():
            if self.validate_product():
                if self.validate_price_stock(self.__price.get(),self.__stock.get()):
                    query='INSERT INTO product VALUES(NULL,?,?,?)'
                    parameters= (self.__name.get(), self.__price.get(), self.__stock.get())
                    self.run_query(query,parameters)
                    self.__message['text']= 'El producto {} ha sido añadido'.format(self.__name.get())
                    self.__name.delete(0,tk.END)
                    self.__price.delete(0,tk.END)
                    self.__stock.delete(0,tk.END)
                else:self.__message['text']='Precio y stock tienen que ser mayores a 0'               
            else:self.__message['text']='{} ya se encuentra en el inventario. Usar opción editar precio/stock'.format(self.__name.get()) 
        else:
            self.__message['text']= 'Nombre, precio por unidad y stock son requeridos'
        self.get_products()
        self.update_inventory_value()
        
    def delete_product(self):
        self.__message['text']=''
        try:
            self.__tree.item(self.__tree.selection())['text'][0]
        except IndexError as e:
            self.__message['text']='Selecciona un producto'
            return
        self.__message['text']=''
        name= self.__tree.item(self.__tree.selection())['text']
        query='DELETE FROM product WHERE name = ?'
        self.run_query(query,(name,))
        self.__message['text']='El producto {} ha sido eliminado'.format(name)
        self.get_products()
        self.update_inventory_value()
        
    def edit_product(self):
        self.__message['text']=''
        try:
            self.__tree.item(self.__tree.selection())['text'][0]
        except IndexError as e:
            self.__message['text']='Selecciona un producto'
            return
        name= self.__tree.item(self.__tree.selection())['text']
        old_price= self.__tree.item(self.__tree.selection())['values'][0]
        old_stock= self.__tree.item(self.__tree.selection())['values'][1]
        self.edit_wind= tk.Toplevel()
        self.edit_wind.title="Editar Precio/Stock"
        
        #old price
        tk.Label(self.edit_wind, text=f'Antiguo valor de {name}:').grid(row=0,column=1)
        tk.Entry(self.edit_wind, textvariable= tk.StringVar(self.edit_wind,value=old_price), state='readonly').grid(row=0, column=2)
        
        #new price
        tk.Label(self.edit_wind, text=f'Nuevo valor de {name}:').grid(row=1,column=1)
        new_price=tk.Entry(self.edit_wind)
        new_price.grid(row=1,column=2)
        
        #old stock
        tk.Label(self.edit_wind,text=f'Antiguo stock de {name}:').grid(row=2,column=1)
        tk.Entry(self.edit_wind, textvariable=tk.StringVar(self.edit_wind,value=old_stock),state='readonly').grid(row=2,column=2)
        
        #new stock
        tk.Label(self.edit_wind, text=f'Nuevo stock de {name}:').grid(row=3,column=1)
        new_stock=tk.Entry(self.edit_wind)
        new_stock.grid(row=3,column=2)
        
        #button
        
        tk.Button(self.edit_wind, text='Actualizar', command= lambda: self.edit_records(name,old_price,new_price.get(),old_stock,new_stock.get()) ).grid(row=4,column=2,sticky=tk.W)
        
    def edit_records(self, name, old_price, new_price, old_stock, new_stock):
        if self.validate_price_stock(new_price,new_stock):
            query= 'UPDATE product SET price=?, stock=? WHERE name=? AND price=? AND stock=?'
            parameters=(new_price, new_stock, name, old_price, old_stock)
            self.run_query(query,parameters)
            self.edit_wind.destroy()
            self.__message['text']= 'Se actualizaron los valores de {}'.format(name)
            self.get_products()
            self.update_inventory_value()
        else:
            self.__message['text']='Precio y stock tienen que ser mayores a 0'  
            
        
        
    def inventory_value(self):
        query= 'SELECT * FROM product ORDER BY name DESC'
        db_rows=self.run_query(query)
        output=0            
        for row in db_rows:
            output+= row[2]*row[3]
        return output
    
    def update_inventory_value(self):
        self.total_cost.destroy()
        self.total_cost=tk.Label(textvariable=tk.StringVar(value=self.inventory_value()))
        self.total_cost.grid(row=7,column=1)
        
               
if __name__ == '__main__':
    window = tk.Tk()
    application=Product(window)
    window.mainloop()




