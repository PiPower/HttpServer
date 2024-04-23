from php_fpm.fpm_interface import process_php_file
from RequestHandlers.common import getResource

def handle_get(request, config):
    if  request.getResourcePath(config["root_directory"]).split(".")[-1] == "php" :
        response = process_php_file(request, config)
    else:
        response = getResource(request, config)

    return response