from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


class Drive:
    def __init__(self,
                 creds_file='credentials.txt',
                 settings_file='settings.yaml'):
        self.creds_file = creds_file
        self.settings_file = settings_file

    def gauth_init(self):
        gauth = GoogleAuth(settings_file=self.settings_file)
        if gauth.credentials is None:
            gauth.GetFlow()
            gauth.flow.params.update({'access_type': 'offline'})
            # gauth.flow.params.update({'approval_prompt': 'force'})
            gauth.LoadCredentialsFile(self.creds_file)
            gauth.LocalWebserverAuth(
            )  # Authenticate if `credentials.txt` doesn't exist
        elif gauth.access_token_expired:
            gauth.Refresh()  # Refresh creds if expired
        else:
            gauth.Authorize()  # Initialize the saved creds
        gauth.SaveCredentialsFile(self.creds_file)
        return gauth

    def drive(self):
        return GoogleDrive(self.gauth_init())
