from tubectrl import YouTube

client_secret_file: str = '/home/lyle/Downloads/secret.json'
youtube = YouTube()
youtube.authenticate(client_secret_file)