from json import dumps
from timeit import default_timer as timer
from xbmcgui import Dialog
from jurialmunkey.ftools import cached_property
from tmdbhelper.lib.addon.dialog import BusyDialog
from tmdbhelper.lib.files.futils import FileUtils, validify_filename
from tmdbhelper_sync_trakt.localization import get_localized


class TraktDiagnosticFiles(FileUtils):
    addondata = 'special://profile/addon_data/script.module.tmdbhelper.sync.trakt/'


class TraktDiagnostic:
    name = ''
    folder = 'log_data'

    def __init__(self, provider, **parameters):
        self.provider = provider
        self.parameters = parameters

    @cached_property
    def files(self):
        return self.get_files()

    def get_files(self):
        return TraktDiagnosticFiles()

    @cached_property
    def data(self):
        return self.get_data()

    def get_data(self):
        raise NotImplementedError

    @cached_property
    def filename(self):
        return self.get_filename()

    def get_filename(self):
        return validify_filename(f'test_func_{self.name}.json')

    @property
    def heading(self):
        return 'Trakt'

    def show_result(self, data, dialog_output):
        text = dumps(data, indent=2) if dialog_output else str(bool(data))
        Dialog().textviewer(self.heading, text)

    def get_report_parameters(self):
        return self.parameters

    def run(self, dialog_output=False):
        started = timer()
        with BusyDialog():
            data = self.data
        if data is None:
            Dialog().ok(self.heading, get_localized(32205))
            return
        report = {
            'func': self.name,
            'kwgs': self.get_report_parameters(),
            'time': f'{timer() - started:.3f} sec',
            'data': data,
        }
        self.files.dumps_to_file(report, self.folder, self.filename)
        self.show_result(data, dialog_output)
        return data


class TraktResponseDiagnostic(TraktDiagnostic):
    name = 'trakt_response'

    def __init__(self, provider, path=None, **parameters):
        super().__init__(provider, **parameters)
        self.request_path = path

    @cached_property
    def path(self):
        return self.get_path()

    def get_path(self):
        return self.request_path or Dialog().input(get_localized(32206))

    @property
    def heading(self):
        return self.path

    def get_data(self):
        response = self.provider.api.get_response(self.path, **self.parameters)
        if response is None or not response.ok:
            return
        try:
            data = response.json()
        except ValueError:
            return
        return {'headers': dict(response.headers), 'request': data}

    def run(self, dialog_output=False):
        if not self.path:
            return
        return super().run(dialog_output=dialog_output)

    def get_report_parameters(self):
        return {'path': self.path, **self.parameters}


class TraktSyncResponseDiagnostic(TraktResponseDiagnostic):
    name = 'get_response_sync'

    def get_data(self):
        data = super().get_data()
        return data['request'] if data is not None else None


class TraktRequestLog(TraktSyncResponseDiagnostic):
    name = 'log_request'
    folder = 'log_request'

    def get_filename(self):
        return validify_filename(f'trakt_{self.path}.json')

    def show_result(self, data, dialog_output):
        path = self.files.get_file_path(self.folder, self.filename, make_dir=False)
        Dialog().ok('Trakt', path)
        super().show_result(data, dialog_output=True)


class TraktAuthorizationDiagnostic(TraktDiagnostic):
    name = 'trakt_auth'

    def get_data(self):
        authenticator = self.provider.api.authenticator
        token = authenticator.trakt_stored_access_token
        return {
            'is_authorized': authenticator.is_authorized,
            'has_refresh_token': bool(token.refresh_token),
            'expires_in_timestamp': token.expires_in_timestamp,
        }


def run_diagnostic(provider, action, test_func=None, dialog_output=False, **parameters):
    name = test_func if action == 'test_func' else action
    diagnostic_class = {
        'log_request': TraktRequestLog,
        'auth_status': TraktAuthorizationDiagnostic,
        'trakt_response': TraktResponseDiagnostic,
        'trakt_auth': TraktAuthorizationDiagnostic,
        'get_response_sync': TraktSyncResponseDiagnostic,
    }[name]
    diagnostic = diagnostic_class(provider, **parameters)
    return diagnostic.run(
        dialog_output=dialog_output or action in ('log_request', 'auth_status'))
