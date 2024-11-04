import requests

class BsaleDAL:
    def __init__(self):
        self.urlAPI = 'https://api.bsale.cl'
        self.token = '1b7908fa44b56ba04a3459db5bb6e9b12bb9fadc'  # Token de EMT
        self.documents = '/v1/documents'
    
    def get_headers(self):
        """
        Genera los headers necesarios para las solicitudes a la API de Bsale.
        """
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_data_api(self, url):
        """
        Realiza una solicitud GET a la API de Bsale.
        """
        headers = self.get_headers()
        response = requests.get(url, headers=headers)

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error en la solicitud a Bsale: {response.status_code}", "detail": response.text}

    def get_unique_document_dal(self, type, number):
        """
        Realiza la lógica para obtener un documento único de Bsale basado en el tipo y número.
        """
        # Primera solicitud para obtener el documento con base en el tipo y número
        url_req = f"{self.urlAPI}/v1/documents/costs.json?codesii={type}&number={number}"
        info = self.get_data_api(url_req)

        # Si no hay error, seguimos con la siguiente solicitud
        if "id" in info:
            document_id = info['id']
            url_details = f"{self.urlAPI}/v1/documents/{document_id}/details.json"
            return self.get_data_api(url_details)
        else:
            return {"error": "Documento no encontrado", "info": info}
