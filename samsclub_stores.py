from pystores.mixins import ScraperAPI, CSVMixin
from pystores.decorators import validate_data_to_csv


class SamsClub(ScraperAPI, CSVMixin):
    url = 'https://www.sams.com.mx/rest/model/atg/userprofiling/ProfileActor/stateStoreLocator'
    
    
    @validate_data_to_csv
    def get_data(self) -> list[dict]:
        context_data = self.run()
        response = context_data['response']
        list_stores = response['stateStores'].values()
        return [store for lista in list_stores for store in lista]


if __name__ == '__main__':
    SamsClub().save()
    