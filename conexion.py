import mysql.connector

# Crear la conexión y el cursor de manera global
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="chatbot"
)
cursor = conexion.cursor()

# Exportar datos de reservación a la base de datos
def exportar_datos(datos):
    try:
        # Prepara la consulta SQL
        sql = "INSERT INTO reservas (nombre, telefono, personas, fecha, hora) VALUES (%s, %s, %s, %s, %s)"
        # Extrae los datos del diccionario y sepáralos
        val = (datos["nombre"], datos["telefono"], datos["personas"], datos["fecha"], datos["hora"])

        # Ejecuta la consulta
        cursor.execute(sql, val)
        conexion.commit()
        print(cursor.rowcount, "reserva insertada.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Exportar pedido a la base de datos
def exportar_pedido(datos_pedido):
    try:
        # Prepara la consulta SQL
        sql = """
        INSERT INTO pedidos (nombre, telefono, direccion, metodo_pago, pedido) 
        VALUES (%s, %s, %s, %s, %s)
        """
        # Extrae los datos del diccionario y sepáralos
        val = (
            datos_pedido["nombre"],
            datos_pedido["telefono"],
            datos_pedido["direccion"],
            datos_pedido["metodo_pago"],
            datos_pedido["pedido"]
        )

        # Ejecuta la consulta
        cursor.execute(sql, val)
        conexion.commit()

        # Verifica si se insertó al menos una fila
        if cursor.rowcount > 0:
            return True  # Operación exitosa
        else:
            return False  # No se insertó ninguna fila

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False  # Error en la operación

# Cerrar la conexión y el cursor al final del programa
def cerrar_conexion():
    try:
        cursor.close()
        conexion.close()
    except mysql.connector.Error as err:
        print(f"Error al cerrar la conexión: {err}")

def obtener_reserva_por_nombre(nombre_cliente):
    try:
        # Consulta SQL para obtener la reserva por nombre
        sql = "SELECT nombre, telefono, personas, fecha, hora FROM reservas WHERE nombre = %s"
        cursor.execute(sql, (nombre_cliente,))
        resultado = cursor.fetchone()

        if resultado:
            return {
                "nombre": resultado[0],
                "telefono": resultado[1],
                "personas": resultado[2],
                "fecha": resultado[3],
                "hora": resultado[4]
            }
        else:
            return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def eliminar_reserva_por_nombre(nombre_cliente):
    try:
        # Consulta SQL para eliminar la reserva por nombre
        sql = "DELETE FROM reservas WHERE nombre = %s"
        cursor.execute(sql, (nombre_cliente,))
        conexion.commit()  # Confirma los cambios en la base de datos

        if cursor.rowcount > 0:
            return True  # La reserva se eliminó con éxito
        else:
            return False  # No se encontró la reserva

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False

def actualizar_reserva_por_nombre(nombre_cliente, nuevos_datos):
    try:
        # Construir dinámicamente la consulta SQL en función de los datos proporcionados
        campos = []
        valores = []

        if "telefono" in nuevos_datos:
            campos.append("telefono = %s")
            valores.append(nuevos_datos["telefono"])
        if "personas" in nuevos_datos:
            campos.append("personas = %s")
            valores.append(nuevos_datos["personas"])
        if "fecha" in nuevos_datos:
            campos.append("fecha = %s")
            valores.append(nuevos_datos["fecha"])
        if "hora" in nuevos_datos:
            campos.append("hora = %s")
            valores.append(nuevos_datos["hora"])

        # Verificar si hay campos para actualizar
        if not campos:
            return False  # No hay datos para actualizar

        # Construir la consulta SQL
        sql = f"UPDATE reservas SET {', '.join(campos)} WHERE nombre = %s"
        valores.append(nombre_cliente)  # Agregar el nombre al final de los valores

        # Ejecutar la consulta
        cursor.execute(sql, tuple(valores))
        conexion.commit()  # Confirmar los cambios en la base de datos

        if cursor.rowcount > 0:
            return True  # La reserva se actualizó con éxito
        else:
            return False  # No se encontró la reserva para actualizar

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False