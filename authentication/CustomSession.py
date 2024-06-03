import firebase_admin
from firebase_admin import credentials, db
from telethon.sessions import MemorySession
from telethon.crypto import AuthKey
from telethon.tl import types
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from telethon import utils
from telethon.sessions.memory import _SentFileType
import base64
import datetime
import time

# Initialize Firebase Admin SDK
cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "cloud-storage-35d72",
  "private_key_id": "8bfa0e1ff0b8ca221307fcb7dffa2c3b45d17041",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCJoPcshFo+s0wd\nhTOutG8pczC0zWfdRt8wtyOM+IUYCZVURiRAi+khXPPOOWctDxhoAzCyXGCIxqVI\ndw9JShCFb9mlZaGY2IUkQQpyO4HmQeU/kyWX7R1HSnGMorKzH4o1CMEY4692fHub\negiCqirhpfdccAbzRo0l7m1ypETUIemDikSrIn42fFTz8Vxj8bCjkz3X3+VzuczX\nbc2OTJlCBsXPKQGN5RTgidg3o2/CXJStFNYK+PT3OK4WeptpP6QvsoArJIhPlQBy\nL0IoR8mtSuB6NM4WM8DbqS3DjNH4UKlfx0amQf71zeGQrzXK7s3RuyUpMZKzKMn8\nmOy7ojA3AgMBAAECggEACXGENEeal53JixGrjlZuyuB5XEE8hLg1sqExAnMU/Xq+\n29Wk7Cbi0WQQOJDDbcSQ5KYqDmWnRrX2plvBA+2IkldZOZpDyySO3Nd3pjHuGQS2\n0bTA32/+J85Jr0rZ9HolYLvf4AYoxnpb0uW94BVZXuVP7UWkkccVV/Uds8A7bCC+\ndRKS2kKE9uss9y3oCLbkbw0RPnTAtVpG30iDrtoqrzulfnb31T6VU5sw5yXqv7Ef\nt6cniH75PK3mCTBP6jzTFMNYqSrsZk72GO9BXqVAsgoHT8+K7VIaYwqaxNeY/3PE\nvdDoEqrvLQ6Qnv6yD4gDNHohz2OjkmqCTZXn/XEnoQKBgQDCO99TID9pMTofYRwk\nARleK2OyMFUhFU6gvtDeezG4KsZjpsXefrxejr4WEOhcZhBxbfUSjg9PdassXxSi\n643d2BL1HkONADR42ULIni3SbEiXGm7K6KZl25WeWgy0P3PKiNlsweInxLJy87U2\nYeutAKuvaqEvYCUj0KANNfCdVwKBgQC1ZQDc8ZgaeGOzF1eh4MkYPm5ls1OX8uF1\nMvCLowep5PlQTeCLQWwtreMR/mqVfnFr/GuNzguoZCkDzbawpNHHd2TJjrgwMX9O\nHVIEyKjM1bHRCRQ4IS/4ftkiKLQ0qWHFAgtbLGrkyfKamM1+vOSShfiMdTRYd3j+\n4+Dy/bhYIQKBgD1tHeV2D1e/H7iIx5ODXXhwlGjn7CQ4TtN7RSb3IvQxYuhk97Kz\ntfLZhbgIxNNj29NjiNvDXYgtmGLB9w7HG+iKywQF/Cr9Y5rMathzXd5sLFDNJTi6\ndtVDqn+Xzui6IG5u9QP2FQWqqRy9ghOeyB/AVIt3V15aM6St98/1vRClAoGBALQV\nJSk0NIQ69wfqaZaNGjeWa3VN9fSJLSl0O/j1DnutlZIS7pRxi9tBoYfQo7HsiN/j\nBkgOweYYIdvj07ZEuvsi3g14QgWebjt3wmB7cZGBqXnUYJ1k3UH/dMOD03vgmO7E\nG9AVJb4je1Xd0006bFXG6T1QcnpNifLK+x1hpCzhAoGAf7/gMmDPE94XlrFrHqqJ\nfR6fSUCd5dfAfj61qMAF54sJfbmN9mrTO/V2u/mil5cBSo7h0Prsz7TtF8wbVi+j\ny+cs0Vl6zB7+2plLaC4dzO16qBs7B/UpoUI53RGq7C/3OA5f2dgXmRSY92Xun6C1\n08WP3ELvX+idrFlVzdUafF4=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-sbqrd@cloud-storage-35d72.iam.gserviceaccount.com",
  "client_id": "104493142581713188137",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-sbqrd%40cloud-storage-35d72.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred, {
    "apiKey": "AIzaSyA2MgAspP9i1Y3SaDqZGy76pIGBSlG-0tU",
    "authDomain": "cloud-storage-35d72.firebaseapp.com",
    "databaseURL": "https://cloud-storage-35d72-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "projectId": "cloud-storage-35d72",
    "storageBucket": "cloud-storage-35d72.appspot.com",
    "messagingSenderId": "231799682675",
    "appId": "1:231799682675:web:2795932aac95d52f5adc06"
})

