from requests import Response
from http import HTTPStatus


class ResponceSpecs:
    @staticmethod
    def request_ok():
        def confirm(responce: Response):
            assert responce.status_code == HTTPStatus.OK, responce.text

        return confirm

    @staticmethod
    def requests_created():
        def confirm(responce: Response):
            assert responce.status_code == HTTPStatus.CREATED, responce.text

        return confirm

    @staticmethod
    def request_bad():
        def confirm(responce: Response):
            assert responce.status_code == HTTPStatus.BAD_REQUEST, responce.text

        return confirm
