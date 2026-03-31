import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart' show kIsWeb;

/// Firebase configuration for kjtcom-c78cd.
/// PLACEHOLDER - regenerate with: flutterfire configure --project=kjtcom-c78cd
class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) return web;
    throw UnsupportedError('Only web platform is supported.');
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyCBw0VLhPbQ-h5mCONdQyGz9WFedxRvJas',
    appId: '1:703812044891:web:84b2df9330066bfbe6177e',
    messagingSenderId: '703812044891',
    projectId: 'kjtcom-c78cd',
    authDomain: 'kjtcom-c78cd.firebaseapp.com',
    storageBucket: 'kjtcom-c78cd.firebasestorage.app',
    measurementId: 'G-JMVEJLW9PC',
  );

}