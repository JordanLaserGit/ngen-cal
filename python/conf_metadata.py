import json, os, re, hashlib, time
from pathlib import Path
from ngen.config.realization import NgenRealization
from ngen.config.metadata import FileMetadata, RunConfigMetadata, ModelForcing, ModelTime
from ngen.config.utils import run_args

def determine_path_type(path):
    path_str = str(path)
    if path_str == '.':
        return None
    else:
        if re.match(r'^[a-zA-Z]:\\|/', path_str):
            return "local"
        elif re.match(r'^\w+://', path_str):
            return "cloud"
        else:
            raise Exception(f'\n\nUnable to determine path type!\n {path_str}')
    
def extract_metadata_file(file, name):

    # This may be changed in the future
    hash_function = hash_256_gen_local
        
    path_type = determine_path_type(Path(file))

    if path_type is not None:
        with open(file) as fp:
            file_hash = hash_function(fp)
            if name == 'IN_FILE':
                try: name = json.load(open(file))['name']      
                except: raise Exception(f'field \'name\' not found in {file}')      
    else:
        file_hash = 'No file provided'
        if name == 'IN_FILE': name = None

    return FileMetadata(
        name,
        path_type, 
        str(file), 
        file_hash
        )

def metadata_dictionary(catchment_file, nexus_file, realization_file, crosswalk_file):

    serialized_realization = NgenRealization.parse_file(realization_file)
    realization_parent = Path(realization_file).parent

    # Global level formulation/configuration
    global_formulation = serialized_realization.global_config.formulations[0]
    global_forcing = serialized_realization.global_config.forcing
    global_params = global_formulation.params
    config_file  = global_params.config

    model_realization   = extract_metadata_file(realization_file,global_formulation.name)
    model_configuration = extract_metadata_file(config_file,global_params.model_name)

    # TODO, get the hydrofabric file names from somewhere.
    model_catchments = extract_metadata_file(catchment_file,"IN_FILE")
    model_nexus      = extract_metadata_file(nexus_file,"IN_FILE")
    model_crosswalk  = extract_metadata_file(crosswalk_file,"IN_FILE")

    # Forcing    
    # forcing_hash = 999 # TODO : this needs to come from the forcing metadata file
    forcing_metadata = Path(str(global_forcing.path),'metadata/ids')
    with open(forcing_metadata) as fp:
        forcing_hash = json.load(fp)['root_hash']      

    model_forcing = ModelForcing(
        global_forcing.file_pattern,
        str(global_forcing.path),
        global_forcing.provider,
        forcing_hash
        )

    # Time
    realization_time = serialized_realization.time
    fmt = "%Y-%m-%d, %H:%M:%S"
    model_time = ModelTime(
        realization_time.start_time.strftime(fmt),
        realization_time.end_time.strftime(fmt),
        realization_time.output_interval
        )

    # Modules belonging to the global formulation/config 
    model_modules = []
    config_full_path = ''
    if len(global_params.modules) > 0:
        model_modules = []
        for j_module in global_params.modules: 
            if str(j_module.params.config) != '.': config_full_path = Path(realization_parent,j_module.params.config)
            model_modules.append(extract_metadata_file(config_full_path,j_module.name))

    # Catchment level formulation/configuration
    model_catchment_formulations = []
    config_full_path = ''
    if len(serialized_realization.catchments) > 0:        
        for j_cat in serialized_realization.catchments:
            catchment_formulation = serialized_realization.catchments[j_cat].formulations[0]
            if str(catchment_formulation.params.config) != '.': config_full_path = Path(realization_parent,catchment_formulation.params.config)
            model_catchment_formulations.append(extract_metadata_file(config_full_path,catchment_formulation.name))            

    # Creating the RunConfigMetadata instance
    run_config_metadata = RunConfigMetadata(
        "METADATA TEST FILE",
        model_realization,
        model_configuration,
        model_time,
        model_forcing, 
        model_catchments, 
        model_nexus,
        model_crosswalk,
        model_modules,
        model_catchment_formulations
        )

    return run_config_metadata

def hash_256_gen_local(file_handle):    
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_handle.read().encode())
    return sha256_hash.hexdigest()

if __name__ == "__main__":

    # Files that may be coming from buckets -> forcings, catchment/nexus/realizations config
    # Optional environment variables that can be set by ngeninabox 
    catchment_uri = os.environ.get('CATCH_CONF')    
    
    ngen_args = run_args()  

    catchment_file   = ngen_args[0]
    nexus_file       = ngen_args[2]
    realization_file = ngen_args[4] 
    crosswalk_file   = ""
    if len(ngen_args) > 5:
        crosswalk_file = ngen_args[5] 
    

    run_config_metadata = metadata_dictionary(catchment_file, nexus_file, realization_file, crosswalk_file)

    # Write metadata to file 
    meta_name = 'metadata.json'
    metadata_dir = os.pardir(catchment_file)
    metadata_file = os.path.join('metadata_dir',meta_name)
    with open(metadata_file,'w') as mf:
        mf.write(json.dumps(run_config_metadata.RUN_CONFIG, indent=4))