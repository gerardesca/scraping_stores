from abc import ABC, abstractmethod
from pathlib import Path
import requests
import json
import csv
import os

from pystores.exceptions import ImproperlyConfigured
from pystores import settings


class ContextMixin:
   
    extra_context = None

    def get_context_data(self, **kwargs) -> dict:
        kwargs.setdefault("object_name", self.__class__.__name__)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs


class RequestMixin:
    url = None
    headers = None
    extra_headers = None
    
    
    def __init__(self, **kwargs) -> None:
        
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        self.get_headers()
        self.get_url()
    
    
    def get_headers(self) -> dict:
        
        if self.headers is None:
            self.headers = getattr(settings, 'HEADERS')
            
        if isinstance(self.extra_headers, dict):
            self.headers.update(self.extra_headers)
            
        return self.headers
        
    
    def get_url(self) -> str:
        if self.url is None:
            raise ImproperlyConfigured(
                "Base requires either a definition of "
                "'url' or an implementation of 'get_url()'"
            )
        return self.url
    
    
    def make_request(self, **kwargs) -> str:
        """Sends a HTTP GET request to the specified URL."""
        try:
            response = requests.get(self.url, headers=self.headers, **kwargs)
            response.raise_for_status()
            if response.status_code == 200:
                return response.text
        except requests.exceptions.HTTPError as http_error:
            print(f"HTTP error occurred: {http_error}")
        except requests.exceptions.RequestException as error:
            print(f"An error occurred: {error}")
    
            
    def __str__(self) -> str:
        return f'{self.__class__.__name__} -> {self.url}'
        

class ScraperMixin(RequestMixin, ContextMixin):
    
    def get_context_data(self, **kwargs) -> dict:
        context = {}
        context['response'] = self.get_response()
        context.update(kwargs)
        return super().get_context_data(**context)
    
    def get_response(self, **kwargs) -> str:
        return self.make_request(**kwargs)
    
    def run(self):
        return self.get_context_data()
    

class ScraperAPI(ScraperMixin):
    
    def get_response(self, **kwargs):
        response = super().get_response(**kwargs)
        json_object = self.str_to_json(response)
        return json_object
    
    
    def str_to_json(self, string: str) -> json:
        return json.loads(string)
    

class CSVMixin(ABC):
    path_dir =  None
    name_file = None
    
    
    @abstractmethod
    def get_data(self) -> list[dict]:
        """
        You need to implement this method,
        this method needs to return a list of dicts
        
        You can use decorator pystores.decorators.validate_data_to_csv, 
        to validate your method return a valid format
        
        Example: 
        return [{'column1':'value1'}, {'column1':'value2'}]
        """
        pass
    
    
    def save(self):
        data = self.get_data()
        try:
            with open(self.get_path(), 'w', newline='', encoding='utf-8') as csv_file:
                fieldnames = data[0].keys() if data else []
                csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                
                csv_writer.writeheader() #header
                csv_writer.writerows(data) #rows
        except Exception as e:
            print(f"An error occurred to save csv: {e}")
    
            
    def get_dir(self) -> str:
        
        if self.path_dir is not None and Path(self.path_dir).resolve().is_dir():
            return self.path_dir
        else:
            base_dir = getattr(settings, 'BASE_DIR')
            self.path_dir = os.path.join(base_dir, 'data')
            os.makedirs(self.path_dir, exist_ok=True)
            return self.path_dir
     
            
    def get_name_file(self) -> str:
        if self.name_file is None:
            self.name_file = f'{self.__class__.__name__.lower()}.csv'
        
        split_name = self.name_file.split('.')
        try:
            if split_name[1] == 'csv':
                return self.name_file
            else:
                self.name_file = split_name[0] + '.csv'
                return self.name_file
        except IndexError:
            self.name_file += '.csv'
            return self.name_file
    
    
    def get_path(self) -> str:
        return os.path.join(self.get_dir(), self.get_name_file())
    