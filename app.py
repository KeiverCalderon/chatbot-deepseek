from openai import OpenAI
import streamlit as st
import re
from conexion import exportar_datos, obtener_reserva_por_nombre,eliminar_reserva_por_nombre, actualizar_reserva_por_nombre, exportar_pedido
from asistente import asistente
import unicodedata

# Función para verificar si los datos de la reservación están completos
def datos_completos(dat):
  claves_requeridas = ["nombre", "telefono", "personas", "fecha", "hora"]
  for clave in claves_requeridas:
    if clave not in dat:
      return st.write("Rellena todos los campos requeridos para la reservacion")
  return exportar_datos(dat)

#funcion para quitar tildes 
def quitar_tildes(cadena):
    normalizado = unicodedata.normalize('NFD', cadena)
    sin_tildes = ''.join(c for c in normalizado if unicodedata.category(c) != 'Mn')
    return sin_tildes

#funcion para el chatbot
def get_response(prompt):
    try:
        # Configuración del cliente OpenAI
        client = OpenAI(
            api_key='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',
            base_url='https://openrouter.ai/api/v1'
        ) 
        # Formato de los mensajes
        messages = [
            {"role": "assistant", "content": asistente()},
            {"role": "user", "content": prompt}
        ]

        # Llamada a la API
        chat = client.chat.completions.create(
        model="deepseek/deepseek-r1:free",  # Cambia el modelo si es necesario
        messages=messages
          )

        # Devolver la respuesta del modelo
        return chat.choices[0].message.content

    except Exception as e:
        # Manejo de errores
        return f"Error al conectar con la API: {e}"


# Función para recolectar datos del cliente
def recolectar_datos_reservacion(prompt):
    # Patrón para extraer datos de la reservación
    prompt = prompt.lower()
    patrones = {
        "nombre": r"(?i)nombre[:\s]*([a-zA-Z\s]+)",
        "telefono": r"(?i)tel[eé]fono[:\s]*([\d\s\-]+)",
        "personas": r"(?i)n[uú]mero de personas[:\s]*(\d+)",
        "fecha": r"(?i)fecha[:\s]*([\d\-\/]+)",
        "hora": r"(?i)hora[:\s]*([\d:apm\s]+)"
    }

    datos = {}
    for campo, patron in patrones.items():
        match = re.search(patron, prompt)
        if match:
            datos[campo] = match.group(1).strip()

    # Guardar los datos en el estado de la sesión
    if "datos_cliente" not in st.session_state:
        st.session_state.datos_cliente = {}
    st.session_state.datos_cliente.update(datos)

    return datos

def recolectar_reservacion_hecha(prompt):
    prompt = prompt.lower()
    nombre =  r"(?i)nombre de[:\s]*([a-zA-Z\s]+)"
    coincidencia = re.search(nombre, prompt)

    if coincidencia:
        return coincidencia.group(1).strip()  # Devuelve el nombre (grupo 1) sin espacios extra
    else:
        return None  # Devuelve None si no se encuentra el patrón
    
def recolectar_eliminar_reservacion(prompt):
    prompt = prompt.lower()
    print(prompt)
    nombre =  r"(?i)eliminar reservacion a nombre de[:\s]*([a-zA-Z\s]+)"
    coincidencia = re.search(nombre, prompt)
    
    if coincidencia:
        return coincidencia.group(1).strip()
    else:
        return None

def recolectar_datos_actualizar(prompt):
    prompt = prompt.lower()
    # Patrón para extraer los datos que se desean actualizar
    patrones = {
        "telefono": r"(?i)tel[eé]fono[:\s]*([\d\s\-]+)",
        "personas": r"(?i)personas[:\s]*(\d+)",
        "fecha": r"(?i)fecha[:\s]*([\d\-\/]+)",
        "hora": r"(?i)hora[:\s]*([\d:apm\s]+)"
    }

    datos_actualizar = {}
    for campo, patron in patrones.items():
        match = re.search(patron, prompt)
        if match:
            datos_actualizar[campo] = match.group(1).strip()

    return datos_actualizar

def recolectar_datos_pedido(prompt):
    # Convertir el prompt a minúsculas para facilitar la búsqueda
    prompt = prompt.lower()

    # Patrón para extraer los datos del pedido
    patrones = {
        "nombre": r"(?i)nombre[:\s]*([a-zA-Z\s]+)",
        "telefono": r"(?i)tel[eé]fono[:\s]*([\d\s\-]+)",
        "metodo_pago": r"(?i)m[eé]todo de pago[:\s]*(efectivo|tarjeta|transferencia)",
        "direccion": r"(?i)direcci[oó]n[:\s]*([a-zA-Z0-9\s,]+)"
        
    }

    datos_pedido = {}
    for campo, patron in patrones.items():
        match = re.search(patron, prompt)
        if match:
            datos_pedido[campo] = match.group(1).strip()

    # Mostrar el menú al cliente
    menu = {
        1: "Ceviche Andino",
        2: "Risotto de Hongos Salvajes y Trufa",
        3: "Pulpo a la Parrilla con Papas Bravas Orientales",
        4: "Costillas de Cerdo Glaseadas con Tamarindo y Piña",
        5: "Curry de Lentejas Rojas y Coco con Pan Naan Casero",
        6: "Hamburguesa Gourmet de Cordero con Queso de Cabra y Mermelada de Higos",
        7: "Salmón Sellado con Salsa de Maracuyá y Espárragos a la Parrilla",
        8: "Ensalada de Burrata con Tomates Heirloom y Pesto de Albahaca",
        9: "Tarta de Chocolate Negro con Helado de Vainilla y Frambuesas Frescas",
        10: "Crème brûlée de Lavanda con Galletas de Almendra"
    }

    st.write("Por favor, selecciona tu pedido del siguiente menú:")
    for key, value in menu.items():
        st.write(f"{key}. {value}")

    # Extraer el pedido del prompt
    pedido_patron = r"(?i)pedido[:\s]*(\d+)"
    pedido_match = re.search(pedido_patron, prompt)
    if pedido_match:
        pedido_numero = int(pedido_match.group(1).strip())
        if pedido_numero in menu:
            datos_pedido["pedido"] = menu[pedido_numero]
        else:
            st.write("El número del pedido no es válido. Por favor, selecciona un número del menú.")
    else:
        st.write("Por favor, proporciona el número de tu pedido.")

    # Guardar los datos en el estado de la sesión
    if "datos_pedido" not in st.session_state:
        st.session_state.datos_pedido = {}
    st.session_state.datos_pedido.update(datos_pedido)

    return datos_pedido

