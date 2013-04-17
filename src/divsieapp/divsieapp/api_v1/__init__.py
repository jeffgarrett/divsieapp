import cornice
import tasks

def includeme(config):
    for svc in tasks.Task._services.values():
        cornice.register_service_views(config, svc)
