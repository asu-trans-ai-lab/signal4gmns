import yaml

class YamlHandler:

    def __init__(self,file,encoding = 'utf-8'):
         self.file = file
         self.encoding = encoding

    def get_ymal_data(self):
        with open(self.file,encoding=self.encoding) as f:
            data = yaml.load(f.read(),Loader=yaml.FullLoader)
        return data

    def write_yaml(self,data):
        with open(self.file,'w',encoding=self.encoding) as f:
            yaml.dump(data,stream=f,allow_unicode = True)