class CustomSession(MemorySession):
    def __init__(self, session_id=None):
        super().__init__()
        self.session_id = session_id or 'default_session'
        self.save_entities = True
        self.db_ref = db.reference(f'sessions/{self.session_id}')
        self._load_session()

    def _load_session(self):
        session_data = self.db_ref.get()
        if session_data:
            self._dc_id = session_data.get('dc_id')
            self._server_address = session_data.get('server_address')
            self._port = session_data.get('port')
            auth_key_data = session_data.get('auth_key')
            self._auth_key = AuthKey(data=base64.b64decode(auth_key_data)) if auth_key_data else None
            self._takeout_id = session_data.get('takeout_id')

    def clone(self, to_instance=None):
        cloned = super().clone(to_instance)
        cloned.save_entities = self.save_entities
        return cloned

    def set_dc(self, dc_id, server_address, port):
        super().set_dc(dc_id, server_address, port)
        self._update_session_table()

    @MemorySession.auth_key.setter
    def auth_key(self, value):
        self._auth_key = value
        self._update_session_table()

    @MemorySession.takeout_id.setter
    def takeout_id(self, value):
        self._takeout_id = value
        self._update_session_table()

    def _update_session_table(self):
        self.db_ref.set({
            'dc_id': self._dc_id,
            'server_address': self._server_address,
            'port': self._port,
            'auth_key': base64.b64encode(self._auth_key.key).decode('utf-8') if self._auth_key else None,
            'takeout_id': self._takeout_id
        })

    def get_update_state(self, entity_id):
        state_ref = self.db_ref.child('update_state').child(str(entity_id))
        state_data = state_ref.get()
        if state_data:
            date = datetime.datetime.fromtimestamp(state_data['date'], tz=datetime.timezone.utc)
            return types.updates.State(
                pts=state_data['pts'],
                qts=state_data['qts'],
                date=date,
                seq=state_data['seq'],
                unread_count=0
            )

    def set_update_state(self, entity_id, state):
        state_ref = self.db_ref.child('update_state').child(str(entity_id))
        state_ref.set({
            'pts': state.pts,
            'qts': state.qts,
            'date': state.date.timestamp(),
            'seq': state.seq
        })

    def get_update_states(self):
        states_ref = self.db_ref.child('update_state')
        states_data = states_ref.get()
        if states_data:
            return (
                (int(entity_id), types.updates.State(
                    pts=data['pts'],
                    qts=data['qts'],
                    date=datetime.datetime.fromtimestamp(data['date'], tz=datetime.timezone.utc),
                    seq=data['seq'],
                    unread_count=0
                )) for entity_id, data in states_data.items()
            )

    def save(self):
        pass  # Firebase operations are already saving data in real-time

    def close(self):
        pass  # No need to close anything for Firebase

    def delete(self):
        self.db_ref.delete()
        return True

    @classmethod
    def list_sessions(cls):
        sessions_ref = db.reference('sessions')
        return [key for key in sessions_ref.get().keys()]

    def process_entities(self, tlo):
        if not self.save_entities:
            return

        rows = self._entities_to_rows(tlo)
        if not rows:
            return

        entities_ref = self.db_ref.child('entities')
        now = int(time.time())
        for row in rows:
            entity_id = row[0]
            entities_ref.child(str(entity_id)).set({
                'id': row[0],
                'hash': row[1],
                'username': row[2],
                'phone': row[3],
                'name': row[4],
                'date': now
            })

    def get_entity_rows_by_phone(self, phone):
        entities_ref = self.db_ref.child('entities')
        entities_data = entities_ref.order_by_child('phone').equal_to(phone).get()
        for entity_id, data in entities_data.items():
            return data['id'], data['hash']

    def get_entity_rows_by_username(self, username):
        entities_ref = self.db_ref.child('entities')
        entities_data = entities_ref.order_by_child('username').equal_to(username).get()
        if entities_data:
            sorted_entities = sorted(entities_data.items(), key=lambda item: item[1].get('date', 0))
            for entity_id, data in sorted_entities[:-1]:
                entities_ref.child(entity_id).update({'username': None})
            last_entity = sorted_entities[-1]
            return last_entity[1]['id'], last_entity[1]['hash']

    def get_entity_rows_by_name(self, name):
        entities_ref = self.db_ref.child('entities')
        entities_data = entities_ref.order_by_child('name').equal_to(name).get()
        for entity_id, data in entities_data.items():
            return data['id'], data['hash']

    def get_entity_rows_by_id(self, id, exact=True):
        entities_ref = self.db_ref.child('entities')
        if exact:
            entity_data = entities_ref.child(str(id)).get()
            if entity_data:
                return entity_data['id'], entity_data['hash']
        else:
            ids = [utils.get_peer_id(PeerUser(id)), utils.get_peer_id(PeerChat(id)), utils.get_peer_id(PeerChannel(id))]
            for entity_id in ids:
                entity_data = entities_ref.child(str(entity_id)).get()
                if entity_data:
                    return entity_data['id'], entity_data['hash']

    def get_file(self, md5_digest, file_size, cls):
        files_ref = self.db_ref.child('sent_files')
        file_data = files_ref.order_by_child('md5_digest').equal_to(md5_digest).get()
        for file_id, data in file_data.items():
            if data['file_size'] == file_size and data['type'] == _SentFileType.from_type(cls).value:
                return cls(data['id'], data['hash'])

    def cache_file(self, md5_digest, file):
        files_ref = self.db_ref.child('sent_files')
        files_ref.push({
            'md5_digest': md5_digest,
            'file_size': file.size,
            'type': _SentFileType.from_type(type(file)).value,
            'id': file.id,
            'hash': file.hash
        })



