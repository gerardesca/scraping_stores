from pystores.mixins import ScraperAPI, CSVMixin
from pystores.decorators import validate_data_to_csv


class Sanborns(ScraperAPI, CSVMixin):
    url = 'https://snapi.sanborns.com.mx/sellers/v1/subsidiaries'
    
    
    @validate_data_to_csv
    def get_data(self) -> list[dict]:
        context_data = self.run()
        response = context_data['response']
        list_stores = response['data']
        return list_stores
    

if __name__ == '__main__':
    Sanborns().save()