from php_fpm.fpm_interface import callPhp_Fpm
from RequestHandlers.common import getResource

def handle_get(request, config):
    if  request.getResourcePath(config["root_directory"]).split(".")[-1] == "php" :
        response = callPhp_Fpm(request, config)
    else:
        response = getResource(request, config)

    return response