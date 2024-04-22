def getSettings():
    settings = {}
    settings["ip"] = '127.0.0.1'
    settings["port"] = 6764
    settings["thread count"] = 1
    settings["use_php_fpm"] = True #currently unused
    settings["fpm_ip"] = "127.0.0.1"
    settings["fpm_port"] = 9000
    settings["root_directory"] = "/home/mateusz/python_projects/HttpServer/tests/php3/"
    settings["php_session"] = "/usr/local/sbin/session"
    return settings