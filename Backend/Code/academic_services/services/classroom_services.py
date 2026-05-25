import os
import re
from django.conf import settings
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_classroom_service(creds):
    if not creds:
        return None
    return build('classroom', 'v1', credentials=creds)


def extrair_id_do_drive(url):
    padrao = r"(?:/d/|/folders/|id=)([\w-]+)"
    match = re.search(padrao, url)
    
    if match:
        return match.group(1)
    
    return None


def postar_material_aula(creds, course_id, titulo, descricao, links_materiais=None):
    service = get_classroom_service(creds)
    if not service:
        return {"erro": "Credenciais inválidas ou ausentes."}
    
    material_body = {
        'title': titulo,
        'description': descricao,
        'state': 'PUBLISHED',
        'materials': []
    } 
    
    if links_materiais:
        for url_drive in links_materiais:
            
            if not isinstance(url_drive, str):
                continue
            
            file_id = extrair_id_do_drive(url_drive)
            
            if file_id:
                material_body['materials'].append({
                    'driveFile':{
                        'driveFile':{
                            'id': file_id,
                        }
                        #},
                        #'shareMode': 'VIEW'
                    }
                })
            else:
                material_body['materials'].append({
                    'link': {'url': url_drive}
                })                 
    
    try: 
        resultado = service.courses().courseWorkMaterials().create(
            courseId=course_id,
            body=material_body
        ).execute()
        return {"Sucesso": True, "post_id": resultado.get('id')}
    
    except Exception as e:
        return {"Sucesso": False, "erro": str(e)}
    
    
    