def getSettings():
    settings = {}
    settings["ip"] = '127.0.0.1'
    settings["port"] = 6764
    settings["thread_count"] = 4
    settings["use_php_fpm"] = True #currently unused
    settings["fpm_ip"] = "127.0.0.1"
    settings["fpm_port"] = 9000
    settings["root_directory"] = "/home/mateusz/python_projects/HttpServer/tests/php4/"
    settings["php_session"] = "/usr/local/sbin/session"
    return settings