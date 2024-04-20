def getSettings():
    settings = {}
    settings["ip"] = '127.0.0.1'
    settings["port"] = 8443
    settings["thread count"] = 5
    settings["use_php_fpm"] = True
    settings["fpm_ip"] = "127.0.0.1"
    settings["fpm_port"] = 9000
    settings["root_directory"] = "/home/mateusz/python_projects/HttpServer/tests/php1"
    return settings