class FileMetadata:
    def __init__(self, name, type, path, hash_value):
        self.name = name
        self.type = type
        self.path = path
        self.hash = hash_value
    
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "hash": self.hash
        }
    
class ModelTime:
    def __init__(self, start_time, end_time, output_interval):
        self.start_time      = start_time
        self.end_time        = end_time
        self.output_interval = output_interval
    
    def to_dict(self):
        return {
            "start_time"      : self.start_time,
            "end_time"        : self.end_time,
            "output_interval" : self.output_interval
        }    
    
class ModelForcing:
    def __init__(self, file_pattern, path, provider, hash_value):
        self.file_pattern  = file_pattern
        self.path          = path
        self.provider      = provider
        self.hash          = hash_value
    
    def to_dict(self):
        return {
            "file_pattern" : self.file_pattern,
            "path"         : self.path,
            "provider"     : self.provider,
            "hash"         : self.hash
        } 

class RunConfigMetadata:
    def __init__(
                self, 
                description,
                model_realization, 
                model_configuration, 
                model_time, 
                forcing_inputs, 
                hydrofabric_catchment, 
                hydrofabric_nexus, 
                hydrofabric_crosswalk,
                model_modules,
                model_catchment_formulations
                ):
        
        self.RUN_CONFIG = {
            "description": description,
            "model": {
                "realization": model_realization.to_dict(),
                "configuration": model_configuration.to_dict(),
                "modules": [j_module.to_dict() for j_module in model_modules],
            },
            "time": model_time.to_dict(),
            "forcings": {
                "inputs": forcing_inputs.to_dict(),
                "hydrofabric": {
                    "catchment": hydrofabric_catchment.to_dict(),
                    "nexus": hydrofabric_nexus.to_dict(),
                    "crosswalk": hydrofabric_crosswalk.to_dict()
                }
            },
            "catchments_formulations": [j_form.to_dict() for j_form in model_catchment_formulations]
        }
