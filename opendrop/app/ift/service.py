from injector import Module, Binder, inject, singleton

from opendrop.app.service import AppService
from .core import SessionModule


class IFTModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.install(SessionModule)
        binder.bind(interface=IFTService, to=IFTService, scope=singleton)


class IFTService:
    @inject
    def __init__(self, app_service: AppService) -> None:
        self._app_service = app_service

    def back(self) -> None:
        self._app_service.show_start()

    def quit(self) -> None:
        self._app_service.quit()
