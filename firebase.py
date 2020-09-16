import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from config import FIREBASE
from datetime import datetime

# Use the application default credentials
if FIREBASE:
    cred = credentials.Certificate(FIREBASE)
    firebase_admin.initialize_app(cred)

    db = firestore.client()


def saveProfitSnapshot(realized, unrealized):
    if FIREBASE:
        doc_ref = db.collection(u'fx_profits').add({
            'time': datetime.utcnow(),
            'realized': realized,
            'unrealized': unrealized
        })
