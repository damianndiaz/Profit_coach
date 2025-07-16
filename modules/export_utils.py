def save_excel_bytes_to_tempfile(excel_bytes):
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    tmp.write(excel_bytes)
    tmp.close()
    return tmp.name
import pandas as pd
import yagmail
import tempfile
import os

def export_routine_to_excel(messages, filename):
    # Filtro estricto: solo exporta mensajes del coach que parecen rutina
    # Si no existe [INICIO_NUEVA_RUTINA], exporta la última respuesta del coach
    def es_rutina(texto):
        # Puedes mejorar este filtro según tu formato de rutina
        palabras_clave = ["día", "ejercicio", "series", "repeticiones", "planificación", "rutina", "entrenamiento", "descanso", "calentamiento", "sesión"]
        texto_l = texto.lower()
        return any(p in texto_l for p in palabras_clave) and len(texto_l) > 30

    # Nueva lógica: exporta el último bloque consecutivo de mensajes del coach que parecen rutina
    routine_msgs = []
    # Buscar el último [INICIO_NUEVA_RUTINA]
    last_idx = -1
    for i, (msg, is_user, created) in enumerate(messages):
        if msg == '[INICIO_NUEVA_RUTINA]':
            last_idx = i
    # Si existe el marcador, buscar los mensajes del coach posteriores hasta el siguiente mensaje del usuario
    if last_idx != -1:
        i = last_idx + 1
        while i < len(messages):
            msg, is_user, created = messages[i]
            if is_user:
                break
            if not is_user and es_rutina(msg):
                routine_msgs.append({'Mensaje': msg, 'Fecha': created})
            i += 1
    else:
        # Si no existe el marcador, buscar el último bloque consecutivo de mensajes del coach que parecen rutina
        i = len(messages) - 1
        # Saltar mensajes del usuario al final
        while i >= 0 and messages[i][1]:
            i -= 1
        # Recoger el bloque de mensajes del coach hacia atrás
        temp_msgs = []
        while i >= 0:
            msg, is_user, created = messages[i]
            if is_user:
                break
            if not is_user and es_rutina(msg):
                temp_msgs.insert(0, {'Mensaje': msg, 'Fecha': created})
            else:
                break
            i -= 1
        routine_msgs = temp_msgs
    if not routine_msgs:
        df = pd.DataFrame([{'Mensaje': 'No hay rutina para exportar', 'Fecha': ''}])
    else:
        df = pd.DataFrame(routine_msgs)
    # Exportar el archivo Excel en memoria para descarga directa
    from io import BytesIO
    output = BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    return output.getvalue()

def send_excel_by_email(to_email, subject, body, excel_path):
    yag = yagmail.SMTP(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
    yag.send(
        to=to_email,
        subject=subject,
        contents=body,
        attachments=[excel_path]
    )

def get_last_routine(messages):
    # Busca el último [INICIO_NUEVA_RUTINA] y devuelve los mensajes posteriores
    last_idx = -1
    for i, (msg, is_user, created) in enumerate(messages):
        if msg == '[INICIO_NUEVA_RUTINA]':
            last_idx = i
    if last_idx != -1:
        return messages[last_idx+1:]
    return []
