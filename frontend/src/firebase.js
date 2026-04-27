import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey:            'AIzaSyBhy8M_ZlNzglaCbKUZ3mfR5sWqbChDUZM',
  authDomain:        'launchpad-93064.firebaseapp.com',
  projectId:         'launchpad-93064',
  storageBucket:     'launchpad-93064.firebasestorage.app',
  messagingSenderId: '593299409514',
  appId:             '1:593299409514:web:b9f63a8a85ab6be8d71813',
};

const app = initializeApp(firebaseConfig);
export const auth     = getAuth(app);
export const provider = new GoogleAuthProvider();