#funcion main de streamlit
def main():
    st.title("Chatbot OneMichelin⭐🥘🍽️")
    st.write("¡Bienvenido al chat! Escribe tu duda o peticion, nos complace ayudarte 🌝")

    # Inicializar el historial de mensajes y datos del cliente en la sesión
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "datos_cliente" not in st.session_state:
        st.session_state.datos_cliente = {}

    # Mostrar el historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Recoger el mensaje del usuario
    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        # Agregar el mensaje del usuario al historial
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        
        
        with st.chat_message("assistant"):
            entrada_sin_tildes = quitar_tildes(prompt)
            # Manejar las solicitudes según las palabras clave en el mensaje
            if ("hacer reservacion") in entrada_sin_tildes.lower():
                # Recolectar datos para hacer una reservación
                datos_reservacion = recolectar_datos_reservacion(entrada_sin_tildes.strip())
                if datos_reservacion:
                    st.write("Datos de reservación recolectados:")
                    st.json(datos_reservacion)
                    datos_completos(datos_reservacion)
                    st.write("Reservación realizada con éxito.")
                else:
                    st.write("Por favor, proporciona todos los datos necesarios para la reservación.")

            elif "consultar reservación" in entrada_sin_tildes.lower():
                # Consultar una reservación por nombre
                reservacion_hecha = recolectar_reservacion_hecha(entrada_sin_tildes.strip())
                if reservacion_hecha:
                    st.write(f"Buscando reserva a nombre de: {reservacion_hecha}")
                    reserva = obtener_reserva_por_nombre(reservacion_hecha)
                    if reserva:
                        st.write("Reserva encontrada:")
                        st.json(reserva)
                    else:
                        st.write(f"No se encontró ninguna reserva a nombre de: {reservacion_hecha}")
                else:
                    st.write("Por favor, proporciona el nombre de la reserva que deseas consultar.")

            elif ("eliminar reservacion") in entrada_sin_tildes.lower():
                # Eliminar una reservación por nombre
                eliminar_reservacion = recolectar_eliminar_reservacion(entrada_sin_tildes.strip())
                if eliminar_reservacion:
                    st.write(f"Intentando eliminar reserva a nombre de: {eliminar_reservacion}")
                    if eliminar_reserva_por_nombre(eliminar_reservacion) is True:
                        st.write(f"Reserva eliminada exitosamente a nombre de: {eliminar_reservacion}")
                    else:
                        st.write(f"No se encontró ninguna reserva a nombre de: {eliminar_reservacion}")
                else:
                    st.write("Por favor, proporciona el nombre de la reserva que deseas eliminar.")

            elif "actualizar reserva" in entrada_sin_tildes.lower():
                # Actualizar una reservación por nombre
                nombre_cliente = recolectar_reservacion_hecha(entrada_sin_tildes.strip())
                if nombre_cliente:
                    # Recolectar los datos a actualizar
                    nuevos_datos = recolectar_datos_actualizar(entrada_sin_tildes.strip())
                    if nuevos_datos:
                         # Intentar actualizar la reserva
                        if actualizar_reserva_por_nombre(nombre_cliente, nuevos_datos):
                            st.write(f"Reserva actualizada exitosamente para {nombre_cliente}.")
                        else:
                            st.write(f"No se encontró ninguna reserva a nombre de {nombre_cliente}.")
                    else:
                        st.write("Por favor, proporciona los datos que deseas actualizar.")
                else:
                    st.write("Por favor, proporciona el nombre de la reserva que deseas actualizar.")

            elif "hacer pedido" in entrada_sin_tildes.lower():
                # Recolectar datos para hacer un pedido
                datos_pedido = recolectar_datos_pedido(entrada_sin_tildes.strip())
                if datos_pedido:
                    st.write("Datos del pedido recolectados:")
                    st.json(datos_pedido)
                    if exportar_pedido(datos_pedido) is True:
                        st.write("Pedido realizado con éxito. Le estara llegando en los proximos minutos, si hay alguna eventualidad o desea cancelarlo  por favor ir a atencion al cliente"),
                    else:
                        st.write("No se pudo realizar el pedido. Por favor, intenta de nuevo. si hay una eventualidad por favor pida informacion en atencion al cliente")
                else:
                    st.write("Por favor, proporciona todos los datos necesarios para realizar el pedido.")

            else:
                # Si no coincide con ninguna palabra clave, delegar al chatbot
                response = get_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()